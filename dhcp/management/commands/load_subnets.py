from configparser import NoOptionError

from django.core.management.base import BaseCommand, CommandError

from dashboard.settings import parser
from dhcp.models import Subnet
from host.models import Network
from nameserver.models import Domain

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
        domainName = parser.get('DHCP', '%sDomain' % pool) 
      except NoOptionError as e:
        self.stderr.write(
            " - Missing parameter in configfile. Subnet is ignored")
        self.stderr.write(" - %s" % str(e))
        continue

      try:
        domain = Domain.objects.get(name=domainName)
      except Domain.DoesNotExist:
        self.stderr.write(" - The domain %s is not found. Subnet is ignored" % \
            domainName)
        continue

      try:
        subnet = Subnet.objects.get(name=pool, ipversion=4)
        if(subnet.setSubnet(network, netmask)):
          self.stdout.write(" - Updating the pool with new net-id and mask")
        if(subnet.domain != domain):
          subnet.domain = domain
          subnet.save()
          self.stdout.write(" - Updating the pool with a new domain name")
      except Subnet.DoesNotExist:
        subnet = Subnet(name=pool, active=True, domain=domain)
        subnet.setSubnet(network, netmask)
        self.stdout.write(" - The pool is new.")

      try:
        v6prefix = parser.get('DHCP', '%sv6prefix' % pool).split('/')[0]
      except NoOptionError:
        v6prefix = None

      if v6prefix:
        try:
          v6subnet = Subnet.objects.get(name=pool, ipversion=6)
          if(v6subnet.setSubnet(v6prefix, 64)):
            self.stdout.write(" - Updating the v6pool with new net-id and mask")
          if(v6subnet.domain != domain):
            v6subnet.domain = domain
            v6subnet.save()
            self.stdout.write(" - Updating the v6pool with a new domain name")
        except Subnet.DoesNotExist:
          v6subnet = Subnet(name=pool, active=True, ipversion=6, domain=domain)
          v6subnet.setSubnet(v6prefix, 64)
      else:
        v6subnet = None

      try:
        network = Network.objects.get(name=pool)
        if(network.domain != domain):
          network.domain = domain
          network.save()
          self.stdout.write(" - Updating the networks domain")
        if(network.v4subnet != subnet):
          network.v4subnet = subnet
          network.save()
          self.stdout.write(" - Updating the networks v4subnet")
        if(network.v6subnet != v6subnet):
          network.v6subnet = v6subnet
          network.save()
          self.stdout.write(" - Updating the networks v6subnet")
      except Network.DoesNotExist:
        network = Network(name=pool, domain=domain, v4subnet=subnet,
            v6subnet=v6subnet)
        network.save()
        self.stdout.write(" - Created the network %s" % pool)
    
    activeNets = Subnet.objects.filter(active=True). \
        values_list('name', flat=True)
    netsToDisable = [ net for net in activeNets if net not in pools ]

    for net in netsToDisable:
      subnet = Subnet.objects.get(name=net)
      subnet.active = False
      subnet.save()
      self.stdout.write("Disabling the subnet '%s'" % net)
