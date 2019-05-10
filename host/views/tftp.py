from django.contrib.auth.decorators import user_passes_test 
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from dashboard.utils import requireSuperuser
from host.models import BootFile, BootFragment, BootFileFragment

@user_passes_test(requireSuperuser)
def bootfile(request, id):
  f = get_object_or_404(BootFile, pk=int(id)) 
  return HttpResponse(f.getContent()) 
