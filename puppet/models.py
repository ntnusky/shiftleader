from datetime import datetime

from django.db import models
from django.utils import timezone

class Environment(models.Model):
  name = models.CharField(max_length=64)
  last_deployed = models.DateTimeField(null=True)

  def __str__(self):
    return "%s (%s)" % (self.name, "Active" if self.is_active else "In-Active")

  def getLatestVersion(self):
    return self.version_set.order_by('-created').first()

  def is_active(self):
    if self.version_set.count() == 0:
      return False

    last_version = self.getLatestVersion()
    last_server_deploy = last_version.server.getLatestVersion()
    
    invalid = last_version.created.timestamp() + 900
    lastServer = last_server_deploy.created.timestamp()
    if lastServer > invalid:
      return False
    
    return True

  class Meta:
    ordering = ['name']

class Server(models.Model):
  STATUSES = (
    ('0', 'Ok'),
    ('1', 'Checkin started'),
    ('2', 'r10k is running'),
    ('3', 'r10k failed'),
    ('4', 'Timeout')
  )

  STATUS_OK = '0'
  STATUS_STARTED = '1'
  STATUS_RUNNING = '2'
  STATUS_ERROR = '3'
  STATUS_TIMEOUT = '4'

  name = models.CharField(max_length=64)
  status = models.CharField(max_length=1, choices=STATUSES)
  last_checkin = models.DateTimeField(null=True)

  def __str__(self):
    return "%s (%s)" % (self.name, self.getStatusText())

  def getStatusText(self):
    invalid = datetime.fromtimestamp(self.last_checkin.timestamp()+360)
    if(timezone.now() > timezone.make_aware(invalid)):
      self.status = self.STATUS_TIMEOUT
      self.save()

    for key, value in self.STATUSES:
      if key == self.status:
        return value
    return None

  def checkin(self, status):
    self.last_checkin = timezone.now()
    self.status = status
    self.save()

  def getLatestVersion(self, env=None):
    if(type(env) == str):
      try:
        environment = Environment.objects.get(name=env)
      except Environment.DoesNotExist: 
        return None
    elif(type(env) == Environment):
      environment = env
    elif(env == None):
      return self.version_set.order_by('-created').first()
    else:
      raise ValueError("This function needs a string or an environment")
    
    return self.version_set.order_by('-created').filter(
        environment=environment).first()

  def getLatestVersions(self):
    versions = []
    for environment in Environment.objects.all():
      if environment.is_active():
        version = self.getLatestVersion(environment)
        if version:
          versions.append(version)
    return versions

  class Meta:
    ordering = ['name']

class Version(models.Model):
  STATUS = (
    ('0', 'Scheduled'),
    ('1', 'Deploying'),
    ('2', 'Deployed'),
    ('3', 'Error'),
  )
  STATUS_SCHEDULED = '0'
  STATUS_DEPLOYING = '1'
  STATUS_DEPLOYED = '2'
  STATUS_ERROR = '3'

  environment = models.ForeignKey(Environment)
  server = models.ForeignKey(Server)
  signature = models.CharField(max_length=64)
  status = models.CharField(max_length=1, choices=STATUS,
      default=STATUS_SCHEDULED)
  created = models.DateTimeField(auto_now_add=True, null=True)
  deployed = models.DateTimeField(auto_now=True, null=True)

  def __str__(self):
    return "%s (rev: %s)" % (self.environment, self.getShortSignature())

  def is_deployable(self):
    return (self.status == self.STATUS_DEPLOYED) or \
        (self.status == self.STATUS_ERROR)

  def getShortSignature(self, length = 7):
    return self.signature[0:length]

  def getStatusText(self):
    for key, val in Version.STATUS:
      if(key == self.status):
        return val
    return None

class Role(models.Model):
  name = models.CharField(max_length=64)
  environment = models.ForeignKey(Environment)
  last_deployed = models.DateTimeField(null=True)

  def __str__(self):
    if(self.last_deployed):
      return "%s in %s (%s)" % (self.name, self.environment.name, 
          "Active" if self.is_active() else "In-Active")
    else:
      return "%s in %s" % (self.name, self.environment.name) 

  def is_active(self):
    invalid = self.last_deployed.timestamp() + 900
    env = self.environment.last_deployed.timestamp()

    if env > invalid:
      return False
    else:
      return True

  class Meta:
    ordering = ['name']
