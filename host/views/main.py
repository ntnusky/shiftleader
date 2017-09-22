from django.contrib.auth.decorators import user_passes_test 
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404

from dashboard.utils import createContext, requireSuperuser, get_client_ip
from dashboard.settings import parser
from host.models import Host
from host.utils import authorize, NONE, IP, USER
from nameserver.models import Domain
from puppet.models import Environment

@user_passes_test(requireSuperuser)
def index(request):
  context = createContext(request)

  context['header'] = "Host status"
  context['hosts'] = Host.objects.all()
  context['domains'] = Domain.objects.all()
  context['environments'] = Environment.objects.filter(active=True).all()

  return render(request, 'hostOverview.html', context)

@user_passes_test(requireSuperuser)
def single(request, id):
  context = createContext(request)

  context['host'] = get_object_or_404(Host, pk=id)
  context['header'] = "%s.%s" % (context['host'].name,
      context['host'].domain.name)

  return render(request, 'hostStatus.html', context)

def preseed(request, id):
  context = {} 

  context['host'] = get_object_or_404(Host, pk=id)
  key, context['dashboardURL'] = parser.items("hosts")[0]
  context['diskname'] = '/dev/sda'

  auth = authorize(request, context['host'])
  if auth == NONE:
    return HttpResponseForbidden()

  if auth == IP:
    context['host'].status = Host.INSTALLING
    context['host'].save()

  return render(request, 'preseed/default.cfg', context)

def tftp(request, id):
  context = {} 

  key, context['dashboardURL'] = parser.items("hosts")[0]
  context['host'] = get_object_or_404(Host, pk=id)

  if not authorize(request, context['host']):
    return HttpResponseForbidden()

  if(int(host.status) == Host.PROVISIONING):
    template = 'tftpboot/install.cfg'
  else:
    template = 'tftpboot/localboot.cfg'

  return render(request, template, context)

def postinstall(request, id):
  context = {} 

  context['host'] = get_object_or_404(Host, pk=id)

  auth = authorize(request, context['host'])
  if auth == NONE:
    return HttpResponseForbidden()

  if auth == IP:
    context['host'].status = Host.PUPPETSIGN
    context['host'].save()

  return render(request, 'postinstall/postinstall.sh', context)
