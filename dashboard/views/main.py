from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test 
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError

from dashboard.utils import createContext, requireSuperuser

@user_passes_test(requireSuperuser)
def index(request):
  return redirect(reverse('hostMain'))

def loginPage(request):
  context = {}

  try:
    context['next'] = request.GET['next']
  except MultiValueDictKeyError:
    context['next'] = None

  if('username' in request.POST):
    user = authenticate(username=request.POST['username'],
        password=request.POST['password'])

    if(user is not None and user.is_superuser):
      login(request, user)
      if(context['next']):
        return redirect(context['next'])
      else:
        return redirect(reverse('index'))
    elif(user is not None):
      context['message'] = \
          "I'm sorry %s, It seems like you have no access here." \
          % user.first_name
    else:
      context['message'] = "Your credentials are not valid."

  return render(request, 'login.html', context) 

@user_passes_test(requireSuperuser)
def logoutPage(request):
  logout(request)
  return redirect(reverse('login'))
