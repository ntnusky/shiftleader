from os import path

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponseBadRequest, QueryDict
from django.utils.datastructures import MultiValueDictKeyError

from dashboard.utils import requireSuperuser

from netinstall.models import ConfigFile, ConfigFileType

@user_passes_test(requireSuperuser)
def main(request, fid = None):
  """ API View - Add/update/delete configfile 

  This view let you create, update and delete configuration-files.

  Possible Parameters:
    id:           An integer representing the configfile to update or delete.
    name:         A string representing the display-name of the configfile.
    description:  A string describing the purpose of the configfile.
    content:      A string representing the content of the configfile
    filetype:     An int representing a ContentFileType object.
  
  Methods:
    GET:          If an ID is specified (in the URL) a single configfile is
                  returned as JSON. If no ID is specified a list of all
                  configfiles are returned.
    DELETE:       Deletes a specified configfile. The configfile can either be
                  specified as an ID in the URL, or as a passed parameter.
    POST:         Creating a new content-file. Requires the parameters name,
                  description, content and filetype to be set.
    PUT:          Updates an existing content-file. Requires the parameters
                  name, description, content and filetype to be set. The ID of
                  the file to update must be supplied in the URL or as the
                  parameter 'id'.
  """

  if(request.method == 'GET' and not fid):
    data = []
    for element in ConfigFile.objects.order_by('name').all():
      data.append(element.toJSON())
    return JsonResponse(data, safe=False)

  elif(request.method == 'GET' and fid):
    try:
      configfile = ConfigFile.objects.get(id=fid)
    except ConfigFile.DoesNotExist:
      return JsonResponse({
        'status': 'error',
        'message': 'Could not find file %s' % fid,
      }, status = 404)
    return JsonResponse(configfile.toJSON())

  elif(request.method == 'DELETE'):
    if not fid:
      data = QueryDict(request.body)
      fid = data['id']

    try:
      cf = ConfigFile.objects.get(id=fid)
    except ConfigFile.DoesNotExist:
      return JsonResponse({
        'status': 'error',
        'message': 'Could not find file %s' % fid,
        }, status = 404)

    cf.delete()

    return JsonResponse({
      'status': 'success',
      'message': 'Deleted file %s' % cf.name,
    })

  elif((request.method == 'POST' and not fid) or request.method == 'PUT'):
    data = QueryDict(request.body)

    # Return a bad request if mandatory fields are missing
    for f in ['name', 'description', 'content', 'filetype']:
      if f not in data:
        return JsonResponse({
          'status': 'error',
          'message': 'Missing parameter "%s"' % f,
        }, status = 400)

    try:
      filetype = ConfigFileType.objects.get(id=data['filetype'])
    except ConfigFileType.DoesNotExist:
      return JsonResponse({
        'status': 'error',
        'message': 'Could not fine filetype "%s"' % data['filetype'],
      }, status = 404)

    # If method is "POST" a new record should be created
    if(request.method == 'POST'):
      cf = ConfigFile()
      response = 201 # if a new record is created, return HTTP Created
      message = 'Created a new file'

    # If method is "PUT" an existing record should be updated
    if(request.method == 'PUT'):
      # To update an existing record, the existing record must be fetched.
      try:
        if(not fid):
          fid = data['id']
        cf = ConfigFile.objects.get(id=fid)
        response = 200 # if a record is updated, return HTTP OK
        message = 'File updated'
      except ConfigFile.DoesNotExist:
        return JsonResponse({
          'status': 'error',
          'message': 'Could not find file with id %s' % fid ,
        }, status = 404)
      except MultiValueDictKeyError:
        return JsonResponse({
          'status': 'error',
          'message': 'No file ID supplied',
        }, status = 400)
        
    cf.name = data['name']
    cf.description = data['description']
    cf.content = data['content']
    cf.filetype = filetype
    cf.save()

    return JsonResponse({
      'status': 'success',
      'message': message, 
    }, status = response)

  else:
    return JsonResponse({
      'status': 'error',
      'message': 'Method "%s" is not implemented' % request.method,
    }, status = 400)

@user_passes_test(requireSuperuser)
def filetype(request, ftid = None):
  """ API View - Add/update/delete configfile-type 

  This view let you create, update and delete configfile-type.

  Possible Parameters:
    id:           An integer representing the configfile to update or delete.
    name:         A string representing the display-name of the configfile.
  
  Methods:
    GET:          If an ID is specified (in the URL) a single configfile-type is
                  returned as JSON. If no ID is specified a list of all
                  configfile-types are returned.
    DELETE:       Deletes a specified configfile-type. The configfile can either 
                  be specified as an ID in the URL, or as a passed parameter.
    POST:         Creating a new file-type. Requires the parameters name
                  to be set.
    PUT:          Updates an existing configfile-type. Requires the parameters
                  name to be set. The ID of the file to update must be supplied
                  in the URL or as the parameter 'id'.
  """

  if(request.method == 'GET' and not ftid):
    data = []
    for element in ConfigFileType.objects.all():
      data.append(element.toJSON())
    return JsonResponse(data, safe=False)

  elif(request.method == 'GET' and ftid):
    try:
      ft = ConfigFileType.objects.get(id=ftid)
    except ConfigFileType.DoesNotExist:
      return JsonResponse({
        'status': 'error',
        'message': 'Could not find filetype %s' % ftid,
      }, status = 404)
    return JsonResponse(ft.toJSON())

  elif(request.method == 'DELETE'):
    if not ftid:
      data = QueryDict(request.body)
      ftid = data['id']

    try:
      ft = ConfigFileType.objects.get(id=ftid)
    except ConfigFileType.DoesNotExist:
      return JsonResponse({
        'status': 'error',
        'message': 'Could not find filetype %s' % ftid,
        }, status = 404)

    ft.delete()

    return JsonResponse({
      'status': 'success',
      'message': 'Deleted filetype %s' % ft.name,
    })

  elif((request.method == 'POST' and not ftid) or request.method == 'PUT'):
    data = QueryDict(request.body)

    # Return a bad request if mandatory fields are missing
    if 'name' not in data:
      return JsonResponse({
        'status': 'error',
        'message': 'Missing parameter "name"',
      }, status = 400)

    # If method is "POST" a new record should be created
    if(request.method == 'POST'):
      # Return a HTTP Conflict if an OS with the same name exists.
      if(ConfigFileType.objects.filter(name=data['name']).count()):
        return JsonResponse({
          'status': 'error',
          'message': 'Filetype with that name already exists',
          }, status = 409)

      ft = ConfigFileType()
      response = 201 # if a new record is created, return HTTP Created
      message = 'Created a new file type'

    # If method is "PUT" an existing record should be updated
    if(request.method == 'PUT'):
      if(not ftid and 'id' in data):
        ftid = data['id']
      elif(not ftid):
        return JsonResponse({
          'status': 'error',
          'message': 'No ID defined.',
        }, status = 400)
        
      # To update an existing record, the existing record must be fetched.
      try:
        ft = ConfigFileType.objects.get(id=ftid)
        response = 200 # if a record is updated, return HTTP OK
        message = 'File type information updated'
      except ConfigFileType.DoesNotExist:
        return JsonResponse({
          'status': 'error',
          'message': 'Could not find filetype with id %s' % data['id'],
          }, status = 404)
        
    ft.name = data['name']
    ft.save()

    return JsonResponse({
      'status': 'success',
      'message': message, 
    }, status = response)
  else:
    return JsonResponse({
      'status': 'error',
      'message': 'Method "%s" is not implemented' % request.method,
    }, status = 400)
