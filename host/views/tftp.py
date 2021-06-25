from django.http import JsonResponse

from netinstall.models import OperatingSystem

def kernels(request):
  response = {}

  for os in OperatingSystem.objects.all():
    response[os.shortname] = {
      'kernel': os.kernelurl,
      'initrd': os.initrdurl,
    }
  
  return JsonResponse(response)
