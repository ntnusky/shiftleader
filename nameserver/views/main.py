from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from dashboard.utils import createContext, requireSuperuser
from nameserver.models import Domain, Server

@user_passes_test(requireSuperuser)
def index(request):
  context = createContext(request)
  context['header'] = "DNS status"
  context['servers'] = Server.objects.all()
  context['domains'] = Domain.objects.all()

  return render(request, "dnsStatus.html", context)
