import ipaddress
import re

from http import HTTPStatus

from django.contrib.auth.decorators import user_passes_test 
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError

from dashboard.utils import createEUI64, requireSuperuser, pretty_time

from dhcp.models import Subnet
from dhcp.omapi import Servers
from host.models import Host, Interface, HostGroup
from netinstall.models import BootTemplate
from puppet.models import Environment, Role

@user_passes_test(requireSuperuser)
def main(request):
  if(request.method == 'GET'):
    hosts = []
    for host in Host.objects.all():
      hosts.append(host.toJSON())

    return JsonResponse(hosts, safe=False)
  elif(request.method == 'POST'):
    # If mandatory parameters are empty, or missing, return an error
    try:
      if(request.POST['hostname'] == '' or request.POST['ifname'] == ''):
        raise Exception()
    except:
      return JsonResponse({
        'message': 'Missing hostname or ifname.'
      }, status=HTTPStatus.BAD_REQUEST.value) 

    # Make sure the hostname is unique
    if(Host.objects.filter(name=request.POST['hostname']).count()):
      return JsonResponse({
        'message': 'There already exist a host with the name %s.' %
            request.POST['hostname']
      }, status=HTTPStatus.BAD_REQUEST.value) 

    # Retrieve the selected role (and env):
    try:
      role = Role.objects.get(pk=request.POST['role'])
      environment = role.environment
    except (Role.DoesNotExist, MultiValueDictKeyError):
      role = None
      try:
        environment = Environment.objects.get(pk=request.POST['environment'])
      except (Environment.DoesNotExist, MultiValueDictKeyError):
        environment = None

    # If the host is of the internal type, make sure it has the parameters
    # 'subnet', 'mac-address' and 'template' set.
    if('hosttype' in request.POST and request.POST['hosttype'] == 'internal'):
      # Try to retrieve template. If template is not set, leave it blank.
      if('template' in request.POST and request.POST['template'] != '0'):
        try:
          template = BootTemplate.objects.get(id=request.POST['template'])
        except BootTemplate.DoesNotExist:
          return JsonResponse({'message': 'Template not found'},
              status=HTTPStatus.BAD_REQUEST.value)
      else:
        template = None

      # Verify that MAC-address is valid:
      pattern = re.compile(r'^[0-9a-f]{2}(:[0-9a-f]{2}){5}$')
      macMatch = pattern.match(request.POST['mac'].lower())
      if macMatch:
        mac = macMatch.group(0)
      else:
        return JsonResponse({'message': 'Invalid MAC-address'},
            status=HTTPStatus.BAD_REQUEST.value)

      # Verify that the mac-address is not already registered.
      try:
        interface = Interface.objects.get(mac=mac)
      except Interface.DoesNotExist:
        pass
      else:
        return JsonResponse({'message': 'MAC-Address already registered'},
            status=HTTPStatus.CONFLICT.value)

      # Retrieve the host subnet.
      try:
        subnet = Subnet.objects.get(pk=request.POST['subnet'])
      except (Subnet.DoesNotExist, MultiValueDictKeyError):
        return JsonResponse({'message': 'Subnet not found'},
            status=HTTPStatus.BAD_REQUEST.value)
      
      # Validate the provided IPv6 address
      if(len(request.POST['ipv6']) > 0):
        v6subnet = subnet.v4network.get().v6subnet.getSubnet()
        if(re.match(r'[eE][uU][iI]-?6?4?', request.POST['ipv6'])):
          ipv6 = createEUI64(v6subnet, mac)
        else:
          try:
            ipv6 = ipaddress.IPv6Address(request.POST['ipv6'])
          except ValueError:
            return JsonResponse({'message': 'Invalid IPv6 Address'},
                status=HTTPStatus.BAD_REQUEST.value)

        if ipv6 not in v6subnet:
          return JsonResponse({'message': 'IPv6-address not in correct subnet'},
              status=HTTPStatus.BAD_REQUEST.value)
      else:
        ipv6 = None

      # Validate the provided IPv4 address:
      if(len(request.POST['ipv4']) > 0):
        try:
          ipv4 = ipaddress.IPv4Address(request.POST['ipv4'])
        except ValueError:
          return JsonResponse({'message': 'Invalid IPv4 Address'},
              status=HTTPStatus.BAD_REQUEST.value)

        if(ipv4 not in subnet.getSubnet()):
          return JsonResponse({'message': 'IPv4-address not in correct subnet'},
              status=HTTPStatus.BAD_REQUEST.value)
        if(ipv4 in subnet.getReservedAddresses()):
          return JsonResponse({'message': 'IPv4-address is reserved'},
              status=HTTPStatus.BAD_REQUEST.value)
        lease = subnet.getLease(str(ipv4)) 
        if(lease):
          return JsonResponse({'message': 'IPv4-address is already in use'},
              status=HTTPStatus.BAD_REQUEST.value)
        ipv4 = str(ipv4)
      else:
        ipv4 = None

      # Create IPv4 Lease for the host
      lease = subnet.createLease(mac, ipv4)
      if not lease:
        return JsonResponse({'message': 'Could not create IPv4-Lease'},
            status=HTTPStatus.INTERNAL_SERVER_ERROR.value)

      if(template):
        hostStatus = Host.PROVISIONING
      else:
        hostStatus = Host.PUPPETSIGN

      host = Host(name=request.POST['hostname'], status = hostStatus,
          environment = environment, role = role,
          template = template)
      host.generatePassword()
      host.save()

      network = subnet.v4network.get()
      interface = Interface(ifname=request.POST['ifname'], mac=mac, host=host,
        primary=True, ipv4Lease=lease, network=network, ipv6=str(ipv6))
      interface.save()

      dhcpservers = Servers()
      dhcpservers.configureLease(lease.IP, lease.MAC, lease.present, str(host))

      host.updateDNS()

      return JsonResponse({
        'message': 'Host is created'
      }, status=HTTPStatus.CREATED.value) 

    # If the host is of the external type, make sure it has the parameters
    # 'domain' and 'ip' set.
    elif('hosttype' in request.POST and request.POST['hosttype'] == 'external'):
      # TODO: Massage data-structure so that we can represent external hosts.
      return JsonResponse({
        'message': 'External hosts are not implemented yet'
      }, status=HTTPStatus.NOT_IMPLEMENTED.value) 
    else:
      return JsonResponse({
        'message': 'Invalid host-type'
      }, status=HTTPStatus.BAD_REQUEST.value) 
  else:
    return JsonResponse({
      'message': 'Method not implemented.'
    }, status=HTTPStatus.BAD_REQUEST.value) 

