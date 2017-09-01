#!/usr/bin/python3

import json
import urllib.request
import urllib.error

def sendUpdate(host, path, data):
  url = "%s/%s" % (host, path)

  headers = {'content-type': 'application/json'}
  params = json.dumps(data).encode('utf-8')
  req = urllib.request.Request(url, data=params, headers=headers)

  try:
    response = urllib.request.urlopen(req)
  except urllib.error.HTTPError:
    return None;

  jsonData = json.loads(response.read().decode('utf-8'))
  return jsonData
