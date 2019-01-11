import datetime

from django.core.management.base import BaseCommand
from django.utils import timezone

from host.models import Interface
from nameserver.models import Domain, StaticRecord

class Command(BaseCommand):
  help = ""

  def add_arguments(self, parser):                                               
    parser.add_argument(                                                         
      '--delete',                                                                
      dest='delete',                                                             
      action='store_true',                                                       
      help='Delete names which expired for more than a month ago',                                   
    )

  def handle(self, *args, **options):
    for sr in StaticRecord.objects.all():
      if(sr.isExpired()):
        self.stdout.write("%s is expired" % sr)

        todelete = timezone.now().date() - datetime.timedelta(days=31)
        if(sr.expire < todelete):
          self.stdout.write("%s expired for more than a month ago" % sr)

          if(options['delete']):
            sr.deactivate()
            sr.delete()
            self.stdout.write("%s was deleted" % sr)
          else:
            self.stdout.write("%s would be deleted if the --delete flag was set" % sr)
