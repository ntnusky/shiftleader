#!/usr/bin/python3

import os
import sys
from configparser import ConfigParser

from clientlib import sendUpdate

def getEnvironments(path = "/etc/puppetlabs/code/environments/"):
  environments = {}
  content = os.listdir(path)
  env = [e for e in content if not os.path.isfile(os.path.join(path, e))]
  levelInPath = len(path.rstrip('/').split('/'))

  for environment in env:
    environments[environment] = {'roles': []}
    for current, dirs, files in os.walk(os.path.join(path, environment, 
          "modules/role/manifests")):
      for f in files:
        dirnames = current.split('/')[levelInPath+4:]
        classname = f.replace('.pp', '')
        dirnames.append(classname)
        fullname = "::".join(dirnames) 
        environments[environment]['roles'].append(fullname)

  return environments

if __name__ == '__main__':
  if(len(sys.argv) < 2):
    print("Usage: %s <configfile>")
    sys.exit(1)

  parser = ConfigParser()
  parser.read([sys.argv[1]])

  data = {}
  data['environments'] = getEnvironments()
  
  server = parser.get('general', 'api')
  response = sendUpdate(server, "puppet/update", data)
  if(response and len(response['changes'])):
    print("Puppet environments updated")
    print("The server reports the following changes:")
    for change in response['changes']:
      print(" - %s" % change)
