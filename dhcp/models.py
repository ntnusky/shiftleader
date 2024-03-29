import ipaddress
from configparser import NoOptionError

from django.db import models

from dashboard.settings import parser
from nameserver.models import Domain

class Subnet(models.Model):
  name = models.CharField(max_length=64)
  active = models.BooleanField()
  domain = models.ForeignKey(Domain, null=True, on_delete=models.PROTECT)
  prefix = models.GenericIPAddressField()
  mask = models.IntegerField()
  free = models.IntegerField(default = -1)
  ipversion = models.IntegerField(default = 4)

  def __str__(self):
    return "%s - %s/%d%s" % (self.name, self.prefix, self.mask, 
        "" if self.active else " - INACTIVE")

  def getSubnet(self):
    return ipaddress.ip_network("%s/%s" % (self.prefix, self.mask))

  def getReservedAddresses(self):
    # Reserve net-ID and broadcast-address
    subnet = self.getSubnet()
    reservedAddresses = [subnet[0], subnet[-1]]

    # Reserve the gateway-IP if it exists
    try:
      gateway = parser.get("DHCP", "%sGateway" % self.name)
      reservedAddresses.append(ipaddress.ip_address(gateway))
    except:
      pass

    # Iterate through reserved ranges and add the address to the reserved list.
    try:
      reserved = parser.get("DHCP", "%sReserved" % self.name)
      for address in reserved.split(','):
        if(len(address) == 0):
          continue
        elif('-' in address):
          first = ipaddress.ip_address(address.split('-')[0])
          last = ipaddress.ip_address(address.split('-')[1])
          for ip in range(int(first), int(last)+1):
            reservedAddresses.append(ipaddress.ip_address(ip))
        else:
          reservedAddresses.append(ipaddress.ip_address(address))
    except NoOptionError:
      pass

    # Retrun the list of addresses; with duplicates removed.
    return list(dict.fromkeys(reservedAddresses))

  def getIPVersion(self):
    subnet = self.getSubnet()

    if(type(subnet) == ipaddress.IPv4Network):
      return 4
    elif(type(subnet) == ipaddress.IPv6Network):
      return 6
    else:
      return 0

  def setSubnet(self, newPrefix, newSubnetMask):
    try:
      subnet = ipaddress.ip_network("%s/%s" % (newPrefix, newSubnetMask))
    except ValueError:
      return False

    toSave = False
    if(self.prefix != str(subnet.network_address)):
      self.prefix = str(subnet.network_address)
      toSave = True
    if(self.mask != subnet.prefixlen):
      self.mask = subnet.prefixlen
      toSave = True

    if(toSave):
      self.save()
    return toSave

  def checkFree(self, ip):
    try:
      lease = Lease.objects.get(subnet = self, present = True, IP=ip)
      return False
    except Lease.DoesNotExist:
      return True
  
  def getLease(self, ip):
    try:
      lease = Lease.objects.get(subnet = self, present = True, IP=ip)
      return lease
    except Lease.DoesNotExist:
      return None

  def createLease(self, mac, ip=None):
    subnet = self.getSubnet()
    reserved = self.getReservedAddresses()
    if ip:
      host = ipaddress.ip_address(ip)
      if self.checkFree(str(host)):
        lease = Lease(IP=str(host), MAC=mac, subnet=self)
        self.free -= 1
        self.save()
        lease.save()
        return lease
    else:
      for host in subnet.hosts():
        if host in reserved:
          continue
        if self.checkFree(str(host)):
          lease = Lease(IP=str(host), MAC=mac, subnet=self)
          self.free -= 1
          self.save()
          lease.save()
          return lease
    return None

  class Meta:
    ordering = ['-active', 'name']

class Lease(models.Model):
  IP = models.GenericIPAddressField()
  MAC = models.CharField(max_length=18)
  subnet = models.ForeignKey(Subnet, on_delete=models.PROTECT)
  present = models.BooleanField(default=True)
  lease = models.BooleanField(default=False)

  def __str__(self):
    try:
      interface = self.interface
    except:
      return "%s->%s" % (self.IP, self.MAC)
    else:
      return "%s->%s, assigned to %s" % (self.IP, self.MAC, interface)

  class Meta:
    ordering = ['IP', 'MAC']
