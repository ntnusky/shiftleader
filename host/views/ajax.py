import re
import ipaddress

from django.contrib.auth.decorators import user_passes_test 
from django.http import JsonResponse, HttpResponseBadRequest 
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt 

from dashboard.utils import requireSuperuser
from dhcp.models import Subnet
from dhcp.omapi import Servers 
from host.models import Host, Interface, PartitionScheme
from host.utils import updatePuppetStatus
from nameserver.models import Domain
from puppet.models import Environment, Role

@user_passes_test(requireSuperuser)
def form(request):
  context = {}
  context['environments'] = Environment.objects.all()
  context['subnets'] = Subnet.objects.filter(ipversion=4).all()
  context['partitionschemes'] = PartitionScheme.objects.all()
  return render(request, 'ajax/hostForm.html', context)

@user_passes_test(requireSuperuser)
def table(request):
  updatePuppetStatus()
  context = {}
  context['hosts'] = Host.objects.all()
  return render(request, 'ajax/hostTable.html', context)

@user_passes_test(requireSuperuser)
def roleList(request, name):
  context = {}
  environment = Environment.objects.get(name=name)
  context['roles'] = environment.role_set.all()
  return render(request, 'ajax/roleSelect.html', context)

@user_passes_test(requireSuperuser)
def roleMenu(request, id):
  context = {}
  environment = Environment.objects.get(pk=id)
  context['roles'] = environment.role_set.all()
  return render(request, 'ajax/roleMenu.html', context)

@user_passes_test(requireSuperuser)
def ifdelete(request, hid, iid):
  context = {}

  try:
    interface = Interface.objects.get(host__id=hid, id=iid)
  except:
    context['status'] = 'danger'
    context['message'] = 'Could not find interface'

  interface.delete()
  context['status'] = 'success'
  context['message'] = 'Interface is deleted'

  return JsonResponse(context)

@user_passes_test(requireSuperuser)
@csrf_exempt
def environment(request):
  response = {}
  
  ids = []
  pattern = re.compile(r'selectHost=([0-9]+)')
  values = request.POST.get('selected').split('&')
  for v in values:
    m = pattern.match(v)
    if m:
      ids.append(int(m.group(1)))
  
  hosts = []
  for h in ids:
    try:
      hosts.append(Host.objects.get(pk = h))
    except Host.DoesNotExist:
      return HttpResponseBadRequest()

  try:
    environment = Environment.objects.get(
        pk=int(request.POST.get('environment')))
  except:
    return HttpResponseBadRequest()

  names = []
  for host in hosts:
    names.append(host.name)
    host.environment = environment
    host.save()

  response['status'] = 'success'
  response['message'] = 'Changed the environment of "%s" to %s.' % \
      (', '.join(names), environment.name)
  return JsonResponse(response)

@user_passes_test(requireSuperuser)
@csrf_exempt
def role(request):
  response = {}
  
  ids = []
  pattern = re.compile(r'selectHost=([0-9]+)')
  values = request.POST.get('selected').split('&')
  for v in values:
    m = pattern.match(v)
    if m:
      ids.append(int(m.group(1)))
  
  hosts = []
  for h in ids:
    try:
      hosts.append(Host.objects.get(pk = h))
    except Host.DoesNotExist:
      return HttpResponseBadRequest("B")

  try:
    role = Role.objects.get(
        pk=int(request.POST.get('role')))
  except Exception as e:
    return HttpResponseBadRequest(str(e))

  names = []
  for host in hosts:
    names.append(host.name)
    host.role = role
    host.save()

  response['status'] = 'success'
  response['message'] = 'Changed the role of "%s" to %s.' % \
      (', '.join(names), role.name)
  return JsonResponse(response)

@user_passes_test(requireSuperuser)
@csrf_exempt
def noprovision(request):
  response = {}
  
  ids = []
  pattern = re.compile(r'selectHost=([0-9]+)')
  values = request.POST.get('selected').split('&')
  for v in values:
    m = pattern.match(v)
    if m:
      ids.append(int(m.group(1)))
  
  hosts = []
  for h in ids:
    try:
      hosts.append(Host.objects.get(pk = h))
    except Host.DoesNotExist:
      return HttpResponseBadRequest()

  for host in hosts:
    host.status = Host.OPERATIONAL
    host.save()

  response['status'] = 'success'
  response['message'] = 'Cancelled reinstall of hosts.'
  return JsonResponse(response)

@user_passes_test(requireSuperuser)
@csrf_exempt
def provision(request):
  response = {}
  
  ids = []
  pattern = re.compile(r'selectHost=([0-9]+)')
  values = request.POST.get('selected').split('&')
  for v in values:
    m = pattern.match(v)
    if m:
      ids.append(int(m.group(1)))
  
  hosts = []
  for h in ids:
    try:
      hosts.append(Host.objects.get(pk = h))
    except Host.DoesNotExist:
      return HttpResponseBadRequest()

  for host in hosts:
    host.status = Host.PROVISIONING
    host.save()

  response['status'] = 'success'
  response['message'] = 'Provisioned hosts for reinstall at next reboot'
  return JsonResponse(response)

@user_passes_test(requireSuperuser)
@csrf_exempt
def remove(request):
  response = {}
  
  ids = []
  pattern = re.compile(r'selectHost=([0-9]+)')
  values = request.POST.get('selected').split('&')
  for v in values:
    m = pattern.match(v)
    if m:
      ids.append(int(m.group(1)))
  
  hosts = []
  for h in ids:
    try:
      hosts.append(Host.objects.get(pk = h))
    except Host.DoesNotExist:
      return HttpResponseBadRequest()

  for host in hosts:
    host.remove()

  response['status'] = 'success'
  response['message'] = 'Removed the selected hosts.'
  return JsonResponse(response)

@user_passes_test(requireSuperuser)
def new(request):
  response = {}

  if(request.POST['partition'] == 'Default'):
    partition = None
  else:
    try:
      partition = PartitionScheme.objects.get(name=request.POST['partition'])
    except PartitionScheme.DoesNotExist:
      response['status'] = "danger"
      response['message'] = "Partition-scheme not found."

  try:
    environment = Environment.objects.get(name=request.POST['environment'])
    role = environment.role_set.get(name=request.POST['role'])
  except Exception as e:
    response['status'] = "danger"
    response['message'] = "The role or environment was not found. %s" % str(e)

  if(not environment.is_active()):
    response['status'] = "danger"
    response['message'] = "The environment is disabled."
    return JsonResponse(response)

  try:
    Host.objects.get(name=request.POST['hostname'])
  except Host.DoesNotExist:
    pass
  else:
    response['status'] = "danger"
    response['message'] = "A host with that hostname (%s) currently exists" \
        % (request.POST['hostname'])
    return JsonResponse(response)

  pattern = re.compile(r'^[0-9a-f]{2}(:[0-9a-f]{2}){5}$')
  macMatch = pattern.match(request.POST['mac'].lower())

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
  subnet = Subnet.objects.get(ipversion=4,
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

  
  host = Host(name=request.POST['hostname'], 
      environment=environment, status = Host.PROVISIONING, role=role,
      partition=partition)
  host.save()
  network = subnet.v4network.get()
  interface = Interface(ifname=request.POST['ifname'], mac=mac, host=host,
      primary=True, ipv4Lease=lease, network=network)
  interface.save()

  dhcpservers = Servers()
  dhcpservers.configureLease(lease.IP, lease.MAC, lease.present, str(host))

  host.updateDNS()
  host.generatePassword()
    
  response['message'] = "The host %s is created." % host
  response['status'] = 'success'

  return JsonResponse(response)

