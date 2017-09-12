import ipaddress
from django.db import models

class Subnet(models.Model):
  name = models.CharField(max_length=64)
  active = models.BooleanField()
  prefix = models.GenericIPAddressField()
  mask = models.IntegerField()
  free = models.IntegerField(default = -1)

  def __str__(self):
    return "%s - %s/%d%s" % (self.name, self.prefix, self.mask, 
        "" if self.active else " - INACTIVE")

  def getSubnet(self):
    return ipaddress.ip_network("%s/%s" % (self.prefix, self.mask))

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

  class Meta:
    ordering = ['-active', 'name']

class Lease(models.Model):
  IP = models.GenericIPAddressField()
  MAC = models.CharField(max_length=18)
  subnet = models.ForeignKey(Subnet)

  def __str__(self):
    return "%s, %s" % (self.IP, self.MAC)

  class Meta:
    ordering = ['IP', 'MAC']
