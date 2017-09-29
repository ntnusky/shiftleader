import ipaddress
import re

from django.contrib.auth.decorators import user_passes_test 
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from dashboard.utils import createContext, requireSuperuser, get_client_ip
from dashboard.settings import parser
from dhcp.models import Subnet, Lease
from dhcp.omapi import Servers
from host.models import Host, Interface
from host.utils import authorize, NONE, IP, USER
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

@user_passes_test(requireSuperuser)
def interface(request, hid, iid = 0):
  context = createContext(request)
  change = False

  host = get_object_or_404(Host, pk=hid)

  if iid == 0:
    context['header'] = "Add interface to %s" % host.name
    context['buttonText'] = "Add interface"
    context['interface'] = Interface(host=host)
    context['lease'] = Lease()
  else:
    context['header'] = "Edit interface"
    context['buttonText'] = "Update interface"
    context['interface'] = get_object_or_404(Interface, host=host, pk=iid)
    context['lease'] = context['interface'].ipv4Lease
  
  context['subnets'] = Subnet.objects.all()

  if(request.POST.get('csrfmiddlewaretoken')):
    errors = []

    # Retrieve subnet, and verify IP if it is supplied
    subnetname = request.POST.get('subnet')
    match = re.match(r'\'([a-zA-Z0-9]+)\'', subnetname)
    subnet = Subnet.objects.get(name=match.group(1))
    
    ipText = request.POST.get('ipv4')
    if(ipText == None):
      ipText = ""
    if(len(ipText) > 0):
      # Verify that the IP is valid
      try:
        ip = ipaddress.IPv4Address(request.POST.get('ipv4'))
      except ValueError:
        errors.append("Invalid IP address")
      else:
        # Verify that the IP is free (or assigned to the interface already)
        if(ip not in subnet.getSubnet()):
          errors.append("Ip is not in the selected subnet")
        elif(ip in subnet.getReservedAddresses()):
          errors.append("IP is reserved")
        else:
          lease = subnet.getLease(str(ip))
          if(lease and lease.interface != context['interface']):
            errors.append("IP is in use")
      context['lease'].IP = ipText
      change = True
    else:
      ip = None

    ipv6Text = request.POST.get('ipv6')
    if(len(ipv6Text) > 0 and ipv6Text != context['interface'].ipv6):
      try:
        ipv6 = ipaddress.IPv6Address(ipv6Text)
      except ValueError:
        errors.append("Invalid IPv6 address")
      else:
        try:
          i = Interface.objects.get(ipv6=ipv6Text)
          if(i.host != host):
            errors.append("IPv6 is already assigned to a host")
        except Interface.DoesNotExist:
          pass
      context['interface'].ipv6 = ipv6Text
      change = True
    else:
      context['interface'].ipv6 = None
      ipv6Text = None
    
    oldName = context['interface'].name
    newName = request.POST.get('name')
    if(context['interface'].name != newName):
      change = True
      try:
        i = host.interface_set.get(name=newName)
        errors.append("The host already have an interface with this name")
      except Interface.DoesNotExist:
        pass
      context['interface'].name = newName

    oldIFName = context['interface'].ifname
    newIFName = request.POST.get('ifname')
    if(context['interface'].ifname != newIFName):
      change = True
      try:
        i = host.interface_set.get(ifname=newIFName)
        errors.append("The host already have an interface with this ifname")
      except Interface.DoesNotExist:
        pass
      context['interface'].ifname = newIFName

    try:
      oldMAC = context['interface'].ipv4Lease.MAC
    except AttributeError:
      oldMAC = None

    newMAC = request.POST.get('mac').lower()
    pattern = re.compile(r'^[0-9a-f]{2}(:[0-9a-f]{2}){5}$')
    match = pattern.match(newMAC)
    if(not match):
      errors.append("No valid MAC is supplied")
    elif(oldMAC != newMAC):
      change = True
      context['lease'].MAC = newMAC
      try:
        lease = Lease.objects.get(MAC=newMAC)
        errors.append("The MAC is already registerd on %s" % lease)
      except Lease.DoesNotExist:
        pass

    if(len(errors) > 0):
      context['message'] = "ERROR: %s" % " and ".join(errors) 
    else:
      if(context['lease'].id):
        if newMAC != oldMAC:
          context['lease'].MAC = newMAC
        if str(ip) != context['lease'].IP:
          context['lease'].IP = str(ip)
        context['lease'].subnet = subnet
        context['lease'].save()
      else:
        context['lease'] = subnet.createLease(newMAC, ip)

      if newName != oldName:
        context['interface'].name = newName
      if newIFName != oldIFName:
        context['interface'].ifname = newIFName
      if ipv6Text != context['interface'].ipv6:
        context['interface'].ipv6 = ipv6Text
      if context['interface'].host != host:
        context['interface'].host = host
      if context['interface'].ipv4Lease != context['lease']:
        context['interface'].ipv4Lease = context['lease']
      context['interface'].save()

      host.updateDNS()
      dhcpservers = Servers()
      dhcpservers.configureLease(context['lease'].IP, context['lease'].MAC, 
          context['lease'].present, "%s.%s" % (newName, host))
      return redirect('singleHost', host.id)

  return render(request, 'hostInterface.html', context)

def preseed(request, id):
  context = {} 

  context['host'] = get_object_or_404(Host, pk=id)
  key, context['dashboardURL'] = parser.items("hosts")[0]
  context['diskname'] = '/dev/sda'

  auth = authorize(request, context['host'])
  if auth == NONE:
    return HttpResponseForbidden()

  if auth == IP:
    context['host'].status = Host.INSTALLING
    context['host'].save()

  return render(request, 'preseed/default.cfg', context)

def tftp(request, id):
  context = {} 

  key, context['dashboardURL'] = parser.items("hosts")[0]
  context['host'] = get_object_or_404(Host, pk=id)

  if not authorize(request, context['host']):
    return HttpResponseForbidden()

  if(int(host.status) == Host.PROVISIONING):
    template = 'tftpboot/install.cfg'
  else:
    template = 'tftpboot/localboot.cfg'

  return render(request, template, context)

def postinstall(request, id):
  context = {} 

  context['host'] = get_object_or_404(Host, pk=id)

  auth = authorize(request, context['host'])
  if auth == NONE:
    return HttpResponseForbidden()

  if auth == IP:
    context['host'].status = Host.PUPPETSIGN
    context['host'].save()

  return render(request, 'postinstall/postinstall.sh', context)
