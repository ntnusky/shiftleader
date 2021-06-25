import dns.query
import dns.name
import dns.update
import dns.resolver
import dns.rdatatype
import dns.rdtypes.ANY.PTR
import dns.rdtypes.IN.A
import dns.rdtypes.IN.AAAA
import dns.tsigkeyring
import dns.zone
import ipaddress
import logging
import random
import string

from django.db import models, transaction
from django.db.models.signals import pre_delete
from django.db.utils import IntegrityError
from django.dispatch import receiver
from django.utils import timezone

logger = logging.getLogger(__name__)

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

  def configureRecord(self, domain, record, destination, rtype = None, present=True, ttl=300):
    if(not rtype):
      rtype = Server.detectRecordType(destination, domain)
      logger.debug('Detected record-type: %s' % rtype)

    # Make sure destination is a fqdn
    if((rtype == 'cname') and not destination.endswith('.')):
      destination = "%s." % destination
    if((rtype == 'ptr') and not destination.endswith('.')):
      destination = "%s." % destination

    if(present):
      logger.debug('NSUPDATE-ADD: Domain: %s Record: %s - TTL: %d - Type: %s - Dest: %s' % (
                                domain, record, ttl, rtype, destination))
      update = self.createConnection(domain)
      update.add(record, ttl, rtype, destination)
      dns.query.tcp(update, self.address)
    else:
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

  def zonetransfer(self, domain):
    if(self.key):
      keyring = dns.tsigkeyring.from_text({ self.keyname : self.key })
      algorithm = dns.name.from_text(self.algorithm)
      z = dns.zone.from_xfr(dns.query.xfr(self.address, domain, keyring=keyring, 
          keyname=self.keyname, keyalgorithm=algorithm))
    else:
      z = dns.zone.from_xfr(dns.query.xfr(self.address, domain)) 

    return z.nodes

class Domain(models.Model):
  name = models.CharField(max_length=200)
  alias = models.CharField(max_length=200, null=True, default=None)
  server = models.ForeignKey(Server, on_delete=models.PROTECT)

  def __str__(self):
    return "%s" % self.name

  def toJSON(self):
    if(self.name.endswith('in-addr.arpa')):
      t = 'reverse'
    else:
      t = 'forward'

    return {
      'id': self.id,
      'name': self.name,
      'alias': self.getName(),
      'type': t,
    }

  def configure(self, record, destination, rtype=None, present=True, ttl=300):
    self.server.configureRecord(self.getName(), record, destination, 
                                    rtype=rtype, present=present, ttl=ttl)

  def deleteDomain(self, name):
    self.server.clearName(self.getName(), name)

  def getName(self):
    if(self.alias):
      return self.alias
    else:
      return self.name

  def testConnection(self):
    return self.server.testConnection(self.getName())

  def zonetransfer(self):
    nodes = self.server.zonetransfer(self.getName()) 
    records = {}

    for node in nodes.keys():
      for dataset in nodes[node].rdatasets:
        for record in dataset.items:
          if(type(record) == dns.rdtypes.ANY.PTR.PTR):
            try:
              records['%s.%s' % (node, self.getName())].append(str(record.target))
            except KeyError:
              records['%s.%s' % (node, self.getName())] = [str(record.target)]
          if(type(record) == dns.rdtypes.IN.A.A or
              type(record) == dns.rdtypes.IN.AAAA.AAAA):
            try:
              records['%s.%s' % (node, self.getName())].append(str(record.address))
            except KeyError:
              records['%s.%s' % (node, self.getName())] = [str(record.address)]
    return records

  class Meta:
    ordering = ['name']

class Record(models.Model):
  TYPE_MANUAL = 0
  TYPE_AUTO = 1
  TYPE_HOST = 2

  RECORDTYPES = (
    (TYPE_MANUAL, 'Manual'),
    (TYPE_AUTO, 'Automatic'),
    (TYPE_HOST, 'Host'),
  )

  name = models.CharField(max_length=200)
  domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
  active = models.BooleanField(default=True)
  record_type = models.IntegerField(choices=RECORDTYPES)

  def __str__(self):
    return self.getName()

  def activate(self):
    self.active = True
    self.configure()
    self.save()

  def configure(self):
    raise NotImplementedError()

  def deactivate(self):
    self.active = False
    self.domain.deleteDomain(self.name)
    self.save()

  def getName(self):
    if(len(self.name) > 0):
      return "%s.%s" % (self.name, self.domain.name)
    else:
      return self.domain.name

  def getRecordTypeName(self):
    for rt in self.RECORDTYPES:
      if(rt[0] == self.record_type):
        return rt[1]
    raise TypeError('Could not find record type')

  def toJSON(self):
    return {
      'active': self.active,
      'domain': self.domain.name,
      'host': self.name,
      'id': self.id,
      'name': '%s.%s' % (self.name, self.domain.name),
      'type': self.record_type,
      'typename': self.getRecordTypeName(),
    }

  class Meta:
    abstract = True
    ordering = ['name']
    unique_together = (
      ('name', 'domain'),
    )

