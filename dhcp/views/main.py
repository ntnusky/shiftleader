import re

from django.contrib.auth.decorators import user_passes_test 
from django.shortcuts import render

from dashboard.utils import createContext, requireSuperuser
from dashboard.settings import parser
from dhcp.models import Subnet, Lease

@user_passes_test(requireSuperuser)
def index(request):
  context = createContext(request)
  context['header'] = "DHCP status"
  return render(request, 'base/main.html', context)

