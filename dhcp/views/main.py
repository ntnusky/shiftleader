from django.contrib.auth.decorators import user_passes_test 
from django.shortcuts import render, get_object_or_404

from dashboard.utils import createContext, requireSuperuser
from dhcp.models import Subnet, Lease
from nameserver.models import StaticRecord

@user_passes_test(requireSuperuser)
def index(request):
  context = createContext(request)
  context['header'] = "DHCP status"
  context['subnets'] = Subnet.objects.order_by('name', 'ipversion').all()
  return render(request, 'dhcpStatus.html', context)

@user_passes_test(requireSuperuser)
def subnet(request, id):
  context = createContext(request)
  context['header'] = "DHCP status"
  context['subnet'] = get_object_or_404(Subnet, pk=id)
  context['addresses'] = []

  subnet = context['subnet'].getSubnet()
  reserved = context['subnet'].getReservedAddresses()
  for address in subnet.hosts():
    if address in reserved:
      sr = StaticRecord.objects.filter(ipv4=str(address)).all()
      if(len(sr) > 0):
        names = []
        for s in sr:
          names.append("%s.%s" % (s.name, s.domain.name))
        context['addresses'].append({'ip': address, 'text': "Static: %s" %
            ",".join(names)})
      else:
        context['addresses'].append({'ip': address, 'text': "Reserved"})
    else:
      try:
        ip = str(address)
        lease = Lease.objects.get(subnet=context['subnet'], present=True, IP=ip)
        try:
          i = lease.interface
        except: 
          context['addresses'].append({'ip': address, 'text': "Free"})
          if(lease.present):
            lease.present = False
            lease.save()
        else:
          context['addresses'].append({'ip': address, 'text': str(lease)})
      except Lease.DoesNotExist:
        context['addresses'].append({'ip': address, 'text': "Free"})

  return render(request, 'dhcpSubnet.html', context)
