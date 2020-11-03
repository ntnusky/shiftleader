from http import HTTPStatus

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, QueryDict
from django.utils.datastructures import MultiValueDictKeyError

from dashboard.utils import requireSuperuser

from nameserver.models import Domain

@user_passes_test(requireSuperuser)
def main(request):
  if(request.method == 'GET'):
    domains = []
    for d in Domain.objects.all():
      domains.append(d.toJSON())
    return JsonResponse(domains, safe=False, status=HTTPStatus.OK.value)
  else:
    return JsonResponse({
      'message': 'Method not implemented.'
    }, status=HTTPStatus.NOT_IMPLEMENTED.value)
