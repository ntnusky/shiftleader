import ipaddress

from django.core.management.base import BaseCommand

from dhcp.models import Subnet, Lease
from dhcp.omapi import Servers
from host.models import Interface

class Command(BaseCommand):
  help = "Removes 'deleted' leases where a newer lease with the same MAC exists."

  def handle(self, *args, **options):
    servers = Servers()

    # For each subnet we are handling DHCP
    for subnet in Subnet.objects.filter(active=True, ipversion=4).all():
      self.stdout.write("Subnet %s" % subnet.name)

      # For each lease in the database
      for lease in Lease.objects.filter(subnet=subnet).order_by('id').all():
        if lease.present == False:
          print("Not Present: %s" % lease)

          macip = Lease.objects.filter(IP=lease.IP, MAC=lease.MAC, present=True).exclude(id=lease.id).all()
          print("MAC+IP:", macip)

          ip = Lease.objects.filter(IP=lease.IP, present=True).exclude(id=lease.id).all()
          print("IP:", ip)

          mac = Lease.objects.filter(MAC=lease.MAC, present=True).exclude(id=lease.id).all()
          print("MAC:", mac)

          if(len(mac)):
            print(" - DELETING THE OLD LEASE %s" % lease)
            lease.delete()

          print()
