from django.db import models

class Subnet(models.Model):
  name = models.CharField(max_length=64)
  active = models.BooleanField()
  prefix = models.GenericIPAddressField()
  mask = models.IntegerField()

  def __str__(self):
    return "%s - %s/%d%s" % (self.name, self.prefix, self.mask, 
        "" if self.active else " - INACTIVE")

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
