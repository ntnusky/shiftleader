import os
import subprocess
import yaml

from django.core.management.base import BaseCommand

from puppet.models import Environment, Role
from host.models import Host

class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument(
      '--delete',
      dest='delete',
      action='store_true',
      help='Actually delete the environments',
    )

  def handle(self, *args, **options):
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
      return

    # For each environment not found in r10k, try to delete it:
    for e in Environment.objects.exclude(name__in=r10kenv).all():
      # If the environment have hosts, it cannot be deleted.
      if Host.objects.filter(environment=e).count() > 0:
        self.stderr.write("The environment %s contains hosts." % e.name)
        self.stderr.write("The environment is thus not deleted for now")
        continue
      
      # If any of the roles in the environment has host, it cannot be deleted.
      toDelete = True
      for role in Role.objects.filter(environment=e).all():
        if role.host_set.count() > 0:
          self.stderr.write("The role %s contains hosts." % role.name)
          self.stderr.write("You should probably run the command puppet_env2fix")
          toDelete = False
          break

      # Print the correct statusmessage, and delete env if possible.
      if(options['delete'] and toDelete):
        self.stdout.write("Deleting the environment %s" % e.name)
        e.delete()
      elif(options['delete']):
        self.stderr.write("The environment %s should be deleted, but couldn't" %
          e.name)
      else:
        self.stdout.write("Would delete %s if the --delete option was set" %
          e.name)
