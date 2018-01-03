from configparser import NoOptionError

from django.core.management.base import BaseCommand, CommandError

from dashboard.settings import parser
from nameserver.models import Server, Domain

class Command(BaseCommand):
  help = ""

  def handle(self, *args, **options):
    serverObjects = {}
    try:
      servers = parser.get("DNS", "servers").split(',')
    except NoOptionError:
      self.stderr.write("No DNS servers listed in the configfile")
      return

    for server in servers:
      try:
        s = Server.objects.get(name=server)
        toSave = False
      except Server.DoesNotExist:
        s = Server(name=server)
        toSave = True
      
      try:
        serverAddress = parser.get("DNS", "%sAddress" % server)
      except NoOptionError:
        self.stderr.write("No IP-address for the server \"%s\" was found" % \
            server)
        continue

      if(s.address != serverAddress):
        self.stdout.write("Updated address for \"%s\". %s->%s" % (server, 
            s.address, serverAddress))
        s.address = serverAddress
        toSave = True

      try:
        key = parser.get("DNS", "%sKey" % server)
      except NoOptionError:
        key = None

      if(s.key != key):
        self.stdout.write("Updated key for \"%s\". %s->%s" % (server, 
            s.key, key))
        s.key = key
        toSave = True

      try:
        keyname = parser.get("DNS", "%sKeyname" % server)
      except NoOptionError:
        keyname = 'update'

      if(s.keyname != keyname):
        self.stdout.write("Updated keyname for \"%s\". %s->%s" % (server, 
            s.keyname, keyname))
        s.keyname = keyname
        toSave = True

      try:
        alg = parser.get("DNS", "%sAlgorithm" % server)
      except NoOptionError:
        alg = "HMAC-MD5.SIG-ALG.REG.INT"

      if(s.algorithm != alg):
        self.stdout.write("Updated algorithm for \"%s\". %s->%s" % (server, 
            s.algorithm, alg))
        s.algorithm = alg
        toSave = True

      if(toSave):
        s.save()

      serverObjects[server] = s

    try:
      domains = parser.items("Domains")
    except NoOptionError:
      self.stderr.write("Could not fetch domains from configfile")
      return

    for domain, server in domains:
      try:
        d = Domain.objects.get(name=domain)
        toSave = False
      except Domain.DoesNotExist:
        d = Domain(name=domain)
        toSave = True

      try:
        oldserver = d.server
      except:
        oldserver = None

      if(oldserver != serverObjects[server]):
        self.stdout.write("Updating server for %s %s->%s" % (domain, 
            oldserver, server))
        d.server = serverObjects[server]
        toSave = True

      if(toSave):
        d.save()
