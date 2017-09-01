from django.db import models

class APIToken(models.Model):
  name = models.CharField(max_length=200)
  token = models.CharField(max_length=200)

  def __str__(self):
    return "%s (%s)" % (self.name, self.token)
