from http import HTTPStatus
import ipaddress
import logging

from django.http import HttpResponseBadRequest, JsonResponse, QueryDict

from nameserver.models import CName, Domain, Forward, Record, Reverse

logger = logging.getLogger(__name__)

def processForm(request):
  # Determine domain:
  if(request.POST['type'] == 'PTR'):
    ip = ipaddress.ip_address(request.POST['ip'])

    if(ip.version == 4):
      domainname = '.'.join(ip.reverse_pointer.split('.')[1:])
      hostname = ip.reverse_pointer.split('.')[0]
    elif(ip.version == 6):
      domainname = ip.reverse_pointer[32:]
      hostname = ip.reverse_pointer[0:31]
  else:
    domainname = request.POST['domain']
    hostname = request.POST['host']

  try:
    domain = Domain.objects.get(name=domainname)
  except:
    return JsonResponse({
      'message': 'Could not find the domain "%s"' % domainname,
    }, status=HTTPStatus.PRECONDITION_REQUIRED.value)

  if(request.POST['type'] == 'Forward'):
    if(Forward.objects.filter(name=hostname, domain=domain).count()):
      return JsonResponse({
        'message': 'Record already present with the name "%s.%s"' % (
            hostname, domain.name),
      }, status=HTTPStatus.CONFLICT.value)
    else:
      try:
        ipv4 = str(ipaddress.IPv4Address(request.POST['ipv4']))
      except:
        ipv4 = None

      try:
        ipv6 = str(ipaddress.IPv6Address(request.POST['ipv6']))
      except:
        ipv6 = None

      if(not ipv4 and not ipv6):
        return JsonResponse({
          'message': 'An IP-address must be supplied to create a record' % (
              hostname, domain.name),
        }, status=HTTPStatus.BAD_REQUEST.value)
      else:
        try:
          record = Forward(name=hostname, domain=domain, reverse=True,
                          record_type=Record.TYPE_MANUAL, ipv4=ipv4, ipv6=ipv6)
          record.save()
          record.configure()
          return JsonResponse({'message': 'Record is created'})
        except Exception as e:
          logger.error("Could not create forward-record.")
          logger.exception(e)
          return JsonResponse({
            'message': "Could not create record. Check logs" 
          }, status=HTTPStatus.BAD_REQUEST.value)

  elif(request.POST['type'] in ['CNAME', 'PTR']):
    if('target' in request.POST and len(request.POST['target'])):
      target = request.POST['target']
    else:
      return JsonResponse({
        'message': 'A target must be supplied to create a record',
      }, status=HTTPStatus.BAD_REQUEST.value)

    if(request.POST['type'] == 'CNAME'):
      OBJ = CName
    elif (request.POST['type'] == 'PTR'): 
      OBJ = Reverse

    if(OBJ.objects.filter(name=hostname, domain=domain).count()):
      return JsonResponse({
        'message': 'Record already present with the name "%s.%s"' % (
            hostname, domain.name),
      }, status=HTTPStatus.CONFLICT.value)
    else:
      try:
        record = OBJ(name=hostname, domain=domain,
                        record_type=Record.TYPE_MANUAL, target=target)
        record.save()
        record.configure()
        return JsonResponse({'message': 'Record is created'})
      except Exception as e:
        logger.error("Could not create record.")
        logger.exception(e)
        return JsonResponse({
          'message': "Could not create record. Check logs" 
        }, status=HTTPStatus.BAD_REQUEST.value)
  else:
    return HttpResponseBadRequest() 
