from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponseBadRequest 
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
      context['record'] = StaticRecord.objects.get(pk=id, active=True)
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

    context['record'].save()
    context['record'].configure()
    return redirect('dnsIndex')

  return render(request, "dnsForm.html", context)


@user_passes_test(requireSuperuser)
def table(request):
  context = {}
  context['records'] = StaticRecord.objects.filter(active=True).all()
  return render(request, "ajax/dnsTable.html", context)

@user_passes_test(requireSuperuser)
def delete(request, id):
  try:
    record = StaticRecord.objects.get(pk=id, active=True)
  except StaticRecord.DoesNotExist:
    return JsonResponse({'status': 'danger', 'message':'Record does not exist'})

  record.deactivate()
  return JsonResponse({'status': 'success', 'message':'%s is deleted' % record})
