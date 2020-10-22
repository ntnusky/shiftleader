from django.core.management.base import BaseCommand
from django.db import transaction

from dashboard.models import Task
from puppet.constants import R10KDEPLOY

class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument('hostname', type=str)
    parser.add_argument('environment', type=str)

  def handle(self, *args, **options):
    hostname = options['hostname']
    environment = options['environment']

    with transaction.atomic():
      task = Task.objects.get(typeid=R10KDEPLOY, status=Task.PROGRESS,
                              payload="%s,%s" % (hostname,environment))
      task.status = Task.FINISHED
      task.save()
