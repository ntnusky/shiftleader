import itertools
import json 

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from puppet.models import Role, Environment

def status(request):
  status = {}
  
  status['environments'] = {}
  for environment in Environment.objects.filter(active=True).all():
    status['environments'][environment.name] = {}
    status['environments'][environment.name]['roles'] = []
    for role in environment.role_set.all():
      status['environments'][environment.name]['roles'].append(role.name)

  return JsonResponse(status)

@csrf_exempt
def update(request):
  response = {}
  changes = []

  # If the supplied data cannot be interpreted as json, return a "BAD REQUEST"
  # message.
  try:
    data = json.loads(request.body.decode('utf-8'))
  except Exception as e:
    response['message'] = "No data provided"
    response['exception'] = str(e)
    return JsonResponse(response, status=400)

  existingEnvironments = {}
  # Deactivating environments which does not exist anymore, and activating
  # environments which has reappeared.
  for env in Environment.objects.all():
    existingEnvironments[env.name] = env

    if env.name not in data['environments'] and env.active:
      env.active = False
      env.save()
      changes.append("Deactivated environment \"%s\"" % env.name)
    elif env.name in data['environments'] and env.active == False:
      env.active = True
      changes.append("Activated environment \"%s\"" % env.name)
      env.save()

  # Updating role list for new and existing environments.
  for e in data['environments']:
    # If environment exists, grab the existing one. Othervise, create a new.
    if e in existingEnvironments:
      environment = existingEnvironments[e]
    else:
      environment = Environment(name = e, active = True)
      changes.append("Created environment \"%s\"" % e)
      environment.save()

    # Construct list over roles in request, and existing roles (enabled and
    # disabled).
    roles = data['environments'][e]['roles']
    enabledRoles = environment.role_set.filter(active=True).values_list(
        'name', flat=True)
    disabledRoles = environment.role_set.filter(active=False).values_list(
        'name', flat=True)
    
    # Create list over changes. Which roles needs to be added, disabled and
    # enabled?
    newRoles = [r for r in roles if (r not in enabledRoles and 
        r not in disabledRoles)]
    disableRoles = [r for r in enabledRoles if r not in roles]
    enableRoles = [r for r in disabledRoles if r in roles]

    # Create new roles
    for role in newRoles:
      r = Role(name=role, active=True, environment=environment)
      r.save()
      changes.append("Created the role \"%s\" in \"%s\"" % (role, e))

    # Update existing roles.
    for role in itertools.chain(disableRoles, enableRoles):
      r = environment.role_set.get(name=role)
      r.active = (role in enableRoles)
      r.save()
      changes.append("%sabled the role \"%s\" in \"%s\"" % (
          "En" if role in enableRoles else "Dis", role, e))

  response['changes'] = changes
  return JsonResponse(response, status=200)
