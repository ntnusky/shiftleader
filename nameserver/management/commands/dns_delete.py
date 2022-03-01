import ipaddress
import django.db.utils

from django.core.management.base import BaseCommand

from host.models import Interface
from nameserver.models import Domain, Record, StaticRecord, Forward, CName, Reverse

class Command(BaseCommand):
  help = "Register a DNS static record"

  def add_arguments(self, parser):                                               
    parser.add_argument('--name', type=str, required=True)

  def handle(self, *args, **options):
    domainname = '.'.join(options['name'].split('.')[1:])
    hostname = options['name'].split('.')[0]

    try:
      domain = Domain.objects.get(name=domainname)
    except Domain.DoesNotExist:
      self.stderr.write("Could not find the domain '%s'" % domainname)
      return

    # Try to delete both Forward and CName if it exists.
    deleted = []
    for rt in [Forward, CName]:
      try:
        record = rt.objects.get(name=hostname, domain=domain)
      except rt.DoesNotExist:
        continue

      if(record.record_type != Record.TYPE_MANUAL):
        self.stderr.write("Can only delete manually defined records")
        return

      record.delete()
      deleted.append(rt)

    if(CName in deleted):
      self.stdout.write("Deleted CNAME record for '%s'" % options['name'])
    if(Forward in deleted):
      self.stdout.write("Deleted A/AAAA record for '%s'" % options['name'])
    if not len(deleted):
      self.stderr.write("No records found for '%s'" % options['name'])
