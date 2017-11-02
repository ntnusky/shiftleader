from django.db import transaction 

from dashboard.utils import get_client_ip
from host.models import Host

NONE = 0
IP = 1
USER = 2

def authorize(request, host):
  ip = get_client_ip(request)

  primaryIF = host.interface_set.filter(primary=True).first()
  if(ip == primaryIF.ipv4Lease.IP or ip == primaryIF.ipv6):
    return IP
  elif (request.user.is_superuser):
    return USER
  else:
    return NONE

@transaction.atomic
def updatePuppetStatus():
  for host in Host.objects.all():
    host.updatePuppetStatus()
