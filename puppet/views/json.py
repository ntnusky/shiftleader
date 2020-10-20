import itertools
import json 

from http import HTTPStatus

from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from dashboard.models import Task
from dashboard.utils import requireSuperuser
from puppet.constants import R10KENVIMPORT
from puppet.models import Role, Environment

def status(request):
  status = {}
  
  status['environments'] = {}
  for environment in Environment.objects.all():
    if(environment.is_active()):
      status['environments'][environment.name] = {}
      status['environments'][environment.name]['roles'] = []
      for role in environment.role_set.all():
        status['environments'][environment.name]['roles'].append(role.name)

  return JsonResponse(status)

@user_passes_test(requireSuperuser)
def envload(request):
  if(request.method == 'POST'):
    with transaction.atomic():
      running = Task.objects.filter(system=Task.PUPPET, status__in=[Task.READY,
                                  Task.PROGRESS], typeid=R10KENVIMPORT).count()
      if running:
        code = HTTPStatus.ALREADY_REPORTED.value
        message = "A refresh of environments are already running"
      else:
        task = Task(system=Task.PUPPET, status=Task.READY, typeid=R10KENVIMPORT,
                payload="")
        task.save()
        code = HTTPStatus.OK.value
        message = "Scheduled a refresh of the environment-list"

    return JsonResponse({'message': message}, status=code)
  else:
    return HttpResponseBadRequest("Method %s not implemented" % request.method)
