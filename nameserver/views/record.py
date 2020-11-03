from http import HTTPStatus

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseBadRequest, JsonResponse, QueryDict

from dashboard.utils import requireSuperuser

from nameserver.models import Forward, CName, Record, Reverse
from nameserver.processor import processForm

@user_passes_test(requireSuperuser)
def all(request):
  if(request.method == 'GET'):
    records = []
    for r in CName.objects.all():
      records.append(r.toJSON())
    for r in Forward.objects.all():
      records.append(r.toJSON())
    for r in Reverse.objects.all():
      records.append(r.toJSON())
    return JsonResponse(records, safe=False, status=HTTPStatus.OK.value)
  elif(request.method == 'POST'):
    return processForm(request)
  elif(request.method == 'DELETE'):
    data = QueryDict(request.body)

    if(data['record_type'] == 'CNAME'):
      OBJ = CName
    elif(data['record_type'] == 'Forward'):
      OBJ = Forward
    elif(data['record_type'] == 'PTR'):
      OBJ = Reverse
    else:
      return HttpResponseBadRequest()

    try:
      record = OBJ.objects.get(pk=data['record_id'])
    except:
      return HttpResponseBadRequest()

    if(record.record_type == Record.TYPE_MANUAL):
      record.delete()
      return JsonResponse({
        'message': 'Record is deleted.',
      })
    else:
      return JsonResponse({
        'message': 'Only manually created records can be deleted.',
      }, status=HTTPSTATUS.METHOD_NOT_ALLOWED.value)
  else:
    return JsonResponse({
      'message': 'Method not implemented.'
    }, status=HTTPStatus.NOT_IMPLEMENTED.value)

@user_passes_test(requireSuperuser)
def cname(request):
  if(request.method == 'GET'):
    records = []
    for r in CName.objects.all():
      records.append(r.toJSON())
    return JsonResponse(records, safe=False, status=HTTPStatus.OK.value)
  else:
    return JsonResponse({
      'message': 'Method not implemented.'
    }, status=HTTPStatus.NOT_IMPLEMENTED.value)

@user_passes_test(requireSuperuser)
def forward(request):
  if(request.method == 'GET'):
    records = []
    for r in Forward.objects.all():
      records.append(r.toJSON())
    return JsonResponse(records, safe=False, status=HTTPStatus.OK.value)
  else:
    return JsonResponse({
      'message': 'Method not implemented.'
    }, status=HTTPStatus.NOT_IMPLEMENTED.value)

@user_passes_test(requireSuperuser)
def reverse(request):
  if(request.method == 'GET'):
    records = []
    for r in Reverse.objects.all():
      records.append(r.toJSON())
    return JsonResponse(records, safe=False, status=HTTPStatus.OK.value)
  else:
    return JsonResponse({
      'message': 'Method not implemented.'
    }, status=HTTPStatus.NOT_IMPLEMENTED.value)
