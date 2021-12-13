from django.core.management.base import BaseCommand

from host.models import Interface
from nameserver.models import Domain, StaticRecord, Forward, CName, Reverse

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

    # Retrieve domains from DNS
    for domain in Domain.objects.all():
      indns.update(domain.zonetransfer())
    
    # Collect all names which should be present in DNS because they are
    # associated with interfaces.
    for interface in Interface.objects.all():
      domain = '%s.%s' % (interface.host.name, interface.network.domain.name)

      try:
        insl[domain].append(interface.ipv4Lease.IP)
      except:
        insl[domain] = [interface.ipv4Lease.IP]
      
      if(interface.ipv6):
        insl[domain].append(interface.ipv6)
      
      ip = interface.ipv4Lease.IP.split('.')
      # If we manage the reverse-domain for the assigned IP, add the PTR record
      # as well.
      try:
        reverseDomain = "%s.%s.%s.in-addr.arpa" % (ip[2], ip[1], ip[0])
        d = Domain.objects.get(name=reverseDomain)
        try:
          insl['%s.%s' % (ip[3], reverseDomain)].append('%s.' % domain)
        except KeyError:
          insl['%s.%s' % (ip[3], reverseDomain)] = ['%s.' % domain]
      except Domain.DoesNotExist:
        pass

    for f in Forward.objects.filter(active=True).all():
      if(len(f.name)):
        domain = '%s.%s' % (f.name, f.domain.name)
      else:
        domain = '@.%s' % f.domain.name

      if(f.ipv4):
        try:
          insl[domain].append(f.ipv4)
        except:
          insl[domain] = [f.ipv4]
      if(f.ipv6):
        try:
          insl[domain].append(f.ipv6)
        except:
          insl[domain] = [f.ipv6]
    
    for r in Reverse.objects.filter(active=True).all():
      try:
        insl['%s.%s' % (r.name, r.domain.name)].append('%s.' % r.target)
      except KeyError:
        insl['%s.%s' % (r.name, r.domain.name)] = ['%s.' % r.target]

    # For each name found in DNS:
    for name in indns:
      for record in indns[name]:
        # If the record is in shiftleader, just skip to the next record.
        try:
          if record in insl[name]:
            continue
        except KeyError:
          pass

        # If the record is not in shiftleader, delete it, or notify the user if
        # he has not requested removal.
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
                "in place with the deleted name")

            for r in insl[name]:
              self.stdout.write(" --- Adding '%s' -> '%s'" % (name, r))
              domain.configure(name.split('.')[0], r)
        else:
          self.stderr.write(
            "Add --delete to your command to actually delete it from DNS")
