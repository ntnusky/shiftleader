import re

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponseBadRequest 
from django.utils import dateparse
from django.shortcuts import render, redirect

from django.utils.datastructures import MultiValueDictKeyError

from dashboard.utils import createContext, requireSuperuser
from nameserver.models import Domain, Server, StaticRecord

@user_passes_test(requireSuperuser)
def index(request):
  context = createContext(request)
  context['header'] = "DNS status"
  context['servers'] = Server.objects.all()
  context['domains'] = Domain.objects.all()

  return render(request, "dnsStatus.html", context)

@user_passes_test(requireSuperuser)
def form(request, id=0):
  context = createContext(request)
  context['domains'] = []

  for domain in Domain.objects.all():
    if('in-addr.arpa' in domain.name):
      continue
    if('ip6.arpa' in domain.name):
      continue
    context['domains'].append(domain)

  if(id):
    context['header'] = "Edit static DNS record"
    context['buttonText'] = "Update record"
    try:
      context['record'] = StaticRecord.objects.get(pk=id)
    except StaticRecord.DoesNotExist:
      return HttpResponseBadRequest()
  else:
    context['header'] = "Create static DNS record"
    context['buttonText'] = "Create record"
    context['record'] = None

  if('csrfmiddlewaretoken' in request.POST):
    try:
      domain = Domain.objects.get(name=request.POST['domain'])
    except Domain.DoesNotExist:
      return HttpResponseBadRequest()

    if(not context['record']):
      try:
        context['record'] = StaticRecord.objects.get(active=False,
            name=request.POST['name'], domain=domain)
      except StaticRecord.DoesNotExist:
        context['record'] = StaticRecord()
    context['record'].domain = domain

    try:
      context['record'].name = request.POST['name']
      context['record'].ipv4 = request.POST['ipv4']
      context['record'].ipv6 = request.POST['ipv6']
      context['record'].expire = request.POST['expire']
    except MultiValueDictKeyError:
      return HttpResponseBadRequest()

    try:
      sr = StaticRecord.objects.get(name=request.POST['name'], domain=domain)
      if(sr.id != context['record'].id):
        context['message'] = "Name is already in use"
        context['status'] = "warning"
        return render(request, "dnsForm.html", context)
    except StaticRecord.DoesNotExist:
      pass

    if(len(context['record'].ipv4) == 0):
      context['record'].ipv4 = None
    if(len(context['record'].ipv6) == 0):
      context['record'].ipv6 = None

    m = re.match(r'([0123]?[0-9])[\.\ \-]?([01]?[0-9])[\.\ \-]?(20[0-9]{2})', 
            request.POST['expire'])

    if len(request.POST['expire']) == 0:
      context['record'].expire = None
    elif not m:
      context['message'] = "The date is invalid"
      context['status'] = "warning"
      return render(request, "dnsForm.html", context)
    else:
      context['record'].expire = dateparse.parse_date(
          "%s-%s-%s" % (m.group(3), m.group(2), m.group(1))
      )
    
    context['record'].save()
    context['record'].configure()
    return redirect('dnsIndex')

  return render(request, "dnsForm.html", context)


@user_passes_test(requireSuperuser)
def table(request):
  context = {}
  context['domains'] = []
  
  for d in Domain.objects.all():
    records = StaticRecord.objects.filter(domain=d)
    if(records.count() > 0):
      context['domains'].append({'name':d.name, 'records': records.all()})

  return render(request, "ajax/dnsTable.html", context)

@user_passes_test(requireSuperuser)
def activate(request, id):
  try:
    record = StaticRecord.objects.get(pk=id)
  except StaticRecord.DoesNotExist:
    return JsonResponse({'status': 'danger', 'message':'Record does not exist'})

  record.activate()
  return JsonResponse({'status': 'success', 'message':'%s is activated' % record})

@user_passes_test(requireSuperuser)
def deactivate(request, id):
  try:
    record = StaticRecord.objects.get(pk=id)
  except StaticRecord.DoesNotExist:
    return JsonResponse({'status': 'danger', 'message':'Record does not exist'})

  record.deactivate()
  return JsonResponse({'status': 'success', 'message':'%s is deactivated' % record})

@user_passes_test(requireSuperuser)
def delete(request, id):
  try:
    record = StaticRecord.objects.get(pk=id)
  except StaticRecord.DoesNotExist:
    return JsonResponse({'status': 'danger', 'message':'Record does not exist'})

  record.deactivate()
  record.delete()
  return JsonResponse({'status': 'success', 'message':'%s is deleted' % record})
