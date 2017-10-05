import json
import os
import re
import socket
import subprocess
import yaml

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from puppet.models import Server, Environment, EnvironmentVersion, Role

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
    server.checkin(Server.STATUS_START)
    
    try:
      FNULL = open(os.devnull, "w")
      result = subprocess.run("/usr/local/bin/r10k deploy display",
          stdout=subprocess.PIPE, stderr=FNULL, shell=True)
      r10kenv = yaml.load(result.stdout)[':sources'][0][':environments']
    except:
      server.checkin(Server.STATUS_ERR)
      return

    # Parse all current environments
    path = '/etc/puppetlabs/code/environments/'
    available = os.listdir(path)
    levelInPath = len(path.rstrip('/').split('/'))
    environments = []
    for environmentName in r10kenv:
      server.checkin(Server.STATUS_RUN)
      try:
        environment = Environment.objects.get(name=environmentName)
      except Environment.DoesNotExist:
        environment = Environment(name=environmentName, active=True)
        environment.save()
        self.stdout.write("Creating environment %s" % environmentName)

      if(not environment.active):
        self.stdout.write("Enabling environment %s" % environmentName)
        environment.active = True
        environment.save()
      environments.append(environment)

      lastVersion = environment.environmentversion_set.filter(server=server).\
          last()
      if(lastVersion.status == EnvironmentVersion.STATUS_SCHEDULED):
        environment.environmentversion_set.create(server=server, signature="",
            started="", finished="", success=False,
            status=EnvironmentVersion.STATUS_DEPLOYING)
        lastVersion = environment.environmentversion_set.filter(server=server
            ).last()
        self.stdout.write("Deploying environment %s" % environment.name)
        logfile=open("/tmp/r10k-%s.log" % environment.name, "w")
        result = subprocess.run(
            "/usr/local/bin/r10k deploy environment %s -pv" % environment.name,
            stdout=logfile, stderr=logfile, shell=True)
        self.stdout.write("Deployed environment %s" % environment.name)
        lastVersion.status = EnvironmentVersion.STATUS_DEPLOYED
        lastVersion.save()
      elif(lastVersion.status == EnvironmentVersion.STATUS_DEPLOYING):
        self.stderr.write("Environment %s is alredy deploying" % \
            environmentName)
        continue

      try:
        envinfo = json.load(open(os.path.join(path, environmentName, 
            '.r10k-deploy.json'), "r"))
      except FileNotFoundError:
        self.stderr.write(\
            "Environment %s is not deployed yet" % environmentName)
        continue

      lastVersion.signature=envinfo['signature']
      lastVersion.started=envinfo['started_at']
      lastVersion.finished=envinfo['finished_at']
      lastVersion.success=envinfo['deploy_success']
      lastVersion.save()

      roles = []
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
            role = environment.role_set.create(name=fullname, active=True)
            self.stdout.write("Creating role %s-%s" % (environmentName, role))

          if not role.active:
            self.stdout.write("Enabling role %s-%s" % (environmentName, role))
            role.active = True
            role.save()
          roles.append(role)

      for role in environment.role_set.all():
        if role.active and role not in roles:
          role.active = False
          role.save()
          self.stdout.write("Disabling role %s-%s" % (environmentName, role))

    for env in Environment.objects.all():
      if env.active and env not in environments:
        env.active = False
        env.save()
        self.stdout.write("Disabled environment %s" % env.name)
    server.checkin(Server.STATUS_OK) 

