import ipaddress
import os
import re

from django.contrib.auth.decorators import user_passes_test 
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseServerError
from django.shortcuts import render, redirect, get_object_or_404

from dashboard.utils import createEUI64, createContext, requireSuperuser, get_client_ip
from dashboard.settings import parser
from dhcp.models import Subnet, Lease
from dhcp.omapi import Servers
from host.models import Host, Interface, PartitionScheme, OperatingSystem, \
                        BootFile
from host.utils import authorize, createReplacements, NONE, IP, USER
from nameserver.models import Domain
from puppet.models import Environment, Report

@user_passes_test(requireSuperuser)
def index(request):
  context = createContext(request)

  context['header'] = "Host status"
  context['hosts'] = Host.objects.all()
  context['environments'] = Environment.objects.all()
  context['partitionschemes'] = PartitionScheme.objects.all()
  context['operatingsystems'] = OperatingSystem.objects.all()
  context['bootfiles'] = BootFile.objects.all()

  return render(request, 'hostOverview.html', context)

@user_passes_test(requireSuperuser)
def single(request, id, logid = 0):
  context = createContext(request)

  context['host'] = get_object_or_404(Host, pk=id)
  context['header'] = "%s.%s" % (context['host'].name,
      context['host'].getDomain().name)
  context['reports'] = context['host'].report_set.order_by('-time').all()[:40]
  context['partitionSchemes'] = PartitionScheme.objects.all()
  if(logid == 0):
    context['report'] = context['host'].report_set.order_by('-time').first()
    context['reporttype'] = "Last report"
  else:
    context['report'] = get_object_or_404(Report, pk=logid,
        host=context['host'])
    context['reporttype'] = "Puppetrun at %s" % context['report'].time
  if(context['report']):
    context['metrics'] = context['report'].getMetrics()

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
  
  context['subnets'] = Subnet.objects.filter(ipversion=4).all()

  if(request.POST.get('csrfmiddlewaretoken')):
    errors = []

    # Retrieve subnet, and verify IP if it is supplied
    subnetname = request.POST.get('subnet')
    match = re.match(r'\'([a-zA-Z0-9]+)\'', subnetname)
    subnet = Subnet.objects.get(name=match.group(1), ipversion=4)
    
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
    pattern = re.compile(r'^.*([0-9a-f]{2}(:[0-9a-f]{2}){5}).*$')
    match = pattern.match(newMAC)
    if(match):
      newMAC = match.group(1)
    else:
      errors.append("No valid MAC is supplied")

    if(match and oldMAC != newMAC):
      change = True
      context['lease'].MAC = newMAC
      try:
        lease = Lease.objects.get(MAC=newMAC, present=True)
        errors.append("The MAC is already registerd on %s" % lease)
      except Lease.DoesNotExist:
        pass

    ipv6Text = request.POST.get('ipv6')
    if(len(ipv6Text) > 0 and ipv6Text != context['interface'].ipv6):
      if(re.match(r'[eE][uU][iI]-?6?4?', ipv6Text)):
        v6subnet = subnet.v4network.get().v6subnet.getSubnet()
        ipv6Text = str(createEUI64(v6subnet, context['lease'].MAC))

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
    elif(len(ipv6Text) == 0):
      context['interface'].ipv6 = None
      ipv6Text = None
    

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

      if newIFName != oldIFName:
        context['interface'].ifname = newIFName
      if ipv6Text != context['interface'].ipv6:
        context['interface'].ipv6 = ipv6Text
      if context['interface'].host != host:
        context['interface'].host = host
      if context['interface'].ipv4Lease != context['lease']:
        context['interface'].ipv4Lease = context['lease']
      network = subnet.v4network.get()
      if context['interface'].network != network:
        context['interface'].network = network
      context['interface'].save()

      host.updateDNS()
      dhcpservers = Servers()

      if(context['interface'].primary):
        hostname = str(host)
      else:
        hostname = None

      dhcpservers.configureLease(context['lease'].IP, context['lease'].MAC, 
          context['lease'].present)
      return redirect('singleHost', host.id)

  return render(request, 'hostInterface.html', context)

@user_passes_test(requireSuperuser)
def bootfiles(request):
  context = createContext(request)
  context['header'] = "Bootfiles"
  
  return render(request, 'host/bootfiles.html', context)

