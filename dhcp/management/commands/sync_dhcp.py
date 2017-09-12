import pypureomapi
import ipaddress
from configparser import NoOptionError

from django.core.management.base import BaseCommand, CommandError

from dashboard.settings import parser
from dhcp.models import Subnet, Lease

class Command(BaseCommand):
  help = "Loads all active reservations from DHCP server" 

  def handle(self, *args, **options):
    try:
      host = parser.get("DHCP", "omapiHost")
      port = parser.get("DHCP", "omapiPort")
      name = parser.get("DHCP", "omapiKeyname")
      key = parser.get("DHCP", "omapiKey")
    except NoOptionError as e:
      self.stderr.write("Could not find omapi configuration in the configfile")
      self.stderr.write(" - %s" % str(e))

    try:
      connection = pypureomapi.Omapi(host, int(port), name.encode('utf-8'), key)
    except pypureomapi.OmapiError:
      self.stderr.write("Could not connect to DHCP server trough the OMAPI")
      return

    for subnet in Subnet.objects.filter(active=True).all():
      gateway = parser.get("DHCP", "%sGateway" % subnet.name)
      reservedAddresses = []
      free = 0
      try:
        reserved = parser.get("DHCP", "%sReserved" % subnet.name)
        for address in reserved.split(','):
          if('-' in address):
            first = ipaddress.ip_address(address.split('-')[0])
            last = ipaddress.ip_address(address.split('-')[1])
            for ip in range(int(first), int(last)+1):
              reservedAddresses.append(ipaddress.ip_address(ip))
          else:
            reservedAddresses.append(ipaddress.ip_address(address))
      except NoOptionError:
        pass

      for host in subnet.getSubnet().hosts():
        if(gateway == str(host) or host in reservedAddresses):
          continue

        try:
          mac = connection.lookup_mac(str(host))
        except pypureomapi.OmapiErrorNotFound:
          free += 1
          continue

        self.stdout.write(host)

        try:
          lease = Lease.objects.get(MAC=mac)
          if(lease.IP != str(host)):
            lease.IP = str(host)
            lease.save()
            self.stdout.write("Updating IP address for %s (%s)" % (lease.MAC,
                lease.IP))
        except Lease.DoesNotExist:
          lease = Lease(IP=str(host), MAC=mac, subnet=subnet)
          lease.save()
          self.stdout.write("Adding a new lease for %s (%s)" % (lease.MAC, 
              lease.IP))

      subnet.free = free
      subnet.save()
