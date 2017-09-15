from django.contrib.auth.decorators import user_passes_test 
from django.shortcuts import render, get_object_or_404

from dashboard.utils import createContext, requireSuperuser
from host.models import Host
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
