from datetime import datetime

from django.db import models
from django.utils import timezone

class Environment(models.Model):
  name = models.CharField(max_length=64)
  last_deployed = models.DateTimeField(null=True)
  active = models.BooleanField(default=False)

  def __str__(self):
    return "%s (%s)" % (self.name, "Active" if self.is_active() else "In-Active")

  def getLatestVersion(self):
    return self.version_set.order_by('-created').first()

  def is_active(self):
    return self.active

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

  def getHostName(self):
    return self.name.split('.')[0]

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

class Report(models.Model):
  STATUSES = (
    (0, 'Unchanged'),
    (1, 'Changed'),
    (2, 'Failed'),
  )
  STATUS_UNCHANGED = 0
  STATUS_CHANGED = 1
  STATUS_FAILED = 2

  host = models.ForeignKey('host.Host')
  environment = models.ForeignKey(Environment)
  noop = models.BooleanField()
  noop_pending = models.BooleanField()
  configuration_version = models.CharField(max_length=32)
  puppet_version = models.CharField(max_length=12)
  status = models.IntegerField(choices=STATUSES)
  time = models.DateTimeField()

  def __str__(self):
    return "%s - %s" % (self.host, self.time)

  def getStatusIcon(self):
    icons = [
      "glyphicon-ok-sign text-success",
      "glyphicon-ok-sign text-info",
      "glyphicon-remove-sign text-danger"
    ]
    return icons[self.status]

  def getTableColor(self):
    icons = [
      "",
      "",
      "danger"
    ]
    return icons[self.status]

  def getMetrics(self):
    data = {}
    interests = ["Total", "Skipped", "Failed", "Changed", "Out of sync"]
    
    metrics = self.reportmetric_set.filter( \
        metricType = ReportMetric.TYPE_RESOURCE).all()
    for metric in metrics:
      if(metric.name in interests):
        data[metric.name.replace(' ', '')] = metric.value

    return data


class ReportMetric(models.Model):
  TYPES = (
    (0, 'Time'),
    (1, 'Resource'),
    (2, 'Event'),
    (3, 'Change'),
  )
  TYPE_TIME = 0
  TYPE_RESOURCE = 1
  TYPE_EVENT = 2
  TYPE_CHANGE = 3

  report = models.ForeignKey(Report)
  metricType = models.IntegerField(choices=TYPES)
  name = models.CharField(max_length=32)
  value = models.CharField(max_length=64)

  def __str__(self):
    return "%s: %s-%s" % (self.TYPES[self.metricType][1], self.name, self.value)

class ReportTag(models.Model):
  name = models.CharField(max_length=64)

  def __str__(self):
    return self.name

class ReportLog(models.Model):
  LEVELS = (
    (0, 'Crit'),
    (1, 'Emerg'),
    (2, 'Alert'),
    (3, 'Err'),
    (4, 'Warning'),
    (5, 'Notice'),
    (6, 'Info'),
    (7, 'Debug'),
  )
  LEVEL_CRITICAL = 0
  LEVEL_EMERGENCY = 1
  LEVEL_ALERT = 2
  LEVEL_ERROR = 3
  LEVEL_WARNING = 4
  LEVEL_NOTICE = 5
  LEVEL_INFO = 6
  LEVEL_DEBUG = 7

  report = models.ForeignKey(Report)
  level = models.IntegerField(choices=LEVELS)
  message = models.TextField()
  source = models.TextField()
  line = models.IntegerField(null=True)
  file = models.CharField(max_length=128, null=True)
  tags = models.ManyToManyField(ReportTag, related_name='entries')
  time = models.DateTimeField()

  def __str__(self):
    return "%s, %s" % (self.LEVELS[self.level][1], self.message)

  def getLevelText(self):
    return self.LEVELS[self.level][1]

  def getTableColor(self):
    if(self.level < self.LEVEL_WARNING):
      return "danger"
    elif(self.level < self.LEVEL_NOTICE):
      return "warning"
    elif(self.level < self.LEVEL_INFO):
      return "info"
    elif(self.level < self.LEVEL_DEBUG):
      return "success"
    else:
      return ""
