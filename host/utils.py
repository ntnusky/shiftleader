from django.core.urlresolvers import reverse
from django.db import transaction 

from dashboard.settings import parser
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

def createReplacements(host):
  data = {}

  data['HOSTID'] = str(host.id)
  data['ROOTPW'] = host.password

  data['DASHBOARD'] = None
  for key, item in parser.items("hosts"):
    if(key == 'ipv4' or (data['DASHBOARD'] == None and key == 'main')):
      data['DASHBOARD'] = item

  data['POSTINSTALL'] = "%s%s" % (
    parser.get('general', 'api'), 
    reverse('hostPostinstall', args=[host.id]),
  )

  data['PUPPETSERVER'] = parser.get('puppet', 'server') 
  data['PUPPETCA'] = parser.get('puppet', 'caserver')

  return data

@transaction.atomic
def updatePuppetStatus():
  for host in Host.objects.all():
    host.updatePuppetStatus()
