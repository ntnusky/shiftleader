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
      return

    try:
      domain = Domain.objects.get(name=match.group(2))
    except:
      return

    host = None
    for h in Host.objects.filter(name=match.group(1)).all():
      if h.getDomain() == domain:
        host = h

    if not host:
      return

    host.status = Host.OPERATIONAL
    host.save()

    self.stdout.write("---")
    self.stdout.write("environment: %s" % host.environment.name)
    self.stdout.write("classes:")
    self.stdout.write(" - role::%s" % host.role.name)
