import os
import socket
import subprocess
import sys
import yaml

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now

from dashboard.models import Task
from puppet.constants import R10KENVIMPORT
from puppet.models import Server, Environment, Version

# This command is a small utility returning 0 if a refresh of environments is
# requested.
class Command(BaseCommand):
  def handle(self, *args, **options):
    with transaction.atomic():
      try:
        task = Task.objects.filter(typeid=R10KENVIMPORT, status=Task.READY).first()
      except KeyError:
        sys.exit(1)

      if(task):
        task.status = Task.PROGRESS
        task.save()

    if(task):
      sys.exit(0)
    else:
      sys.exit(2)
