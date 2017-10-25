from configparser import NoOptionError

from django.core.management.base import BaseCommand, CommandError

from dashboard.settings import parser
from host.models import Host
from nameserver.models import Server, Domain, StaticRecord

class Command(BaseCommand):
  help = ""

  def handle(self, *args, **options):
    for sr in StaticRecord.objects.filter(active=True).all():
      sr.configure()
    for host in Host.objects.all():
      host.updateDNS()
