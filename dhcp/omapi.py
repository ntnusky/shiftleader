from configparser import NoOptionError
from pypureomapi import Omapi, OmapiErrorNotFound

from dashboard.settings import parser

class OMAPIException(Exception):
  pass

class Servers:
  NO_CHANGE = 0
  CREATED = 1
  DELETED = 2
  UPDATED = 4

  def __init__(self):
    self.servers = []

    try:
      servers = parser.get('DHCP-SERVERS', 'servers').split(',')
    except NoOptionError:
      raise OMAPIException('Cannot retrieve DHCP servers from configfile')

    for server in servers:
      try:
        host = parser.get('DHCP-SERVERS', '%sHost' % server)
        port = parser.get('DHCP-SERVERS', '%sPort' % server)
        keyname = parser.get('DHCP-SERVERS', '%sKeyname' % server)
        key = parser.get('DHCP-SERVERS', '%sKey' % server)
      except NoOptionError:
        raise OMAPIException('The server %s is missing a parameter.' % server)

      s = Server(host, port, keyname, key)
      if s.active:
        self.servers.append(s)

  def configureLease(self, ip, mac, present=True, hostname=None):
    status = 0
    for server in self.servers:
      status = status | server.configureLease(ip, mac, present, hostname)
    return status

  def status(self):
    return "%d servers." % len(self.servers)

class Server:
  def __init__(self, host, port, keyname, key):
    self.host = host
    self.port = port
    self.keyname = keyname
    self.key = key
    
    try:
      self.connection = Omapi(self.host, int(self.port), 
          self.keyname.encode('utf-8'), self.key)
      self.active = True
    except OmapiErrorNotFound:
      self.active = False
      raise OMAPIException('Could not connect to OMAPI')
    except OSError:
      self.active = False

  def getLease(self, mac):
    try:
      ip = self.connection.lookup_ip(mac)
      return ip
    except OmapiErrorNotFound:
      pass

    try:
      ip = self.connection.lookup_ip_host(mac)
      return ip
    except OmapiErrorNotFound:
      pass

    return None

  def addLease(self, ip, mac, hostname=None):
    if hostname:
      self.connection.add_host_supersede_name(ip, mac, hostname)
    else:
      self.connection.add_host(ip, mac)

  def deleteLease(self, mac):
    self.connection.del_host(mac)

  def configureLease(self, ip, mac, present=True, hostname=None):
    try:
      currentIP = self.getLease(mac)

      # If the lease exists, but contains wrong IP, recreate it.
      if(present and currentIP and currentIP != ip):
        self.deleteLease(mac)
        self.addLease(ip, mac, hostname)
        return Servers.UPDATED

      # If lease does not already exist, but should exist, create it.
      elif(present and not currentIP):
        self.addLease(ip, mac, hostname)
        return Servers.CREATED

      # If lease exists and should not, delete it
      elif(not present and currentIP and currentIP == ip):
        self.deleteLease(mac)
        return Servers.DELETED
    except OSError:
      pass

    return Servers.NO_CHANGE
