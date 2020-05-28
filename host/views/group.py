import re

from http import HTTPStatus

from django.contrib.auth.decorators import user_passes_test 
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError

from dashboard.utils import createEUI64, requireSuperuser, pretty_time

from dhcp.models import Subnet
from dhcp.omapi import Servers
from host.models import Host, Interface, HostGroup
from netinstall.models import BootTemplate
from puppet.models import Environment, Role

@user_passes_test(requireSuperuser)
def main(request):
  if(request.method == 'DELETE'):
    data = QueryDict(request.body)
    try:
      hostgroup = HostGroup.objects.get(pk=data['hgid'])
    except:
      return JsonResponse({
        'message': 'Group not found.'
      }, status=HTTPStatus.NOT_FOUND.value) 

    for h in hostgroup.host_set.all():
      h.group = None
      h.save()

    hostgroup.delete()

    return JsonResponse({
      'message': 'The hostgroup \'%s\' is deleted' % hostgroup.name
    }, status=HTTPStatus.OK.value) 
  else:
    return JsonResponse({
      'message': 'Method not implemented.'
    }, status=HTTPStatus.BAD_REQUEST.value) 
