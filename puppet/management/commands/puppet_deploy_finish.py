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
      tasks = Task.objects.filter(typeid=R10KDEPLOY, status=Task.PROGRESS,
                              payload="%s,%s" % (hostname,environment)).all()
      for task in tasks:
        task.status = Task.FINISHED
        task.save()
