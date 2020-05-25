import re

from django.core.urlresolvers import reverse
from django.db import models

from dashboard.settings import parser

class BootTemplate(models.Model):
  name          = models.CharField(max_length=64)
  description   = models.TextField()

  tftpconfig    = models.ForeignKey('ConfigFile', null=True,
                                      related_name='bt_tftp', 
                                      on_delete=models.SET_NULL)
  installconfig = models.ForeignKey('ConfigFile', null=True, 
                                      related_name='bt_inst',
                                      on_delete=models.SET_NULL)
  postinstall   = models.ForeignKey('ConfigFile', null=True, 
                                      related_name='bt_postinst',
                                      on_delete=models.SET_NULL)
  os            = models.ForeignKey('OperatingSystem', null=True,
                                      on_delete=models.SET_NULL)
  
  def __str__(self):
    return "%s" % self.name

  def toJSON(self):
    json = {
      'id': self.id,
      'name': self.name,
      'description': self.description,
    }

    if self.tftpconfig:
      json['tftpconfig'] = self.tftpconfig.toJSON()
    else:
      json['tftpconfig'] = None

    if self.installconfig:
      json['installconfig'] = self.installconfig.toJSON()
    else:
      json['installconfig'] = None

    if self.postinstall:
      json['postinstall'] = self.postinstall.toJSON()
    else:
      json['postinstall'] = None

    if self.os:
      json['os'] = self.os.toJSON()
    else:
      json['os'] = None

    return json

  class Meta:
    ordering = ['name']

class ConfigFile(models.Model):
  name = models.CharField(max_length=64)
  description = models.TextField()
  content = models.TextField(null=True)
  
  filetype = models.ForeignKey('ConfigFileType', null=True,
                                on_delete=models.SET_NULL)
  
  def __str__(self):
    return "%s" % self.name

  def toJSON(self):
    json = {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'content': self.content,
    }

    if self.filetype:
      json['filetype'] = self.filetype.toJSON()
    else:
      json['filetype'] = None

    return json

  def getContent(self, host = None):
    content = []

    substitutions = {
      'PUPPETSERVER': parser.get('puppet', 'server'),
      'PUPPETCA': parser.get('puppet', 'caserver'),
    }

    dashboard = None
    for key, item in parser.items("hosts"):
      if(key == 'ipv4' or (dashboard == None and key == 'main')):
        dashboard = item

    if(dashboard):
      substitutions['DASHBOARD'] = dashboard

    if(host):
      substitutions['HOSTID'] = str(host.id)
      substitutions['HOSTNAME'] = host.name
      substitutions['ROOTPW'] = host.password
      substitutions['POSTINSTALL'] = "%s%s" % (
        parser.get('general', 'api'),
        reverse('host_api_postinstall', args=[host.id]),
      )
      substitutions['INSTALLCONFIG'] = "%s%s" % (
        parser.get('general', 'api'),
        reverse('host_api_installerconfig', args=[host.id]),
      )

      if(host.getPrimaryIf()):
        substitutions['INTERFACENAME'] = host.getPrimaryIf().ifname

      if(host.template and host.template.os):
        substitutions['OSSHORTNAME'] = host.template.os.shortname
        substitutions['OSKERNELNAME'] = host.template.os.kernelname
        substitutions['OSINITRDNAME'] = host.template.os.initrdname

    filereplace = re.compile(r'^%FILE:([0-9]+)%$')

    for line in self.content.splitlines():
      replace = filereplace.match(line)
      if(replace):
        try:
          included = ConfigFile.objects.get(id=replace.group(1))
          content.append(included.getContent(host))
        except ConfigFile.DoesNotExist:
          content.append(line)
      else:
        for key in substitutions:
          line = line.replace('%%%s%%' % key, substitutions[key])
        content.append(line)

    return '\n'.join(content);

  class Meta:
    ordering = ['filetype__name', 'name']

class ConfigFileType(models.Model):
  name = models.CharField(max_length=64)
  
  def __str__(self):
    return "%s" % self.name

  def toJSON(self):
    json = {
      'id': self.id,
      'name': self.name,
    }
    return json

  class Meta:
    ordering = ['name']

class OperatingSystem(models.Model):
  name = models.CharField(max_length=64)
  shortname = models.CharField(max_length=20)

  kernelname = models.CharField(max_length=64)
  kernelurl = models.CharField(max_length=256)
  kernelsum = models.CharField(max_length=130, default=None, null=True)

  initrdname = models.CharField(max_length=64)
  initrdurl = models.CharField(max_length=256)
  initrdsum = models.CharField(max_length=130, default=None, null=True)
  
  def __str__(self):
    return "%s (%s)" % (self.name, self.shortname)

  def toJSON(self):
    json = {
      'id': self.id,
      'name': self.name,
      'shortname': self.shortname,
      'kernelurl': self.kernelurl,
      'kernelname': self.kernelname,
      'kernelsum': self.kernelsum,
      'initrdurl': self.initrdurl,
      'initrdname': self.initrdname,
      'initrdsum': self.initrdsum,
    }
    return json

  class Meta:
    ordering = ['name']
