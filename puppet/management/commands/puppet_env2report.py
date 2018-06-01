import json
import os
import socket
import traceback

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from puppet.models import Server, Environment, Version, Role

class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument('environment', type=str)

  def handle(self, *args, **options):
    env = options['environment']

    fqdn = socket.getfqdn()
    try:
      server = Server.objects.get(name=fqdn)
    except Server.DoesNotExist:
      sys.stderr.write("Could not find the server")
      return

    try:
      environment = Environment.objects.get(name=env)
    except Environment.DoesNotExist:
      sys.stderr.write("Could not find the environment")
      return

    lastVersion = server.getLatestVersion(environment)

    # Grab the signature after the deployment.
    try:
      envinfo = json.load(open(os.path.join(path, env, 
          '.r10k-deploy.json'), "r"))
    except FileNotFoundError:
      self.stderr.write(\
          "Environment %s is not deployed yet" % environmentName)
      return

    try:
      vid = lastVersion.id
      lastVersion = Version.objects.get(id=vid) 
      # Save the version-object
      lastVersion.signature=envinfo['signature']
      lastVersion.status = Version.STATUS_DEPLOYED
      lastVersion.save()
    except Exception as err:
      sys.stderr.write("Could not save environment information:\n")
      sys.stderr.write(traceback.print_tb(err.__traceback__))
      return

    path = '/etc/puppetlabs/code/environments/'
    levelInPath = len(path.rstrip('/').split('/'))

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
        role.last_deployed = now()
        role.save()
