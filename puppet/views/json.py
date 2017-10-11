import itertools
import json 

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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
