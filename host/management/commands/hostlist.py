from django.core.management.base import BaseCommand

from host.models import Host

class Command(BaseCommand):
  help = "Lists hostnames based on the provided filter"

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