@user_passes_test(requireSuperuser)
def single(request, id):
  if(request.method == 'GET'):
    host = get_object_or_404(Host, pk=id)
    return JsonResponse(host.toJSON())
  elif(request.method == 'PUT'):
    host = get_object_or_404(Host, pk=id)
    data = QueryDict(request.body)

    try:
      changed = host.updateInfo(data)
    except KeyError as e:
      return JsonResponse({
        'message': str(e), 
      }, status=HTTPStatus.NOT_FOUND.value)
    except AttributeError as e:
      return JsonResponse({
        'message': str(e), 
      }, status=HTTPStatus.BAD_REQUEST.value)
      
    if(changed):
      host.save()
      return JsonResponse({'message': 'Host "%s" is updated.' % host.name})
    else:
      return JsonResponse({'message': 'No changes to "%s".' % host.name})
  elif(request.method == 'DELETE'):
    host = get_object_or_404(Host, pk=id)
    host.remove()
    return JsonResponse({'message': 'Host "%s" is deleted.' % host.name})
  else:
    return JsonResponse({
      'status':'error', 
      'message': 'Method not implemented.'
    }, status=HTTPStatus.BAD_REQUEST.value) 

@user_passes_test(requireSuperuser)
def group(request, id):
  host = get_object_or_404(Host, pk=id)
  
  if(request.method == 'GET'):
    data = host.group.toJSON()

    return JsonResponse(data)
  elif(request.method == 'PUT'):
    data = QueryDict(request.body)
    
    if('group_id' not in data):
      return JsonResponse({
        'message': 'Missing parameter "group_id".',
      }, status=HTTPStatus.BAD_REQUEST.value) 

    if(data['group_id'] == '0'):
      group = None
    else:
      group = get_object_or_404(HostGroup, pk=data['group_id'])

    host.group = group
    host.save()

    if(group):
      msg = 'Moved "%s" to the new host-group "%s"' % (host.name, group.name)
    else:
      msg = 'Removed the host "%s" from its group' % host.name

    return JsonResponse({ 'message': msg, }) 
      
  else:
    return JsonResponse({
      'message': 'Method not implemented.'
    }, status=HTTPStatus.BAD_REQUEST.value) 

@user_passes_test(requireSuperuser)
def puppet(request, id):
  host = get_object_or_404(Host, pk=id)
  if(request.method == 'GET'):
    data = {}

    data['status'] = host.getStatusText()
    data['last_run'] = host.report_set.last().time
    data['last_run_pretty'] = "%s ago" % pretty_time(data['last_run'])

    return JsonResponse(data)
  else:
    return JsonResponse({
      'status':'error', 
      'message': 'Method not implemented.'
    }, status=HTTPStatus.BAD_REQUEST.value) 
