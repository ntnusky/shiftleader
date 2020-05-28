from os import path

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponseBadRequest, QueryDict
from django.utils.datastructures import MultiValueDictKeyError

from dashboard.utils import requireSuperuser

from netinstall.models import BootTemplate, ConfigFileType, ConfigFile, \
                              OperatingSystem

@user_passes_test(requireSuperuser)
def main(request, tid=None):
  """ API View - Add/update/delete Boot-templates 

  This view let you create, update and delete boot-templates.

  Possible Parameters:
    id:             An integer representing the template to update or delete.
    name:           A string representing the display-name of the template.
    description:    A textual description of the template.
    tftpconfig:     An integer representing a config-file to use as
                    tftp-configuration.
    installconfig:  An integer representing a config-file which will be passed
                    to the OS installer. (preseed or kickstart)
    postinstall:    An integer representing a config-file which will be ran
                    as a script after the OS installation is finished.
    os:             An os shortname describing which OS to install.
  
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

  if(request.method == 'GET' and not tid):
    data = []
    for element in BootTemplate.objects.order_by('name').all():
      data.append(element.toJSON())
    return JsonResponse(data, safe=False)

  elif(request.method == 'GET' and tid):
    try:
      return JsonResponse(BootTemplate.objects.get(id=tid).toJSON())
    except BootTemplate.DoesNotExist:
      return JsonResponse({
        'status': 'danger',
        'message': 'Could not find BootTemplate',
      }, status=404)
      
  elif(request.method == 'DELETE'):
    if not tid:
      data = QueryDict(request.body)
      shortname = data['id']

    try:
      template = BootTemplate.objects.get(id=tid)
    except BootTemplate.DoesNotExist:
      return JsonResponse({
        'status': 'error',
        'message': 'Could not find template with id %s' % tid,
        }, status = 404)

    template.delete()
    return JsonResponse({
      'status': 'success',
      'message': 'Deleted template %s' % template.name,
    })

  elif((request.method == 'POST' and not tid) or request.method == 'PUT'):
    data = QueryDict(request.body)

    # Return a bad request if mandatory fields are missing
    fields = ['name', 'description', 'tftpconfig', 'installconfig',
              'postinstall', 'os']
    for f in fields:
      if f not in data:
        return JsonResponse({
          'status': 'warning',
          'message': 'Missing parameter (%s)' % f,
        }, status = 400)

    # If method is "POST" a new record should be created
    if(request.method == 'POST'):
      template = BootTemplate()
      response = 201 # if a new record is created, return HTTP Created
      message = 'Created a new Template' 

    # If method is "PUT" an existing record should be updated
    if(request.method == 'PUT'):
      # To update an existing record, the existing record must be fetched.
      try:
        if(not tid):
          tid = data['id']
        template = BootTemplate.objects.get(id=tid)
        response = 200 # if a record is updated, return HTTP OK
        message = 'Operating System information updated'
      except (BootTemplate.DoesNotExist, MultiValueDictKeyError):
        return JsonResponse({
          'status': 'danger',
          'message': 'Could not find Template',
          }, status = 404)

    if(data['tftpconfig'] != '0'):
      try:
        template.tftpconfig = ConfigFile.objects.get(id=data['tftpconfig'])
      except ConfigFile.DoesNotExist:
        return JsonResponse({
          'status': 'warning',
          'message': 'Could not find configfile for TFTP',
          }, status = 404)
    else:
      template.tftpconfig = None

    if(data['installconfig'] != '0'):
      try:
        template.installconfig = ConfigFile.objects.get(id=data['installconfig'])
      except ConfigFile.DoesNotExist:
        return JsonResponse({
          'status': 'warning',
          'message': 'Could not find configfile for installation',
          }, status = 404)
    else:
      template.installconfig = None

    if(data['postinstall'] != '0'):
      try:
        template.postinstall = ConfigFile.objects.get(id=data['postinstall'])
      except ConfigFile.DoesNotExist:
        return JsonResponse({
          'status': 'warning',
          'message': 'Could not find post-installation file',
          }, status = 404)
    else:
      template.postinstall = None

    if(data['os'] != '0'):
      try:
        template.os = OperatingSystem.objects.get(shortname=data['os'])
      except ConfigFile.DoesNotExist:
        return JsonResponse({
          'status': 'warning',
          'message': 'Could not find OS',
          }, status = 404)
    else:
      template.os = None

    if(len(data['name']) == 0):
      return JsonResponse({
        'status': 'warning',
        'message': 'Missing name',
      }, status = 400)
        
    # Create OS and report success.
    template.name         = data['name']
    template.description  = data['description']
    template.save()

    return JsonResponse({
      'status': 'success',
      'message': message 
    }, status = response)
  else:
    return JsonResponse({
      'status': 'danger',
      'message': 'Method "%s" is not implemented' % request.method,
    }, status = 400)
