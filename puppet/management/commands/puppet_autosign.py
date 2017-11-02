import re

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from dashboard.settings import parser
from host.models import Host
from nameserver.models import Domain

class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument('fqdn', type=str)

  def handle(self, *args, **options):
    fqdn = options['fqdn']
    pattern = re.compile(r'^([a-zA-Z0-9\-]+)\.([a-zA-Z0-9\.\-]+)$')
    match = pattern.match(fqdn)

    if(not match):
      self.stdout.write("1")
      return

    try:
      domain = Domain.objects.get(name=match.group(2))
      host = Host.objects.get(name=match.group(1), domain=domain)
    except:
      self.stdout.write("2")
      return

    if(int(host.status) == Host.PUPPETSIGN):
      self.stdout.write("0")
      host.status = Host.PUPPETREADY
      host.save()
    else:
      self.stdout.write("3")
      
      
