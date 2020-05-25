from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, Http404, HttpResponseForbidden, \
                        HttpResponseServerError 
from django.shortcuts import render, redirect, get_object_or_404

from dashboard.utils import createContext, requireSuperuser
from netinstall.models import ConfigFile
from host.models import Host

@user_passes_test(requireSuperuser)
def file(request):
  context = createContext(request)
  context['header'] = "Config-files"
  return render(request, 'netinstall/files.html', context)

@user_passes_test(requireSuperuser)
def template(request):
  context = createContext(request)
  context['header'] = "Boot-Templates"
  return render(request, 'netinstall/templates.html', context)

@user_passes_test(requireSuperuser)
def filepreview(request, fid):
  configFile = get_object_or_404(ConfigFile, id=fid)
  return HttpResponse(configFile.getContent(None))
  
