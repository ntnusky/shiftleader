from configparser import NoOptionError

from django.core.management.base import BaseCommand, CommandError

from dashboard.settings import parser
from host.models import Host
from nameserver.models import CName, Forward, Record, Reverse, StaticRecord

class Command(BaseCommand):
  help = ""

  def handle(self, *args, **options):
    for sr in StaticRecord.objects.filter(active=True).all():
      if(Forward.objects.filter(domain=sr.domain, name=sr.name).count() == 0):
        record = Forward(name=sr.name, domain=sr.domain, ipv4=sr.ipv4, 
                    ipv6=sr.ipv6, record_type=Record.TYPE_MANUAL, reverse=True, 
                    active=True)
        record.save()
      sr.delete()
    for host in Host.objects.all():
      host.updateDNS()

    for t in [Forward, CName, Reverse]: 
      for record in t.objects.filter(active=True).all():
        record.configure()
