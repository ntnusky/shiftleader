from datetime import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from puppet.models import Report

class Command(BaseCommand):
  def add_arguments(self, parser):
    pass
    #parser.add_argument('fqdn', type=str)

  def handle(self, *args, **options):
    invalid = datetime.fromtimestamp(timezone.now().timestamp()-1209600)
    invalid = timezone.make_aware(invalid)
    todelete = Report.objects.filter(time__lt=invalid)
    number = todelete.count()
    todelete.all().delete()
