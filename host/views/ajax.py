import re
import ipaddress

from django.contrib.auth.decorators import user_passes_test 
from django.http import JsonResponse 
from django.shortcuts import render

from dashboard.utils import requireSuperuser
from dhcp.models import Subnet
from dhcp.omapi import Servers 
from host.models import Host, Interface
from nameserver.models import Domain
from puppet.models import Environment

@user_passes_test(requireSuperuser)
def form(request):
  context = {}
  context['domains'] = Domain.objects.all()
  context['environments'] = Environment.objects.filter(active=True).all()
  context['subnets'] = Subnet.objects.all()
  return render(request, 'ajax/hostForm.html', context)

@user_passes_test(requireSuperuser)
def table(request):
  context = {}
  context['hosts'] = Host.objects.all()
  return render(request, 'ajax/hostTable.html', context)

@user_passes_test(requireSuperuser)
def new(request):
  response = {}

  domain = Domain.objects.get(name=request.POST['domain'])
  environment = Environment.objects.get(name=request.POST['environment'])

  if(not environment.active):
    response['status'] = "danger"
    response['message'] = "The environment is disabled."
    return JsonResponse(response)

  try:
    Host.objects.get(name=request.POST['hostname'], domain=domain)
  except Host.DoesNotExist:
    pass
  else:
    response['status'] = "danger"
    response['message'] = "A host with that hostname (%s.%s) currently exists" \
        % (request.POST['hostname'], domain.name)
    return JsonResponse(response)

  pattern = re.compile(r'^[0-9a-f]{2}(:[0-9a-f]{2}){5}$')
  macMatch = pattern.match(request.POST['mac'])

  if macMatch:
    mac = macMatch.group(0)
  else:
    response['status'] = "danger"
    response['message'] = "'%s' does not look like a mac address" % \
        request.POST['mac']
    return JsonResponse(response)

  try:
    interface = Interface.objects.get(mac=mac)
  except Interface.DoesNotExist:
    pass
  else:
    response['status'] = "danger"
    response['message'] = "An interface (%s) already has that MAC (%s)" % (
        interface, request.POST['mac'])
    return JsonResponse(response)

  pattern = re.compile(r'\'(.*)\'')
  subnet = Subnet.objects.get(
      name=pattern.match(request.POST['subnet']).group(1))
  
  if(len(request.POST['ipv4']) > 0):
    try:
      ip = ipaddress.IPv4Address(request.POST['ipv4'])
    except ValueError:
      response['status'] = "danger"
      response['message'] = "The IP address provided is invalid"
      return JsonResponse(response)

    if(ip not in subnet.getSubnet()):
      response['status'] = "danger"
      response['message'] = "The IP address provided is not in the selected subnet"
      return JsonResponse(response)

    if(ip in subnet.getReservedAddresses()):
      response['status'] = "danger"
      response['message'] = "The provided IP is reserved"
      return JsonResponse(response)

    lease = subnet.getLease(str(ip))
    if(lease):
      response['status'] = "danger"
      response['message'] = "The IP address provided is already in use (%s)" % \
          lease
      return JsonResponse(response)
    ip = str(ip)
  else:
    ip = None

  lease = subnet.createLease(mac, ip) 
  if(not lease):
    response['message'] = "Could not create IP address lease"
    response['status'] = "danger"
    return JsonResponse(response)
  
  host = Host(name=request.POST['hostname'], domain=domain,
      environment=environment, status = Host.PROVISIONING)
  host.save()
  interface = Interface(ifname=request.POST['ifname'],
      name=request.POST['ifdesc'], mac=mac, domain=domain, host=host,
      primary=True, ipv4Lease=lease)
  interface.save()

  dhcpservers = Servers()
  dhcpservers.configureLease(lease.IP, lease.MAC, lease.present, str(host))
    
  response['message'] = "The host %s is created." % host
  response['status'] = 'success'

  return JsonResponse(response)

