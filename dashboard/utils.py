import ipaddress
import re

from django.core.urlresolvers import reverse

from dashboard.settings import parser

def populateMenu(request):
  menu = []
  
  m = {}
  m['name'] = 'Hosts' 
  m['url'] = reverse('hostIndex')
  m['active'] = request.path.startswith(m['url'])
  m['type'] = 'link'
  menu.append(m)

  m = {}
  m['name'] = 'Boot-config'
  m['type'] = 'dropdown'
  m['elements'] = []
  
  me = {}
  me['name'] = 'Config-files' 
  me['url'] = reverse('netinstall_file')
  me['type'] = 'link'
  me['active'] = request.path.startswith(me['url'])
  m['elements'].append(me)

  me = {}
  me['name'] = 'Boot-Templates' 
  me['url'] = reverse('netinstall_template')
  me['type'] = 'link'
  me['active'] = request.path.startswith(me['url'])
  m['elements'].append(me)

  m['active'] = False
  for e in m['elements']:
    if e['active']:
      m['active'] = True

  menu.append(m)

  m = {}
  m['name'] = 'DNS' 
  m['url'] = reverse('dnsIndex')
  m['active'] = request.path == m['url']
  m['type'] = 'link'
  menu.append(m)

  m = {}
  m['name'] = 'DHCP' 
  m['url'] = reverse('dhcpIndex')
  m['active'] = request.path == m['url']
  m['type'] = 'link'
  menu.append(m)

  m = {}
  m['name'] = 'Puppet' 
  m['url'] = reverse('puppetIndex')
  m['active'] = request.path == m['url']
  m['type'] = 'link'
  menu.append(m)

  m = {}
  m['name'] = 'Log out' 
  m['url'] = reverse('logout')
  m['active'] = False
  m['type'] = 'link'
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

def createEUI64(v6net, mac):
  mac = mac.lower()
  network = ipaddress.IPv6Network(v6net)
  netid = int(network.network_address)
  hostid = 0

  match = re.match(r'(([0-9a-f]{2}:){5}[0-9a-f]{2})', mac)
  if match:
    octets = match.group(0).split(':')
    octetid = 7
    for octet in octets:
      hostid += int(octet, 16) << (octetid*8)
      octetid -= 1
      if(octetid == 4):
        hostid += int('FF', 16) << (4*8)
        hostid += int('FE', 16) << (3*8)
        octetid = 2

    hostid = hostid ^ 1 << 57
        
    return ipaddress.IPv6Address(netid+hostid)
  else:
    return False
