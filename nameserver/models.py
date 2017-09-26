import dns.query
import dns.update
import dns.rdatatype
import random
import string


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

  def query(self, name, rtype=dns.rdatatype.A):
    qname = dns.name.from_text("%s.%s" % (name, self.name))
    q = dns.message.make_query(qname, rtype)
    r = dns.query.udp(q, self.server.address)
    try:
      data = []
      ns_rrset = r.find_rrset(r.answer, qname, dns.rdataclass.IN, rtype)
      for rr in ns_rrset:
        data.append(rr)
      return data
    except:
      return None

  def deleteDomain(self, name):
    update = dns.update.Update(self.name)
    update.delete(name)
    dns.query.tcp(update, self.server.address)

  def configureA(self, name, address):
    qname = dns.name.from_text("%s.%s" % (name, self.name))
    response = self.query(name)

    try:
      # If a response is received, and it is correct, return true.
      if(response[0].address == address):
        return True
      # If it is wrong, delete it.
      else:
        update = dns.update.Update(self.name)
        update.delete(name)
        dns.query.tcp(update, self.server.address)
    except (TypeError, IndexError):
      pass

    # Create the new record
    update = dns.update.Update(self.name)
    update.add(name, 300, 'a', address)
    dns.query.tcp(update, self.server.address)
    return True

  def testConnection(self):
    dnsName = ''.join(random.choice(string.ascii_lowercase) for i in range(20))
    try:
      update = dns.update.Update(self.name)
      update.add(dnsName, 300, 'a', '127.0.0.1')
      response = dns.query.tcp(update, self.server.address)
      update.delete(dnsName)
      response = dns.query.tcp(update, self.server.address)
      return True
    except:
      return False

  class Meta:
    ordering = ['name']

class StaticRecord(models.Model):
  name = models.CharField(max_length=200)
  domain = models.ForeignKey(Domain)
  ipv4 = models.GenericIPAddressField(protocol='IPv4', null=True)
  ipv6 = models.GenericIPAddressField(protocol='IPv6', null=True)
  active = models.BooleanField(default=True)

  def __str__(self):
    if(self.ipv4 and self.ipv6):
      return "%s.%s - %s %s" % (self.name, self.domain.name, 
          self.ipv4, self.ipv6)
    elif(self.ipv4):
      return "%s.%s - %s" % (self.name, self.domain.name, self.ipv4)
    elif(self.ipv6):
      return "%s.%s - %s" % (self.name, self.domain.name, self.ipv6)
    else:
      return "%s.%s - NO ADDRESSES CONFIGURED" % (self.name, self.domain.name)

  def configure(self):
    if(self.ipv4):
      self.domain.configureA(self.name, self.ipv4)

  def deactivate(self):
    self.active = False
    self.domain.deleteDomain(self.name)
    self.save()

  class Meta:
    ordering = ['domain','name']
