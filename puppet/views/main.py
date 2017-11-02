from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test 
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError

from dashboard.utils import createContext, requireSuperuser
from puppet.models import Version, Role, Environment, Server, ReportLog

@user_passes_test(requireSuperuser)
def index(request):
  context = createContext(request)

  context['header'] = "Puppet status"

  context['servers'] = Server.objects.all()
  context['environments'] = Environment.objects.order_by('name').all()

  context['serverenvs'] = []
  for environment in context['environments']:
    data = {}
    data['environment'] = environment
    data['servers'] = []
    for server in context['servers']:
      latest = server.getLatestVersion(env=environment)
      data['servers'].append({'latest':latest, 'server':server})

    context['serverenvs'].append(data)

  return render(request, 'puppetStatus.html', context)

@user_passes_test(requireSuperuser)
def message(request, id):
  context = createContext(request)
  context['header'] = "Puppet message"
  context['log'] = get_object_or_404(ReportLog, pk=id)
  return render(request, 'puppetMessage.html', context)


@user_passes_test(requireSuperuser)
def deploy(request, eid, sid = 0):
  environment = get_object_or_404(Environment, pk=eid)
  if(sid != 0):
    servers = [get_object_or_404(Server, pk=sid)]
  else:
    servers = Server.objects.all()

  for server in servers:
    latestVersion = server.getLatestVersion(environment)
    if(not latestVersion or \
        (latestVersion and latestVersion.is_deployable())): 
      newVersion = Version(environment=environment, server=server, signature="",
          status=Version.STATUS_SCHEDULED)
      newVersion.save()
    elif(latestVersion and not latestVersion.is_deployable() and sid != 0):
      return HttpResponseBadRequest("Env %s is not deployable on %s" % \
          (environment, server))

  return redirect('puppetIndex')
