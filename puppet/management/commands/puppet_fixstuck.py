from django.core.management.base import BaseCommand

from puppet.models import Server, Version

class Command(BaseCommand):
  def handle(self, *args, **options):
    for server in Server.objects.all():
      v = server.getLatestVersion()
      if(v.status == Version.STATUS_DEPLOYING):
        v.status = Version.STATUS_ERROR
        v.save()
      
