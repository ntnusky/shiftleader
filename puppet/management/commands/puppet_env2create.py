import os
import subprocess
import yaml

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from puppet.models import Environment

class Command(BaseCommand):
  def handle(self, *args, **options):
    try:
      FNULL = open(os.devnull, "w")
      # Grab a list over current environments
      result = subprocess.run("/usr/bin/r10k deploy display",
          stdout=subprocess.PIPE, stderr=FNULL, shell=True)
      r10kenv = yaml.load(result.stdout)[':sources'][0][':environments']
    except Exception as e: 
      self.stderr.write("An error occurred: %s" % str(e))
      return

    # Parse all current environments
    path = '/etc/puppetlabs/code/environments/'
    levelInPath = len(path.rstrip('/').split('/'))
    environments = []
    for environmentName in r10kenv:
      environment, created = Environment.objects.get_or_create(
                                                  name=environmentName)
      environment.last_deployed = now()
      environment.save()

      if created:
        self.stdout.write("Creating environment %s" % environmentName)
