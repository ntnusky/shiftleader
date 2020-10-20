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

class Command(BaseCommand):
  def handle(self, *args, **options):
    with transaction.atomic():
      try:
        task = Task.objects.filter(typeid=R10KENVIMPORT, status=Task.READY).first()
      except KeyError:
        sys.exit(1)

      if(task):
        task.status = Task.FINISHED
        task.save()

    if(task):
      print("Started %d" % task.id)
      sys.exit(0)
    else:
      sys.exit(2)
