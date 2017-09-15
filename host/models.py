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
