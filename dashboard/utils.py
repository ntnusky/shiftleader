from django.core.urlresolvers import reverse

from dashboard.settings import parser

def populateMenu(request):
  menu = []
  
  m = {}
  m['name'] = 'Home' 
  m['url'] = reverse('index')
  m['active'] = request.path == m['url']
  menu.append(m)

  m = {}
  m['name'] = 'Hosts' 
  m['url'] = reverse('hostIndex')
  m['active'] = request.path.startswith(m['url'])
  menu.append(m)

  m = {}
  m['name'] = 'DNS' 
  m['url'] = reverse('dnsIndex')
  m['active'] = request.path == m['url']
  menu.append(m)

  m = {}
  m['name'] = 'DHCP' 
  m['url'] = reverse('dhcpIndex')
  m['active'] = request.path == m['url']
  menu.append(m)

  m = {}
  m['name'] = 'Puppet' 
  m['url'] = reverse('puppetIndex')
  m['active'] = request.path == m['url']
  menu.append(m)

  m = {}
  m['name'] = 'Log out' 
  m['url'] = reverse('logout')
  m['active'] = False
  menu.append(m)

  return menu

def createContext(request):
  context = {}
  context['menu'] = populateMenu(request)

  try:
    context['env'] = parser.get("general", "env")
  except:
    pass

  return context

def requireSuperuser(user):
    return user.is_superuser

def get_client_ip(request):
  x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
  if x_forwarded_for:
    ip = x_forwarded_for.split(',')[-1]
  else:
    ip = request.META.get('REMOTE_ADDR')
  return ip
