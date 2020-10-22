from django.core.management.base import BaseCommand

from dashboard.models import Task

class Command(BaseCommand):
  def handle(self, *args, **options):
    Task.objects.all().delete()
