import json
import os
import socket
import traceback
import logging

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from puppet.models import Server, Environment, Version, Role

logger = logging.getLogger(__name__)

class Command(BaseCommand):
  def add_arguments(self, parser):
    parser.add_argument('environment', type=str)

  def handle(self, *args, **options):
    env = options['environment']

    path = '/etc/puppetlabs/code/environments/'
    levelInPath = len(path.rstrip('/').split('/'))

    try:
      environment = Environment.objects.get(name=env)
      environment.active = True
      environment.save()
    except Environment.DoesNotExist:
      logger.error("Could not find the environment %s" % env)
      return

    for current, dirs, files in os.walk(os.path.join(path, env, 
        "modules/role/manifests")):
      for f in files:
        dirnames = current.split('/')[levelInPath+4:]
        classname = f.replace('.pp', '')
        dirnames.append(classname)
        fullname = "::".join(dirnames) 

        try:
          role = environment.role_set.get(name=fullname)
        except Role.DoesNotExist:
          role = environment.role_set.create(name=fullname)
          logger.info("Creating role %s-%s" % (env, role))
        role.last_deployed = now()
        role.save()
