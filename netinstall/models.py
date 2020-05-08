from django.db import models

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
