from django.contrib.auth.decorators import user_passes_test 
from django.http import JsonResponse

from dashboard.utils import requireSuperuser
from host.models import BootFile, BootFragment, BootFileFragment

@user_passes_test(requireSuperuser)
def file(request):
  if(request.method == 'GET'):
    files = []
    for f in BootFile.objects.order_by('filetype', 'name').all():
      fragments = []
      for fragment in f.bootfilefragment_set.order_by('fragment__name').all():
        fragments.append(fragment.id)

      files.append({
        'id': f.id,
        'type': f.getType(),
        'typetxt': f.getTypeTxt(),
        'name': f.name,
        'description': f.description,
        'fragments': fragments,
      })
    return JsonResponse({
      'status':'success', 
      'files': files
    }) 
  elif(request.method == 'POST'):
    f = BootFile(
      name = request.POST['name'],
      description = request.POST['description'],
      filetype = request.POST['type']
    )
    f.save()

    i = 10
    try:
      ids = [int(i) for i in request.POST.getlist('fragments')]
      for fragment in BootFragment.objects.filter(id__in = ids).order_by('name').all():
        bff = BootFileFragment(
          bootfile = f,
          fragment = fragment,
          order = i,
        )
        bff.save()
        i += 10;
    except:
      pass

    return JsonResponse({
      'status':'success', 
    }) 
  else:
    return JsonResponse({'status':'error', 'message': 'Bad request'}, status=400) 

@user_passes_test(requireSuperuser)
def singlefile(request, fid):
  try:
    f = BootFile.objects.get(pk=int(fid))
  except:
    return JsonResponse({
      'status':'error', 
      'message': 'file not found'
    }, status=404) 
    
  if(request.method == 'GET'):
    fragments = []
    for fragment in f.bootfilefragment_set.order_by('fragment__name').all():
      fragments.append(fragment.fragment.id)

    return JsonResponse({
      'id': f.id,
      'name': f.name,
      'description': f.description,
      'type': f.getType(),
      'typetxt': f.getTypeTxt(),
      'fragments': fragments,
    })
  elif(request.method == 'POST'):
    f.name = request.POST['name']
    f.description = request.POST['description']
    f.filetype = request.POST['type']
    f.save()
    
    f.bootfilefragment_set.all().delete()

    i = 10
    try:
      ids = [int(i) for i in request.POST.getlist('fragments')]
      for fragment in BootFragment.objects.filter(id__in = ids).order_by('name').all():
        bff = BootFileFragment(
          bootfile = f,
          fragment = fragment,
          order = i,
        )
        bff.save()
        i += 10;
    except:
      pass

    return JsonResponse({
      'status':'success', 
    }) 
  elif(request.method == 'DELETE'):
    f.bootfilefragment_set.all().delete()
    f.delete()
    return JsonResponse({
      'status':'success', 
    }) 
  else:
    return JsonResponse({'status':'error', 'message': 'Bad request'}, status=400) 

@user_passes_test(requireSuperuser)
def fragment(request):
  if(request.method == 'GET'):
    data = []
    for f in BootFragment.objects.all():
      data.append({
        'id': f.id,
        'name': f.name,
        'description': f.description,
        'content': f.content,
      })
    return JsonResponse({
      'status':'success',
      'fragments': data,
    }) 
  elif(request.method == 'POST'):
    fragment = BootFragment()
    fragment.name = request.POST['name']
    fragment.description = request.POST['description']
    fragment.content = request.POST['content']
    fragment.save()
    return JsonResponse({'status':'success'}) 
  else:
    return JsonResponse({'status':'error', 'message': 'Bad request'}, status=400) 

@user_passes_test(requireSuperuser)
def singlefragment(request, fid):
  try:
    f = BootFragment.objects.get(pk=fid)
  except:
    return JsonResponse({
      'status': 'error',
      'message': 'Fragment not found',
    }, status=404)

  if(request.method == 'GET'):
    return JsonResponse({
      'status': 'success',
      'id': f.id,
      'name': f.name,
      'description': f.description,
      'content': f.content,
    })
  elif(request.method == 'POST'):
    f.name = request.POST['name']
    f.description = request.POST['description']
    f.content = request.POST['content']
    f.save()
    return JsonResponse({'status':'success'}) 
  elif(request.method == 'DELETE'):
    f.delete()
    return JsonResponse({'status':'success'}) 
  else:
    return JsonResponse({'status':'error', 'message': 'Bad request'}, status=400) 
