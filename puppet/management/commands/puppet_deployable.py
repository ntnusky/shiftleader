import os
import socket
import subprocess
import sys
import yaml

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import now

from dashboard.models import Task
from puppet.constants import R10KDEPLOY
from puppet.models import Server, Environment, Version

class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument('hostname', type=str)

  def handle(self, *args, **options):
    # Find or create a server-object, and checkin STATUS_START 
    hostname = options['hostname']

    with transaction.atomic():
      try:
        task = Task.objects.filter(typeid=R10KDEPLOY, status=Task.READY,
                                          payload__startswith=hostname).first()
      except KeyError:
        sys.exit(1)

      if(task):
        task.status = Task.PROGRESS
        task.save()

    if(task):
      print(task)
      sys.exit(0)
    else:
      sys.exit(2)
