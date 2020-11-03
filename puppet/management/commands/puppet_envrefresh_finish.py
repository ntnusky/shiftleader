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

# This command is a small utility marking on-going env-refreshes as finished
class Command(BaseCommand):
  def handle(self, *args, **options):
    with transaction.atomic():
      for task in Task.objects.filter(typeid=R10KENVIMPORT, 
            status=Task.PROGRESS).all():
        task.status = Task.FINISHED
        task.save()
