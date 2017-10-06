import datetime

from django.db import models
from django.utils import timezone

class Environment(models.Model):
  name = models.CharField(max_length=64)
  active = models.BooleanField()

  def __str__(self):
    return "%s (%s)" % (self.name, "Active" if self.active else "In-Active")

  class Meta:
    ordering = ['-active', 'name']

class Server(models.Model):
  STATUSES = (
    ('0', 'Ok'),
    ('1', 'Checkin started'),
    ('2', 'r10k running'),
    ('3', 'r10k error'),
    ('4', 'Timeout')
  )

  STATUS_OK = '0'
  STATUS_START = '1'
  STATUS_RUN = '2'
  STATUS_ERR = '3'
  STATUS_TIME = '4'

  name = models.CharField(max_length=64)
  todeploy = models.ManyToManyField(Environment)
  last_checkin = models.DateTimeField()
  status = models.CharField(max_length=1, choices=STATUSES)

  def __str__(self):
    return "%s (%s)" % (self.name, self.getStatusText())

  def getStatusText(self):
    invalid = datetime.datetime.fromtimestamp(self.last_checkin.timestamp()+360)
    if(timezone.now() > timezone.make_aware(invalid)):
      self.status = self.STATUS_TIME
      self.save()

    for key, value in self.STATUSES:
      if key == self.status:
        return value
    return None

  def checkin(self, status):
    self.last_checkin = timezone.now()
    self.status = status
    self.save()

  def deploy(self, env):
    if(env not in self.todeploy.all()):
      self.todeploy.add(env)
      return True
    return False

  def latest_envs(self):
    envs = []
    for env in Environment.objects.all():
      last = self.environmentversion_set.filter(environment=env).last()
      if(not last):
        last = self.environmentversion_set.create(environment=env,
            signature="", started="", finished="", success=False)
      envs.append(last)
    return envs
      

class EnvironmentVersion(models.Model):
  STATUS = (
    ('-1', 'Unavailable'),
    ('0', 'Deploying'),
    ('1', 'Deployed'),
    ('2', 'Scheduled'),
  )
  STATUS_UNAVAILABLE = '-1'
  STATUS_DEPLOYING = '0'
  STATUS_DEPLOYED = '1'
  STATUS_SCHEDULED = '2'

  environment = models.ForeignKey(Environment)
  server = models.ForeignKey(Server)
  signature = models.CharField(max_length=64)
  started = models.CharField(max_length=64)
  finished = models.CharField(max_length=64)
  success = models.BooleanField()
  status = models.CharField(max_length=1, choices=STATUS,
      default=STATUS_UNAVAILABLE)

  def __str__(self):
    return "%s (rev: %s)" % (self.environment, self.signature[0:7])

  def deployable(self):
    return (self.status == self.STATUS_DEPLOYED) or \
        (self.status == self.STATUS_UNAVAILABLE)

  def getShortSignature(self):
    return self.signature[0:7]

  def getStatusText(self):
    for key, val in EnvironmentVersion.STATUS:
      if(key == self.status):
        return val
    return ""

class Role(models.Model):
  name = models.CharField(max_length=64)
  environment = models.ForeignKey(Environment)
  active = models.BooleanField()

  def __str__(self):
    return "%s in %s (%s)" % (self.name, self.environment.name, 
        "Active" if self.active else "In-Active")

  class Meta:
    ordering = ['-active', 'name']

