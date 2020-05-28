from os import path

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseBadRequest, HttpResponseForbidden,  \
                        JsonResponse, QueryDict
from django.shortcuts import get_object_or_404

from dashboard.utils import requireSuperuser

from netinstall.models import OperatingSystem

def main(request, osid = None):
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

  if(request.method == 'GET' and not osid):
    data = []
    for element in OperatingSystem.objects.order_by('name').all():
      data.append(element.toJSON())
    return JsonResponse(data, safe=False)

  elif(request.method == 'GET' and osid):
    opsys = get_object_or_404(OperatingSystem, pk=osid)
    return JsonResponse(opsys.toJSON())

  elif(request.method == 'DELETE'):
    # Return a HTTP Forbidden if the request is unauthenticated.
    if not request.user.is_superuser:
      return HttpResponseForbidden('This method requires AUTH')
      
    if not osid:
      data = QueryDict(request.body)
      osid = data['id']

    opsys = get_object_or_404(OperatingSystem, pk=osid)
    opsys.delete()

    return JsonResponse({
      'message': 'Deleted OS %s' % opsys.name,
    })

  elif((request.method == 'POST' and not osid) or request.method == 'PUT'):
    # Return a HTTP Forbidden if the request is unauthenticated.
    if not request.user.is_superuser:
      return HttpResponseForbidden('This method requires AUTH')

    data = QueryDict(request.body)

    # Return a bad request if mandatory fields are missing
    fields = ['name', 'shortname', 'kernelurl', 'initrdurl']
    for f in fields:
      if f not in data:
        return JsonResponse({
          'message': 'Missing parameter (%s)' % f,
        }, status = 400)

    # If method is "POST" a new record should be created
    if(request.method == 'POST'):
      # Return a HTTP Conflict if an OS with the same shortname exists.
      if(OperatingSystem.objects.filter(shortname=data['shortname']).count()):
        return JsonResponse({
          'message': 'OS with that shortname already exists',
          }, status = 409)

      opsys = OperatingSystem()
      response = 201 # if a new record is created, return HTTP Created
      message = 'Created a new Operating System'

    # If method is "PUT" an existing record should be updated
    if(request.method == 'PUT'):
      if(not osid):
        osid = data['id']

      # To update an existing record, the existing record must be fetched.
      opsys = get_object_or_404(OperatingSystem, pk=osid)
      response = 200 # if a record is updated, return HTTP OK
      message = 'Operating System information updated'
        
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
      'message': message, 
    }, status = response)
  else:
    return JsonResponse({
      'message': 'Method "%s" is not implemented' % request.method,
    }, status = 400)
