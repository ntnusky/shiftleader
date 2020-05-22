from django.contrib.auth.decorators import user_passes_test 
from django.http import JsonResponse, QueryDict
from django.shortcuts import get_object_or_404

from dashboard.utils import requireSuperuser
from puppet.models import Role, Environment

@user_passes_test(requireSuperuser)
def index(request, eid = None):
  data = QueryDict(request.body)

  if(eid):
    environment = get_object_or_404(Environment, pk=eid)
  elif('id' in data):
    environment = get_object_or_404(Environment, pk=data['id'])
  else:
    environment = None
  
  if(request.method == 'GET' and not environment):
    environments = []
    for env in Environment.objects.all():
      environments.append(env.toJSON())
    return JsonResponse(environments, safe=False)
  elif(request.method == 'GET' and environment):
    return JsonResponse(environment.toJSON())
  else:
    return JsonResponse({
      'status':'error', 
      'message': 'Method not implemented.'
    }, status=400) 
  
