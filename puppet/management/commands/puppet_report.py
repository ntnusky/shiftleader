import json
import os
import re
import socket
import subprocess
import time
import traceback
import yaml

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.timezone import now

from puppet.models import Server, Environment, Version, Role
from host.models import Host

class Command(BaseCommand):
  def add_arguments(self, parser):
    pass
    #parser.add_argument('fqdn', type=str)

  def handle(self, *args, **options):
    #fqdn = options['fqdn']
    
    # Find or create a server-object, and checkin STATUS_START 
    fqdn = socket.getfqdn()
    try:
      server = Server.objects.get(name=fqdn)
    except Server.DoesNotExist:
      server = Server(name=fqdn)
    server.checkin(Server.STATUS_STARTED)
    
    try:
      FNULL = open(os.devnull, "w")
      # First, deploy production to make sure that we get a list over all
      # available environments.
      result = subprocess.run("/usr/bin/r10k deploy environment production",
          stdout=FNULL, stderr=FNULL, shell=True)
      # Grab a list over current environments
      result = subprocess.run("/usr/bin/r10k deploy display",
          stdout=subprocess.PIPE, stderr=FNULL, shell=True)
      r10kenv = yaml.load(result.stdout)[':sources'][0][':environments']
    except Exception as e: 
      self.stderr.write("An error occurred: %s" % str(e))
      server.checkin(Server.STATUS_ERR)
      return

    # Parse all current environments
    path = '/etc/puppetlabs/code/environments/'
    levelInPath = len(path.rstrip('/').split('/'))
    environments = []
    for environmentName in r10kenv:
      server.checkin(Server.STATUS_RUNNING)
      try:
        environment = Environment.objects.get(name=environmentName)
      except Environment.DoesNotExist:
        environment = Environment(name=environmentName)
        self.stdout.write("Creating environment %s" % environmentName)

      environment.last_deployed = now()
      environment.save()

      environments.append(environment)

      lastVersion = server.getLatestVersion(environment)
      self.stdout.write("Should %s be deployed?" % environment)
      if(lastVersion and lastVersion.status == Version.STATUS_SCHEDULED):
        self.stdout.write("YES")
        if(not environment.active):
          environment.active = True
          environment.save()

        lastVersion.status = Version.STATUS_DEPLOYING
        lastVersion.save()

        # Deploy r10k environment
        timestamp = int(time.time())
        self.stdout.write("Deploying environment %s" % environment.name)
        logfile=open("/tmp/r10k-%s.%s.log" % (environment.name, timestamp), "w")
        logfile.write("Deploying environment %s\n" % environment.name)
        result = subprocess.run(
            "/usr/bin/r10k deploy environment %s -pv" % environment.name,
            stdout=logfile, stderr=logfile, shell=True)
        self.stdout.write("Deployed environment %s" % environment.name)
        logfile.write("Deployed environment %s\n" % environment.name)

        # Grab the signature after the deployment.
        try:
          envinfo = json.load(open(os.path.join(path, environmentName, 
              '.r10k-deploy.json'), "r"))
        except FileNotFoundError:
          self.stderr.write(\
              "Environment %s is not deployed yet" % environmentName)
          logfile.write(\
              "Environment %s is not deployed yet\n" % environmentName)
          continue

        logfile.write("Saving the environment information\n")

        try:
          # Save the version-object
          lastVersion.signature=envinfo['signature']
          lastVersion.status = Version.STATUS_DEPLOYED
          lastVersion.save()
        except Exception as err:
          logfile.write("Could not save environment information:\n")
          logfile.write(traceback.print_tb(err.__traceback__))

        logfile.write("Saved the environment information\n")

        for current, dirs, files in os.walk(os.path.join(path, environmentName, 
            "modules/role/manifests")):
          for f in files:
            dirnames = current.split('/')[levelInPath+4:]
            classname = f.replace('.pp', '')
            dirnames.append(classname)
            fullname = "::".join(dirnames) 

            try:
              role = environment.role_set.get(name=fullname)
            except Role.DoesNotExist:
              role = environment.role_set.create(name=fullname)
              self.stdout.write("Creating role %s-%s" % (environmentName, role))
              logfile.write("Creating role %s-%s\n" % (environmentName, role))
            role.last_deployed = now()
            role.save()
          logfile.close()

    for e in Environment.objects.exclude(name__in=r10kenv).all():
      for host in Host.objects.filter(environment=e).all():
        host.environment = None
        host.save()
      self.stdout.write("Deleting the environment %s" % e.name)
      e.delete()

    server.checkin(Server.STATUS_OK) 
