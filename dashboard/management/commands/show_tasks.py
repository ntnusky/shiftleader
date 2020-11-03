from django.core.management.base import BaseCommand

from dashboard.models import Task

class Command(BaseCommand):
  def handle(self, *args, **options):
    for task in Task.objects.filter(status__in=[Task.READY, Task.PROGRESS]).all():
      print(task)
      if(task.payload):
        print(" - %s" % task.payload)
