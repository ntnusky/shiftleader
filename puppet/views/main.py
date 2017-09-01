from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test 
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError

from dashboard.utils import createContext, requireSuperuser
from puppet.models import Role, Environment

@user_passes_test(requireSuperuser)
def index(request):
  context = createContext(request)

  context['header'] = "Puppet status"

  context['environments'] = Environment.objects.order_by('-active','name').all()

  return render(request, 'puppetStatus.html', context)