class Forward(Record):
  ipv4 = models.GenericIPAddressField(protocol='IPv4', null=True)
  ipv6 = models.GenericIPAddressField(protocol='IPv6', null=True)
  reverse = models.BooleanField()

  def configure(self):
    if(not self.active):
      self.deactivate()
      return

    self.domain.deleteDomain(self.name)
    if(self.ipv4):
      logger.debug('Configuring A-record for %s.%s to %s' % (
                          self.name, self.domain.name, self.ipv4))
      self.domain.configure(self.name, self.ipv4)

      if(self.reverse):
        v4 = ipaddress.IPv4Address(self.ipv4)
        host = v4.reverse_pointer.split('.')[0]
        reverseDomain = '.'.join(v4.reverse_pointer.split('.')[1:])
        try:
          domain = Domain.objects.get(name=reverseDomain)
          logger.debug('Confiuring PTR-record %s.%s for %s.%s' % (
                                  host, reverseDomain, self.name, self.domain))
          reverse, created = Reverse.objects.get_or_create(
                                  name=host, domain=domain,
                                  record_type=Record.TYPE_AUTO, active=True,
                                  target = '%s.%s' % (self.name, self.domain))
          reverse.configure()
        except Domain.DoesNotExist:
          logger.debug('Could not find reverse-domain %s' % reverseDomain)
        except IntegrityError:
          logger.warning('Reverse-record already exists %s' % reverseDomain)

    if(self.ipv6):
      logger.debug('Configuring AAAA-record for %s.%s to %s' % (
                          self.name, self.domain.name, self.ipv6))
      self.domain.configure(self.name, self.ipv6)

      if(self.reverse):
        try:
          v6 = ipaddress.IPv6Address(self.ipv6)
        except:
          logger.warning("Could not parse %s as an IPv6 address" % self.ipv6)
          return

        try:
          domain = Domain.objects.get(name=v6.reverse_pointer[32:])
          logger.debug('Confiuring PTR-record %s.%s for %s.%s' % (
                                  v6.reverse_pointer[0:31],
                                  v6.reverse_pointer[32:], 
                                  reverseDomain, self.name, self.domain))
          reverse, created = Reverse.objects.get_or_create(
                            name=v6.reverse_pointer[0:31], domain=domain,
                            record_type=Record.TYPE_AUTO, active=True,
                            target = '%s.%s' % (self.name, self.domain))
          reverse.configure()
        except Domain.DoesNotExist:
          logger.debug('Could not find reverse-domain %s' %
                                  v6.reverse_pointer[32:])
        except IntegrityError:
          logger.warning('Reverse-record already exists %s' % reverseDomain)

  def activate(self):
    super().activate()
    for r in self.getReverse():
      r.activate()

  def deactivate(self):
    super().deactivate()
    for r in self.getReverse():
      r.deactivate()

  def getReverse(self):
    return Reverse.objects.filter(
              target = '%s.%s' % (self.name, self.domain)).all()

  def toJSON(self):
    data = super().toJSON()

    data['reverse'] = self.reverse
    data['recordtype'] = 'Forward'
    if(self.ipv4):
      data['ipv4'] = self.ipv4
    if(self.ipv6):
      data['ipv6'] = self.ipv6

    return data

@receiver(pre_delete, sender=Forward)
def delete_reverse(sender, instance, **kwargs):
  instance.deactivate()
  for r in instance.getReverse():
    r.delete()

class CName(Record):
  target = models.CharField(max_length=200)

  def configure(self):
    logger.debug('Configuring CNAME for %s.%s to %s' % (
                          self.name, self.domain.name, self.target))
    self.domain.configure(self.name, self.target, rtype='cname')

  def toJSON(self):
    data = super().toJSON()
    data['recordtype'] = 'CNAME'
    data['target'] = self.target
    return data

@receiver(pre_delete, sender=CName)
def deactivate_before_delete(sender, instance, **kwargs):
  instance.deactivate()

class Reverse(Record):
  target = models.CharField(max_length=200)

  def configure(self):
    logger.debug('Configuring PTR for %s.%s to %s' % (
                          self.name, self.domain.name, self.target))
    self.domain.configure(self.name, self.target, rtype='ptr')

  def toJSON(self):
    data = super().toJSON()
    data['recordtype'] = 'PTR'
    data['target'] = self.target
    return data

@receiver(pre_delete, sender=Reverse)
def deactivate_before_delete(sender, instance, **kwargs):
  instance.deactivate()

class StaticRecord(models.Model):
  name = models.CharField(max_length=200)
  domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
  ipv4 = models.GenericIPAddressField(protocol='IPv4', null=True)
  ipv6 = models.GenericIPAddressField(protocol='IPv6', null=True)
  expire = models.DateField(default=None, null=True)
  active = models.BooleanField(default=True)

  def __str__(self):
    if(self.ipv4 and self.ipv6):
      return "%s - %s %s" % (self.getName(), self.ipv4, self.ipv6)
    elif(self.ipv4):
      return "%s - %s" % (self.getName(), self.ipv4)
    elif(self.ipv6):
      return "%s - %s" % (self.getName(), self.ipv6)
    else:
      return "%s - NO ADDRESSES CONFIGURED" % (self.getName())

  def getName(self):
    if(len(self.name) > 0):
      return "%s.%s" % (self.name, self.domain.name)
    else:
      return self.domain.name
  
  def getExpireDateText(self):
    if(self.expire):
      return "%s.%s.%s" % (self.expire.day, self.expire.month, self.expire.year)
    else:
      return ""

  def isExpired(self):
    if(self.expire):
      expired = (self.expire < timezone.now().date())
      if(expired and self.active):
        self.deactivate()
      return expired
    else:
      return False

  def isActive(self):
    return not self.isExpired() and self.active

  def configure(self):
    if(not self.isActive()):
      self.deactivate()
      return

    self.domain.deleteDomain(self.name)
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

    if(self.ipv6):
      self.domain.configure(self.name, self.ipv6)

  def activate(self):
    self.active = True
    self.configure()
    self.save()

  def deactivate(self):
    self.active = False
    self.domain.deleteDomain(self.name)
    self.save()

  class Meta:
    ordering = ['domain','name']
