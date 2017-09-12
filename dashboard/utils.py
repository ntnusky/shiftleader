from django.core.urlresolvers import reverse

def populateMenu(request):
  menu = []
  
  m = {}
  m['name'] = 'Home' 
  m['url'] = reverse('index')
  m['active'] = request.path == m['url']
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
  return context

def requireSuperuser(user):
    return user.is_superuser
