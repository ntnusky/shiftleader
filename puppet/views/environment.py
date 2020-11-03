from http import HTTPStatus

from django.contrib.auth.decorators import user_passes_test 
from django.db import transaction
from django.http import JsonResponse, QueryDict
from django.shortcuts import get_object_or_404

from dashboard.models import Task
from dashboard.utils import requireSuperuser
from puppet.constants import R10KDEPLOY, R10KENVIMPORT
from puppet.models import Environment,  Server

@user_passes_test(requireSuperuser)
def index(request, eid = None):
  if(request.method == 'GET'):
    data = QueryDict(request.body)

    if(eid):
      environment = get_object_or_404(Environment, pk=eid)
    elif('id' in data):
      environment = get_object_or_404(Environment, pk=data['id'])
    else:
      environment = None

    if ( not environment):
      environments = []
      for env in Environment.objects.all():
        environments.append(env.toJSON())
      return JsonResponse(environments, safe=False)
    else:
      return JsonResponse(environment.toJSON())
  else:
    return JsonResponse({
      'status':'error', 
      'message': 'Method not implemented.'
    }, status=400) 
  
@user_passes_test(requireSuperuser)
def deploy(request, eid):
  data = {}
  environment = get_object_or_404(Environment, pk=eid)

  if(request.method == 'GET'):
    for server in Server.objects.all():
      task = Task.objects.filter(typeid=R10KDEPLOY, 
          payload="%s,%s" % (server.name, environment.name)).last()
      if(task and task.status == Task.READY):
        data[server.name.split('.')[0]] = 'Scheduled' 
      elif(task and task.status == Task.PROGRESS):
        data[server.name.split('.')[0]] = 'Deploying' 
      elif(task and task.status == Task.FINISHED):
        data[server.name.split('.')[0]] = 'Deployed' 
      else:
        data[server.name.split('.')[0]] = 'Undeployed'
    return JsonResponse(data)
  elif(request.method == 'POST'):
    for server in Server.objects.all():
      task = Task(system=Task.PUPPET, typeid=R10KDEPLOY)
      task.payload = "%s,%s" % (server.name, environment.name)
      task.save()
    return JsonResponse(data);
  else:
    return JsonResponse({
      'status':'error', 
      'message': 'Method not implemented.'
    }, status=400) 

@user_passes_test(requireSuperuser)
def discover(request):
  if(request.method == 'GET'):
    with transaction.atomic():
      running = Task.objects.filter(system=Task.PUPPET, status__in=[Task.READY,
                                  Task.PROGRESS], typeid=R10KENVIMPORT).count()
    if(running):
      code = HTTPStatus.ACCEPTED.value
      message = "A refresh of environments running"
      status = 'running'
    else:
      code = HTTPStatus.OK.value
      message = "No refresh is running"
      status = 'ok'
    return JsonResponse({'message': message, 'status': status}, status=code)
  elif(request.method == 'POST'):
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
        code = HTTPStatus.ACCEPTED.value
        message = "Scheduled a refresh of the environment-list"

    return JsonResponse({'message': message}, status=code)
  else:
    return JsonResponse({
      'status':'error', 
      'message': 'Method not implemented.'
    }, status=400) 
