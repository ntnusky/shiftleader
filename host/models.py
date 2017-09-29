import string
from random import sample, choice

from django.db import models

from dhcp.models import Lease
from dhcp.omapi import Servers
from nameserver.models import Domain
from puppet.models import Environment, Role

class Host(models.Model):
  STATUSES = (
    (0, "Operational"),
    (1, "Provisioning"),
    (2, "Installing"),
    (3, "Puppet-Sign"),
    (4, "Puppet-run"),
  )

  OPERATIONAL = 0
  PROVISIONING = 1
  INSTALLING = 2
  PUPPETSIGN = 3
  PUPPETRUN = 4

  name = models.CharField(max_length=64)
  password = models.CharField(max_length=64, null=True)
  domain = models.ForeignKey(Domain)
  environment = models.ForeignKey(Environment)
  role = models.ForeignKey(Role, null=True)
  status = models.CharField(max_length=1, choices=STATUSES)

  def __str__(self):
    return "%s.%s" % (self.name, self.domain.name)

  def getStatusText(self):
    for s in self.STATUSES:
      if s[0] == int(self.status):
        return s[1]
    return "N/A"

  def deleteDNS(self):
    for interface in self.interface_set.all():
      # If this is the primary interface, delete the A record with the machine's
      # hostname.
      if(interface.primary):
        try:
          self.domain.deleteDomain(self.name)
        except AttributeError:
          pass

      # Delete the interface-specific A record
      try:
        self.domain.deleteDomain("%s.%s" % (interface.name, self.name))
      except AttributeError:
        pass

  def updateDNS(self):
    for interface in self.interface_set.all():
      # If this is the primary interface, add an A record with the machine's
      # hostname.
      if(interface.primary):
        if(interface.ipv4Lease):
          self.domain.configure(self.name, interface.ipv4Lease.IP)
        if(interface.ipv6):
          self.domain.configure(self.name, interface.ipv6)

      ifname = "%s.%s" % (interface.name, self.name)
      if(interface.ipv4Lease):
        self.domain.configure(ifname, interface.ipv4Lease.IP)
      if(interface.ipv6):
        self.domain.configure(ifname, interface.ipv6)

  def generatePassword(self):
    chars = string.ascii_letters + string.digits
    self.password = ''.join(choice(chars) for _ in range(16))
    self.save()

  def remove(self):
    self.deleteDNS()
    dhcp = Servers()
    for interface in self.interface_set.all():
      dhcp.configureLease(interface.ipv4Lease.IP, interface.ipv4Lease.MAC,
          present = False)
      lease = interface.ipv4Lease
      lease.present = False
      lease.lease = False
      lease.save()
      lease.subnet.free += 1
      lease.subnet.save()
      interface.delete()
    self.delete()

  class Meta:
    ordering = ['domain', 'name']

class Interface(models.Model):
  ifname = models.CharField(max_length=20)
  name = models.CharField(max_length=64)
  mac = models.CharField(max_length=64)
  host = models.ForeignKey(Host)
  primary = models.BooleanField(default=False)
  ipv4Lease = models.OneToOneField(Lease, null=True)
  ipv6 = models.GenericIPAddressField(protocol='IPv6', null=True)

  def __str__(self):
    return "%s on %s" % (self.name, self.host)
