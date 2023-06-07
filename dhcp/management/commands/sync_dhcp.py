import ipaddress

from django.core.management.base import BaseCommand

from dhcp.models import Subnet, Lease
from dhcp.omapi import Servers
from host.models import Interface

class Command(BaseCommand):
  help = "Loads all active reservations from DHCP server" 

  def handle(self, *args, **options):
    servers = Servers()

    # For each subnet we are handling DHCP
    for subnet in Subnet.objects.filter(active=True, ipversion=4).all():
      self.stdout.write("Subnet %s" % subnet.name)
      used = subnet.getReservedAddresses()

      # For each lease in the database
      for lease in Lease.objects.filter(subnet=subnet).order_by('id').all():
        name = None
        try:
          if(lease.interface.primary):
            name = "%s.%s" % (lease.interface.host.name, 
                lease.interface.host.getDomain())
        except Interface.DoesNotExist:
          pass

        status = servers.configureLease(lease.IP, lease.MAC, lease.present,
          name, debug=True)

        if status & Servers.CREATED:
          self.stdout.write("Created lease for %s->%s" % (lease.IP, lease.MAC))
        if status & Servers.UPDATED:
          self.stdout.write("Updated lease for %s->%s" % (lease.IP, lease.MAC))
        if status & Servers.DELETED:
          self.stdout.write("Deleted lease for %s->%s" % (lease.IP, lease.MAC))

        if lease.present:
          used.append(ipaddress.IPv4Address(lease.IP))

      subnet.free = subnet.getSubnet().num_addresses - \
                        len(list(dict.fromkeys(used))) 
      subnet.save()
