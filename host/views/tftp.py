from django.contrib.auth.decorators import user_passes_test 
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from dashboard.utils import requireSuperuser
from host.models import BootFile, BootFragment, BootFileFragment
from netinstall.models import OperatingSystem

@user_passes_test(requireSuperuser)
def bootfile(request, id):
  f = get_object_or_404(BootFile, pk=int(id)) 
  return HttpResponse(f.getContent()) 

def kernels(request):
  response = {}

  for os in OperatingSystem.objects.all():
    response[os.shortname] = {
      'kernel': os.kernelurl,
      'initrd': os.initrdurl,
    }
  
  return JsonResponse(response)
