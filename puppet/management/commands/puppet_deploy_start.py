import socket
import sys

from django.core.management.base import BaseCommand
from django.db import transaction

from dashboard.models import Task
from puppet.constants import R10KDEPLOY
from puppet.models import Server

class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument('hostname', type=str)

  def handle(self, *args, **options):
    hostname = options['hostname']

    fqdn = socket.getfqdn()
    try:
      server = Server.objects.get(name=fqdn)
    except Server.DoesNotExist:
      server = Server(name=fqdn)
      server.status = STATUS_TIMEOUT
      server.save()

    with transaction.atomic():
      task = Task.objects.filter(typeid=R10KDEPLOY, status=Task.READY,
                                        payload__startswith=hostname).first()

      if(task):
        task.status = Task.PROGRESS
        task.save()

    if(task):
      print(task.payload.split(',')[1])
      sys.exit(0)
    else:
      sys.exit(2)
