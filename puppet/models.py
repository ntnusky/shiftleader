from django.db import models

class Environment(models.Model):
  name = models.CharField(max_length=64)
  active = models.BooleanField()

  def __str__(self):
    return "%s (%s)" % (self.name, "Active" if self.active else "In-Active")

  class Meta:
    ordering = ['-active', 'name']

class Role(models.Model):
  name = models.CharField(max_length=64)
  environment = models.ForeignKey(Environment)
  active = models.BooleanField()

  def __str__(self):
    return "%s in %s (%s)" % (self.name, self.environment.name, 
        "Active" if self.active else "In-Active")

  class Meta:
    ordering = ['-active', 'name']
