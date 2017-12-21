import os

from django.core.management.base import BaseCommand

from host.models import Host, Network, Interface
from dhcp.models import Subnet

class Command(BaseCommand):
  help = "Adds the networks objects to existing lease-objects based " + \
          "on which subnet this object belongs to"

  def handle(self, *args, **options):
    
    for interface in Interface.objects.all():
      if interface.network:
        self.stdout.write("OK: %s" % interface)
      else:
        self.stdout.write("Missing: %s Primary: %s" % (interface,
            interface.primary))
        self.stdout.write(" - Should be %s" %
            interface.ipv4Lease.subnet.v4network.get())
        interface.network = interface.ipv4Lease.subnet.v4network.get()
        interface.save()

