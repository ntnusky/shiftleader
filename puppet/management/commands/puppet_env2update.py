import os
import socket
import subprocess
import yaml

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from puppet.models import Server, Environment, Version

class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument('environment', type=str)

  def handle(self, *args, **options):
    env = options['environment']
    
    # Find or create a server-object, and checkin STATUS_START 
    fqdn = socket.getfqdn()
    try:
      server = Server.objects.get(name=fqdn)
    except Server.DoesNotExist:
      server = Server(name=fqdn)
    server.checkin(Server.STATUS_STARTED)
    
    try:
      FNULL = open(os.devnull, "w")
      # Grab a list over current environments
      result = subprocess.run("/usr/bin/r10k deploy display",
          stdout=subprocess.PIPE, stderr=FNULL, shell=True)
      r10kenv = yaml.load(result.stdout)[':sources'][0][':environments']
    except Exception as e: 
      self.stderr.write("An error occurred: %s" % str(e))
      server.checkin(Server.STATUS_ERR)
      return


    if(env not in r10kenv):
      sys.stdout.write("0")
      server.checkin(Server.STATUS_ERR)
      return

    try:
      environment = Environment.objects.get(name=env)
    except Environment.DoesNotExist:
      environment = Environment(name=env)
      self.stderr.write("Creating environment %s" % environmentName)

    environment.last_deployed = now()
    environment.save()

    lastVersion = server.getLatestVersion(environment)

    if(lastVersion and lastVersion.status == Version.STATUS_SCHEDULED):
      self.stdout.write("1")

      lastVersion.status = Version.STATUS_DEPLOYING
      lastVersion.save()

      if(not environment.active):
        environment.active = True
        environment.save()
    else:
      self.stdout.write("0")
    
    server.checkin(Server.STATUS_OK)
