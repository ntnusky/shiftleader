import os
import time

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from dashboard.settings import parser
from host.models import Host

class Command(BaseCommand):
  help = "Creates TFTP boot files"

  def add_arguments(self, parser):
    parser.add_argument('filter', type=str, nargs='?', default='all')

  def handle(self, *args, **options):
    choices = ['all', 'operational', 'provisioning', 'installing', 'puppet-sign', 
        'puppet-ready', 'error', 'timeout']
    filters = [-1, Host.OPERATIONAL, Host.PROVISIONING, Host.INSTALLING,
        Host.PUPPETSIGN, Host.PUPPETREADY, Host.ERROR, Host.TIMEOUT]

    if(options['filter'] not in choices):
      self.stderr.write("'%s' is not a valid option. Valid choices are:" %
          options['filter'] )
      for c in choices:
        self.stderr.write(' - %s' % c)
      return

    f = filters[choices.index(options['filter'])]
    if(f == -1):
      query = Host.objects
    else:
      query = Host.objects.filter(status = f)

    for host in query.all():
      self.stdout.write(str(host))
