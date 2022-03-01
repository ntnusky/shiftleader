import ipaddress
import django.db.utils

from django.core.management.base import BaseCommand

from host.models import Interface
from nameserver.models import Domain, Record, StaticRecord, Forward, CName, Reverse

class Command(BaseCommand):
  help = "Register a DNS static record"

  def add_arguments(self, parser):                                               
    parser.add_argument('--name', type=str, required=True)
    parser.add_argument('--ipv4', type=str)
    parser.add_argument('--ipv6', type=str)
    parser.add_argument('--alias', type=str)

  def handle(self, *args, **options):
    if not (options['alias'] or options['ipv4'] or options['ipv6']):
      self.stderr.write(
          "You must define either an alias or an address for the name")
      return
    elif(options['alias'] and (options['ipv4'] or options['ipv6'])):
      self.stderr.write("Cannot define a record to be both an alias (CNAME) " +
        "and point to an IP (A/AAAA) at the same time")
      return

    domainname = '.'.join(options['name'].split('.')[1:])
    hostname = options['name'].split('.')[0]

    try:
      domain = Domain.objects.get(name=domainname)
    except Domain.DoesNotExist:
      self.stderr.write("Could not find the domain '%s'" % domainname)
      return

    # If it is a CName-record:
    if(options['alias']):
      record = CName(name=hostname, domain=domain,
                    record_type=Record.TYPE_MANUAL, target=options['alias'])
    # If it is an A/AAAA record:
    else:
      if(options['ipv4']):
        try:
          ipv4 = str(ipaddress.IPv4Address(options['ipv4']))
        except ipaddress.AddressValueError:
          self.stderr.write(
              "'%s' does not look like an IPv4 address" % options['ipv4'])
          return
      else:
        ipv4 = None

      if(options['ipv6']):
        try:
          ipv6 = str(ipaddress.IPv6Address(options['ipv6']))
        except ipaddress.AddressValueError:
          self.stderr.write(
              "'%s' does not look like an IPv6 address" % options['ipv6'])
          return
      else:
        ipv6 = None

      record = Forward(name=hostname, domain=domain, reverse=True,
                      record_type=Record.TYPE_MANUAL, ipv4=ipv4, ipv6=ipv6)

    # Save the record, and update DNS
    try:
      record.save()
      record.configure()
      self.stdout.write("Record created")
    except django.db.utils.IntegrityError:
      self.stderr.write("Record already exists")
    except Exception as e:
      self.stderr.write("Could not create record!")
      self.stderr.write(e)
