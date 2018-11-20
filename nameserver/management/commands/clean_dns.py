from django.core.management.base import BaseCommand

from host.models import Interface
from nameserver.models import Domain, StaticRecord

class Command(BaseCommand):
  help = ""

  def add_arguments(self, parser):                                               
    parser.add_argument(                                                         
      '--delete',                                                                
      dest='delete',                                                             
      action='store_true',                                                       
      help='Delete names which are not in shiftleader from DNS',                                   
    )

  def handle(self, *args, **options):
    indns = {}
    insl = {}

    for domain in Domain.objects.all():
      indns.update(domain.zonetransfer())
    
    for interface in Interface.objects.all():
      domain = '%s.%s' % (interface.host.name, interface.network.domain.name)

      try:
        insl[domain].append(interface.ipv4Lease.IP)
      except:
        insl[domain] = [interface.ipv4Lease.IP]
      
      if(interface.ipv6):
        insl[domain].append(interface.ipv6)
      
      ip = interface.ipv4Lease.IP.split('.')
      try:
        reverseDomain = "%s.%s.%s.in-addr.arpa" % (ip[2], ip[1], ip[0])
        d = Domain.objects.get(name=reverseDomain)
        try:
          insl['%s.%s' % (ip[3], reverseDomain)].append('%s.' % domain)
        except KeyError:
          insl['%s.%s' % (ip[3], reverseDomain)] = ['%s.' % domain]
      except Domain.DoesNotExist:
        pass

    for sr in StaticRecord.objects.all():
      if(len(sr.name)):
        domain = '%s.%s' % (sr.name, sr.domain)
      else:
        domain = '@.%s' % sr.domain

      if(sr.ipv4):
        try:
          insl[domain].append(sr.ipv4)
        except:
          insl[domain] = [sr.ipv4]

        try:
          ip = sr.ipv4.split('.')
          reverseDomain = "%s.%s.%s.in-addr.arpa" % (ip[2], ip[1], ip[0])
          d = Domain.objects.get(name=reverseDomain)
          try:
            insl['%s.%s' % (ip[3], reverseDomain)].append('%s.' % domain)
          except KeyError:
            insl['%s.%s' % (ip[3], reverseDomain)] = ['%s.' % domain]
        except Domain.DoesNotExist:
          pass

      if(sr.ipv6):
        try:
          insl[domain].append(sr.ipv6)
        except:
          insl[domain] = [sr.ipv6]
    
    for name in indns:
      for record in indns[name]:
        try:
          if record in insl[name]:
            continue
        except KeyError:
          pass

        self.stdout.write("%s->%s is not in shiftleader" % (name, record)) 
        if(options['delete']):
          domainname = '.'.join(name.split('.')[1:])
          hostname = name.split('.')[0]
          domain = Domain.objects.get(name=domainname)

          self.stdout.write(" - Deleting '%s' from the zone '%s'" % (hostname, 
              domainname))
          domain.deleteDomain(hostname)
          if(name in insl):
            self.stdout.write(" - Need to re-add records which should be " + \
              i  "in place with the deleted name")

            for r in insl[name]:
              self.stdout.write(" --- Adding '%s' -> '%s'" % (name, r))
              domain.configure(name.split('.')[0], r)
        else:
          self.stderr.write(
            "Add --delete to your command to actually delete it from DNS")
