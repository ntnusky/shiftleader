from configparser import NoOptionError

from django.core.management.base import BaseCommand, CommandError

from dashboard.settings import parser
from host.models import Host
from nameserver.models import Server, Domain

class Command(BaseCommand):
  help = ""

  def handle(self, *args, **options):
    for host in Host.objects.all():
      host.updateDNS()
    #d = Domain.objects.first()
    #d.configureA("gw", "192.168.254.2")
