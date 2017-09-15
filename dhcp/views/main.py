from django.contrib.auth.decorators import user_passes_test 
from django.shortcuts import render

from dashboard.utils import createContext, requireSuperuser
from dhcp.models import Subnet

@user_passes_test(requireSuperuser)
def index(request):
  context = createContext(request)
  context['header'] = "DHCP status"
  context['subnets'] = Subnet.objects.all()
  return render(request, 'dhcpStatus.html', context)
