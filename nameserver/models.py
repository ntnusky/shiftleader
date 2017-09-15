import dns.query
import dns.update

from django.db import models

class Server(models.Model):
  name = models.CharField(max_length=64)
  address = models.GenericIPAddressField()
  key = models.CharField(max_length=200, null=True)

  def __str__(self):
    return "%s (%s)" % (self.name, self.address)

class Domain(models.Model):
  name = models.CharField(max_length=200)
  server = models.ForeignKey(Server)

  def __str__(self):
    return "%s" % self.name

  def testConnection(self):
    try:
      update = dns.update.Update(self.name)
      update.add('dnstesting', 300, 'a', '127.0.0.1')
      response = dns.query.tcp(update, self.server.address)
      update.delete('dnstesting')
      response = dns.query.tcp(update, self.server.address)
      return True
    except:
      return False

  class Meta:
    ordering = ['name']
