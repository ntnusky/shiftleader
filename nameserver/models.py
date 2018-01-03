import dns.query
import dns.name
import dns.update
import dns.rdatatype
import dns.tsigkeyring
import ipaddress
import random
import string

from django.db import models

class Server(models.Model):
  name = models.CharField(max_length=64)
  address = models.GenericIPAddressField()
  key = models.CharField(max_length=200, null=True)
  keyname = models.CharField(max_length=200, default='update')
  algorithm = models.CharField(max_length=28,
      default="HMAC-MD5.SIG-ALG.REG.INT")

  def __str__(self):
    return "%s (%s)" % (self.name, self.address)

  def createConnection(self, domain):
    if(self.key):
      keyring = dns.tsigkeyring.from_text({ self.keyname : self.key })
      algorithm = dns.name.from_text(self.algorithm)
      return dns.update.Update(domain, keyring=keyring, keyname=self.keyname,
          keyalgorithm=algorithm)
    else:
      return dns.update.Update(domain)

  def detectRecordType(name, domain=None):
    try:
      ip = ipaddress.ip_address(name)
    except ValueError:
      if(domain and ("ip6.arpa" in domain or "in-addr.arpa" in domain)):
        return 'ptr'
      else:
        return 'cname'
    else:
      if ip.version == 4:
        return 'a'
      elif ip.version == 6:
        return 'aaaa'
      else:
        raise ValueError

  def query(self, domain, rdtype):
    qname = dns.name.from_text(domain)
    rtype = dns.rdatatype.from_text(rdtype)

    q = dns.message.make_query(qname, rtype)
    r = dns.query.udp(q, self.address)
    try:
      data = []
      ns_rrset = r.find_rrset(r.answer, qname, dns.rdataclass.IN, rtype)
      for rr in ns_rrset:
        data.append(rr.to_text())
      return data
    except:
      return None

  def configureRecord(self, domain, record, destination, exclusive=True, present=True, ttl=300):
    rtype = Server.detectRecordType(destination, domain)

    # Make sure destination is a fqdn
    if((rtype == 'cname') and not destination.endswith('.')):
      destination = "%s.%s." % (destination, domain)
    if((rtype == 'ptr') and not destination.endswith('.')):
      destination = "%s." % destination

    # Query for existing records
    existing = self.query("%s.%s" % (record, domain), rtype)

    # If there exists destination which should not be there; remove them
    if(exclusive and existing and 
          (destination not in existing or len(existing) > 1)):
      try:
        existing.remove(destination)
      except ValueError: # If destination is not in existing
        pass

      for dest in existing:
        update = self.createConnection(domain)
        update.delete(record, rtype, dest)
        dns.query.tcp(update, self.address)

    # If the record should be present, but is not; create it:
    if(present and (not existing or destination not in existing)):
      update = self.createConnection(domain)
      update.add(record, ttl, rtype, destination)
      dns.query.tcp(update, self.address)

    # It the record is present, but should not be: remove it
    if(not present and existing and destination in existing):
      update = self.createConnection(domain)
      update.delete(record, rtype, destination)
      dns.query.tcp(update, self.address)
  
  def clearName(self, domain, name):
    update = self.createConnection(domain)
    update.delete(name)
    dns.query.tcp(update, self.address)

  def testConnection(self, domain):
    dnsName = ''.join(random.choice(string.ascii_lowercase) for i in range(20))
    try:
      update = self.createConnection(domain)
      update.add(dnsName, 300, 'a', '127.0.0.1')
      response = dns.query.tcp(update, self.address)
      update.delete(dnsName)
      response = dns.query.tcp(update, self.address)
      return True
    except Exception as e:
      return False

class Domain(models.Model):
  name = models.CharField(max_length=200)
  server = models.ForeignKey(Server)

  def __str__(self):
    return "%s" % self.name

  def deleteDomain(self, name):
    self.server.clearName(self.name, name)

  def configure(self, record, destination, exclusive=True, present=True, ttl=300):
    self.server.configureRecord(self.name, record, destination, exclusive,
        present, ttl)

  def testConnection(self):
    return self.server.testConnection(self.name)

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
      self.domain.configure(self.name, self.ipv4)

      # If we manage the reverse-zone, configure a reverse name for this
      # interface.
      ip = self.ipv4.split('.')
      try:
        reverseDomain = "%s.%s.%s.in-addr.arpa" % (ip[2], ip[1], ip[0])
        domain = Domain.objects.get(name=reverseDomain)
        domain.configure(ip[3], "%s.%s." % (self.name, self.domain))
      except Domain.DoesNotExist:
        pass
    else:
      self.domain.configure(self.name, "198.51.100.218", present=False)

    if(self.ipv6):
      self.domain.configure(self.name, self.ipv6)
    else:
      self.domain.configure(self.name, "2001:db8::1", present=False)

  def deactivate(self):
    self.active = False
    self.domain.deleteDomain(self.name)
    self.save()

  class Meta:
    ordering = ['domain','name']
