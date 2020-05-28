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

    if not os.path.exists(location):
      os.makedirs(location)

    path = os.path.join(location, 'default')
    open(path, "w").write(render_to_string('tftpboot/localboot.cfg', {}))

    for host in Host.objects.all():
      try:
        mac = host.interface_set.filter(primary=True).get().ipv4Lease.MAC
        filename = os.path.join(location, "01-%s" % mac.replace(':', '-'))

        f = open(filename, "w")
        f.write(host.getTFTPConfig())
        f.close()
      except:
        pass
