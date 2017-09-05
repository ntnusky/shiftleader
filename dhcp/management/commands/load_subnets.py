from configparser import NoOptionError

from django.core.management.base import BaseCommand, CommandError

from dashboard.settings import parser
from dhcp.models import Subnet
from dhcp.utils import calculateMaskLength

class Command(BaseCommand):
  help = "Reads the configuration-file and loads relevand dhcp configuration" \
      + " into the database"

  def handle(self, *args, **options):
    self.stdout.write("Reading the configuration file to find DHCP pools")
    try:
      pools = parser.get('DHCP', 'pools').split(',')
    except NoOptionError:
      self.stderr.write("No pools are defined in the configfile")
      return

    for pool in pools:
      self.stdout.write("Found the pool '%s'" % pool)
      try:
        network = parser.get('DHCP', '%sNetwork' % pool)
        netmask = parser.get('DHCP', '%sNetmask' % pool)
        gateway = parser.get('DHCP', '%sGateway' % pool) 
      except NoOptionError as e:
        self.stderr.write(
            " - Missing parameter in configfile. Subnet is ignored")
        self.stderr.write(" - %s" % str(e))
        continue

      mask = calculateMaskLength(netmask)
      
      toSave = False
      try:
        subnet = Subnet.objects.get(name=pool)
        if(subnet.setSubnet(network, mask)):
          self.stdout.write(" - Updating the pool with new net-id and mask")
      except Subnet.DoesNotExist:
        subnet = Subnet(name=pool, active=True, prefix=network, mask=mask)
        subnet.save()
        self.stdout.write(" - The pool is new.")
    
    activeNets = Subnet.objects.filter(active=True). \
        values_list('name', flat=True)
    netsToDisable = [ net for net in activeNets if net not in pools ]

    for net in netsToDisable:
      subnet = Subnet.objects.get(name=net)
      subnet.active = False
      subnet.save()
      self.stdout.write("Disabling the subnet '%s'" % net)
