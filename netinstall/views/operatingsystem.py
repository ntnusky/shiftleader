from os import path

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponseBadRequest, QueryDict

from dashboard.utils import requireSuperuser

from netinstall.models import OperatingSystem

@user_passes_test(requireSuperuser)
def main(request, shortname = None):
  """ API View - Add/update/delete operatingsystem 

  This view let you create, update and delete operating-system.

  Possible Parameters:
    id:           An integer representing the os to update or delete.
    name:         A string representing the display-name of the os.
    shortname:    A string representing a unique internal name for the os. 
    kernelurl:    An url pointing to a net-bootable kernel of the required OS.    
    kernelsum:    (optional) A checksum verifying the integrity of the kernel.
    initrdurl:    An url pointing to an initrd-image for booting the kernel.
    initrdsum:    (optional) A checksum verifying the integrity of the initrd
                  image.
  
  Methods:
    GET:          If an ID is specified (in the URL) a single os is returned as 
                  JSON. If no ID is specified a list of all os's are returned.
    DELETE:       Deletes a specified os. The configfile can either be
                  specified as an ID in the URL, or as a passed parameter.
    POST:         Creating a new os. Requires all the listed parameters (except
                  id) to be set. 
    PUT:          Updates an existing os. Needs all parameters to be set. The ID
                  can be set in the url or as a parameter.
  """ 
  data = {}

  if(request.method == 'GET' and not shortname):
    data = []
    for element in OperatingSystem.objects.order_by('name').all():
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
