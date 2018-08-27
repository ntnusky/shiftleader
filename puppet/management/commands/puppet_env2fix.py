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
      '--fix',
      dest='fix',
      action='store_true',
      help='Updates the database with the fixes',
    )

  def handle(self, *args, **options):
    for host in Host.objects.all():
      self.stdout.write("Checking %s" % str(host))
      if(host.environment != host.role.environment):
        self.stdout.write(" - The host has another env than its role...")
        try:
          newRole = Role.objects.get(environment=host.environment,
              name=host.role.name)
        except:
          newRole = None

        if(options['fix']):
          self.stdout.write(" - Updating the role to %s" % str(newRole))
          host.role = newRole
          host.save()
        else:
          self.stdout.write(" - Would update the role to %s" % str(newRole))
          self.stdout.write(" - The change is note stored as --fix is not set")
      else:
        self.stdout.write(" - Seems fine")

