from django.db import transaction 
from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse

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
    reverse('host_api_postinstall', args=[host.id]),
  )

  data['PUPPETSERVER'] = parser.get('puppet', 'server') 
  data['PUPPETCA'] = parser.get('puppet', 'caserver')

  return data

def getBootConfigFile(hostid, request, filetype):
  filetypes = ['TFTP', 'PostInstall', 'InstallConfig']
  statuschange = {
    'PostInstall': Host.PUPPETSIGN,
    'InstallConfig': Host.INSTALLING,
  }

  if filetype not in filetypes:
    raise ValueError(
        'Not a supported fil eype. Supported is %s' % \
        ', '.join(filetypes)
    )

  try:
    host = Host.objects.get(pk=hostid)
  except:
    auth = NONE
  else:
    auth = authorize(request, host)

  if auth == NONE:
    return HttpResponseForbidden("This call needs authorization")

  if(filetype == 'TFTP' and host.template.tftpconfig):
    if(int(host.status) == Host.PROVISIONING):
      content = host.template.tftpconfig.getContent(host)
    else:
      return render(request, 'tftpboot/localboot.cfg', {})
  elif(filetype == 'InstallConfig' and host.template.installconfig):
    content = host.template.installconfig.getContent(host)
  elif(filetype == 'PostInstall' and host.template.postinstall):
    content = host.template.postinstall.getContent(host)
  else:
    raise Http404

  if auth == IP and filetype in statuschange:
    host.status = statuschange[filetype]
    host.save()

  return HttpResponse(content)

@transaction.atomic
def updatePuppetStatus():
  for host in Host.objects.all():
    host.updatePuppetStatus()
