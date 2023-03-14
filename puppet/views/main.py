from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test 
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError

from dashboard.models import Task
from dashboard.utils import createContext, requireSuperuser
from puppet.constants import R10KDEPLOY
from puppet.models import Version, Role, Environment, Server, ReportLog

@user_passes_test(requireSuperuser)
def index(request):
  context = createContext(request)
  context['header'] = "Puppet status"
  return render(request, 'puppet/status.html', context)

@user_passes_test(requireSuperuser)
def message(request, id):
  context = createContext(request)
  context['header'] = "Puppet message"
  context['log'] = get_object_or_404(ReportLog, pk=id)
  return render(request, 'puppet/message.html', context)
