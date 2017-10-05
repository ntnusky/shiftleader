from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test 
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError

from dashboard.utils import createContext, requireSuperuser
from puppet.models import EnvironmentVersion, Role, Environment, Server

@user_passes_test(requireSuperuser)
def index(request):
  context = createContext(request)

  context['header'] = "Puppet status"

  context['servers'] = Server.objects.all()
  context['environments'] = Environment.objects.order_by('-active','name').all()

  return render(request, 'puppetStatus.html', context)


@user_passes_test(requireSuperuser)
def deploy(request, sid, eid):
  try:
    environment = Environment.objects.get(pk=eid)
    server = Server.objects.get(pk=sid)
    ev = EnvironmentVersion.objects.filter(server=server,
        environment=environment).last()
    ev.status = EnvironmentVersion.STATUS_SCHEDULED
    ev.save()
  except Exception as e:
    return HttpResponseBadRequest(str(e))
  
  return redirect('puppetIndex')


