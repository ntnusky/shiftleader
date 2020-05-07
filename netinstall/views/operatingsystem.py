from os import path

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponseBadRequest, QueryDict

from dashboard.utils import requireSuperuser

from netinstall.models import OperatingSystem

@user_passes_test(requireSuperuser)
def main(request, shortname = None):
  data = {}

  if(request.method == 'GET' and not shortname):
    data = []
    for element in OperatingSystem.objects.all():
      data.append(element.toJSON())
    return JsonResponse(data, safe=False)

  elif(request.method == 'GET' and shortname):
    try:
      return JsonResponse(
          OperatingSystem.objects.get(shortname=shortname).toJSON()
      )
    except OperatingSystem.DoesNotExist:
      return JsonResponse({
        'status': 'error',
        'message': 'Could not find OS with shortname %s' % data['shortname'],
      }, status = 404)

  elif(request.method == 'DELETE'):
    if not shortname:
      data = QueryDict(request.body)
      shortname = data['shortname']

    try:
      opsys = OperatingSystem.objects.get(shortname=shortname)
    except OperatingSystem.DoesNotExist:
      return JsonResponse({
        'status': 'error',
        'message': 'Could not find OS with shortname %s' % shortname,
        }, status = 404)

    opsys.delete()
    return JsonResponse({
      'status': 'success',
      'message': 'Deleted OS %s' % opsys.name,
    })

  elif((request.method == 'POST' and not ftid) or request.method == 'PUT'):
    data = QueryDict(request.body)

    # Return a bad request if mandatory fields are missing
    fields = ['name', 'shortname', 'kernelurl', 'initrdurl']
    for f in fields:
      if f not in data:
        return JsonResponse({
          'status': 'error',
          'message': 'Missing parameter (%s)' % f,
        }, status = 400)

    # If method is "POST" a new record should be created
    if(request.method == 'POST'):
      # Return a HTTP Conflict if an OS with the same shortname exists.
      if(OperatingSystem.objects.filter(shortname=data['shortname']).count()):
        return JsonResponse({
          'status': 'error',
          'message': 'OS with that shortname already exists',
          }, status = 409)

      opsys = OperatingSystem()
      response = 201 # if a new record is created, return HTTP Created
      message = 'Created a new Operating System'

    # If method is "PUT" an existing record should be updated
    if(request.method == 'PUT'):
      if(not shortname):
        shortname = data['shortname']
      # To update an existing record, the existing record must be fetched.
      try:
        opsys = OperatingSystem.objects.get(shortname=shortname)
        response = 200 # if a record is updated, return HTTP OK
        message = 'Operating System information updated'
      except OperatingSystem.DoesNotExist:
        return JsonResponse({
          'status': 'error',
          'message': 'Could not find OS with shortname %s' % data['shortname'],
          }, status = 404)
        
    # Create OS and report success.
    opsys.name       = data['name']
    opsys.shortname  = data['shortname']
    opsys.kernelurl  = data['kernelurl']
    opsys.kernelname = path.basename(opsys.kernelurl)
    opsys.initrdurl  = data['initrdurl']
    opsys.initrdname = path.basename(opsys.initrdurl)

    if('kernelsum' in data):
      opsys.kernelsum  = data['kernelsum']
    if('initrdsum' in data):
      opsys.initrdsum  = data['initrdsum']

    opsys.save()

    return JsonResponse({
      'status': 'success',
      'message': message, 
    }, status = response)
  else:
    return JsonResponse({
      'status': 'error',
      'message': 'Method "%s" is not implemented' % request.method,
    }, status = 400)
