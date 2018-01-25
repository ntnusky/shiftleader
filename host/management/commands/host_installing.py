import os
import time

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from dashboard.settings import parser
from host.models import Host

class Command(BaseCommand):
  help = "Creates TFTP boot files"

  def handle(self, *args, **options):
    for host in Host.objects.filter(status = Host.INSTALLING).all():
      self.stdout.write(str(host))
