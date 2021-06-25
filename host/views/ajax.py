import re
import ipaddress

from django.contrib.auth.decorators import user_passes_test 
from django.http import JsonResponse 

from dashboard.utils import requireSuperuser
from host.models import Interface

@user_passes_test(requireSuperuser)
def ifdelete(request, hid, iid):
  context = {}

  try:
    interface = Interface.objects.get(host__id=hid, id=iid)
  except:
    context['status'] = 'danger'
    context['message'] = 'Could not find interface'

  try:
    lease = interface.ipv4Lease
    lease.present = False
    lease.lease = False
    lease.save()
    lease.subnet.free += 1
    lease.subnet.save()
  except:
    pass

  interface.network.domain.deleteDomain(interface.host.name)

  interface.delete()

  context['status'] = 'success'
  context['message'] = 'Interface is deleted'

  return JsonResponse(context)
