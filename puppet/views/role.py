from django.contrib.auth.decorators import user_passes_test 
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from dashboard.utils import requireSuperuser
from puppet.models import Role, Environment

@user_passes_test(requireSuperuser)
def index(request, eid):
  environment = get_object_or_404(Environment, pk=eid)

  if(request.method == 'GET'):
    roles = []
    for role in environment.role_set.all():
      roles.append(role.toJSON())
    return JsonResponse(roles, safe=False)
  else:
    return JsonResponse({
      'status':'error', 
      'message': 'Method not implemented.'
    }, status=400) 
  