def preseed(request, id):
  host = get_object_or_404(Host, pk=id)
  data = createReplacements(host)

  auth = authorize(request, host)
  if auth == NONE:
    return HttpResponseForbidden()

  if auth == IP:
    host.status = Host.INSTALLING
    host.save()
  
  try:
    return HttpResponse(host.bootfile.getContent(data)) 
  except:
    raise Http404

def tftp(request, id):
  context = {} 

  context['dashboardURL'] = None
  for key, item in parser.items("hosts"):
    if(key == 'ipv4' or (context['dashboardURL'] == None and key == 'main')):
      context['dashboardURL'] = item
  context['host'] = get_object_or_404(Host, pk=id)

  if not authorize(request, context['host']):
    return HttpResponseForbidden()

  if(int(context['host'].status) == Host.PROVISIONING and context['host'].os):
    template = 'tftpboot/install.cfg'
  else:
    template = 'tftpboot/localboot.cfg'

  return render(request, template, context)

def postinstall(request, id):
  host = get_object_or_404(Host, pk=id)
  data = createReplacements(host)

  auth = authorize(request, host)

  if auth == NONE:
    return HttpResponseForbidden()

  if auth == IP:
    host.status = Host.PUPPETSIGN
    host.save()

  try:
    return HttpResponse(host.postinstallscript.getContent(data)) 
  except:
    raise Http404

@user_passes_test(requireSuperuser)
def osform(request, pid=0):
  context = createContext(request)

  if(pid == 0):
    opsys = None
    context['header'] = "Add an OS"
    context['buttonText'] = "Add"
  else:
    opsys = get_object_or_404(OperatingSystem, pk=pid)
    context['os'] = opsys
    context['header'] = "Update '%s'" % opsys.name
    context['buttonText'] = "Update"
  
  if(request.POST.get('csrfmiddlewaretoken')):
    if(opsys == None):
      opsys = OperatingSystem()
    
    toSave = False
    if(opsys.name != request.POST.get('name')):
      opsys.name = request.POST.get('name')
      toSave = True
    if(opsys.shortname != request.POST.get('shortname')):
      opsys.shortname = request.POST.get('shortname')
      toSave = True
    if(opsys.kernelurl != request.POST.get('kernelurl')):
      opsys.kernelurl = request.POST.get('kernelurl')
      opsys.kernelname = os.path.basename(opsys.kernelurl)
      toSave = True
    if(opsys.initrdurl != request.POST.get('initrdurl')):
      opsys.initrdurl = request.POST.get('initrdurl')
      opsys.initrdname = os.path.basename(opsys.initrdurl)
      toSave = True

    if(len(opsys.name) == 0 or len(opsys.shortname) == 0 or
        len(opsys.kernelurl) == 0 or len(opsys.initrdurl) == 0):
      context['message'] = "All fields need a value!"
      toSave = False

    if(toSave):
      opsys.save()
      return redirect('hostIndex')

  return render(request, 'hostOsForm.html', context)

@user_passes_test(requireSuperuser)
def pform(request, pid=0):
  context = createContext(request)

  if(pid == 0):
    scheme = None
    context['header'] = "Create a new partitioning-scheme"
    context['buttonText'] = "Create new scheme"
  else:
    scheme = get_object_or_404(PartitionScheme, pk=pid)
    context['partitionscheme'] = scheme
    context['header'] = "Update the scheme %s" % scheme.name
    context['buttonText'] = "Update scheme"

  if(request.POST.get('csrfmiddlewaretoken')):
    if(scheme == None):
      scheme = PartitionScheme()

    toSave = False
    if(scheme.name != request.POST.get('name')):
      scheme.name = request.POST.get('name')
      toSave = True
    if(scheme.description != request.POST.get('description')):
      scheme.description = request.POST.get('description')
      toSave = True
    if(scheme.content != request.POST.get('scheme')):
      scheme.content = request.POST.get('scheme')
      toSave = True

    if(len(scheme.name) == 0 or len(scheme.content) ==0):
      context['message'] = "You need to fill in name and scheme!"
      toSave = False

    if(toSave):
      scheme.save()
      return redirect('hostIndex')
  return render(request, 'hostPartitionForm.html', context)

def list(request):
  context = {}
  context['hosts'] = Host.objects.all()
  return render(request, 'hostList.html', context)
