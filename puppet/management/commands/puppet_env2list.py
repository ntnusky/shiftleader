import os
import subprocess
import yaml

from django.core.management.base import BaseCommand

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

    for env in r10kenv:
      self.stdout.write(env)
