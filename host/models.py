from django.db import models

from dhcp.models import Lease
from nameserver.models import Domain
from puppet.models import Environment

class Host(models.Model):
  STATUSES = (
    (0, "Operational"),
    (1, "Provisioning"),
    (2, "Installing"),
  )

  OPERATIONAL = 0
  PROVISIONING = 1
  INSTALLING = 2

  name = models.CharField(max_length=64)
  domain = models.ForeignKey(Domain)
  environment = models.ForeignKey(Environment)
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
        interface.domain.deleteDomain("%s.%s" % (interface.name, self.name))
      except AttributeError:
        pass

  def updateDNS(self):
    for interface in self.interface_set.all():
      # If this is the primary interface, add an A record with the machine's
      # hostname.
      if(interface.primary):
        try:
          self.domain.configureA(self.name, interface.ipv4Lease.IP)
        except AttributeError:
          pass

      # Add DNS record for each interface
      try:
        interface.domain.configureA("%s.%s" % (interface.name, self.name), 
            interface.ipv4Lease.IP)
      except AttributeError:
        pass

  class Meta:
    ordering = ['domain', 'name']

class Interface(models.Model):
  ifname = models.CharField(max_length=20)
  name = models.CharField(max_length=64)
  mac = models.CharField(max_length=64)
  domain = models.ForeignKey(Domain)
  host = models.ForeignKey(Host)
  primary = models.BooleanField(default=False)
  ipv4Lease = models.OneToOneField(Lease, null=True)
  ipv6 = models.GenericIPAddressField(protocol='IPv6', null=True)

  def __str__(self):
    return "%s on %s" % (self.name, self.host)
