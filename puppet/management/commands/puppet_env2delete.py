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
    parser.add_argument(
      '--delete',
      dest='delete',
      default=False,
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

    for e in Environment.objects.exclude(name__in=r10kenv).all():
      if(options['delete']):
        for host in Host.objects.filter(environment=e).all():
          host.environment = None
          host.save()
        self.stdout.write("Deleting the environment %s" % e.name)
        e.delete()
      else:
        self.stdout.write("Would delete %s if the --delete option was set" %
          e.name)
