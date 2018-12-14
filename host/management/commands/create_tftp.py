import os

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from dashboard.settings import parser
from host.models import Host

class Command(BaseCommand):
  help = "Creates TFTP boot files"

  def handle(self, *args, **options):
    data = {}
    location = os.path.join(parser.get("TFTP", "rootdir"), 'pxelinux.cfg')
    data['dashboardURL'] = None
    for key, item in parser.items("hosts"):
      if(key == 'ipv4' or (data['dashboardURL'] == None and key == 'main')):
        data['dashboardURL'] = item

    if not os.path.exists(location):
      os.makedirs(location)

    path = os.path.join(location, 'default')
    self.stdout.write("Creating %s based on %s" % (path, 'tftpboot/localboot.cfg'))
    open(path, "w").write(render_to_string('tftpboot/localboot.cfg', {}))

    for host in Host.objects.all():
      if(int(host.status) == Host.PROVISIONING and host.os):
        template = 'tftpboot/install.cfg'
      else:
        template = 'tftpboot/localboot.cfg'

      mac = host.interface_set.filter(primary=True).get().ipv4Lease.MAC
      filename = os.path.join(location, "01-%s" % mac.replace(':', '-'))
      data['host'] = host

      self.stdout.write("Creating %s based on %s" % (filename, template))
      open(filename, "w").write(render_to_string(template, data))
