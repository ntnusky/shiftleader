import re
import string
from random import sample, choice

from django.db import models
from django.utils import timezone

from dashboard.settings import parser
from dhcp.models import Lease
from dhcp.omapi import Servers
from nameserver.models import Domain
from puppet.models import Environment, Role, Report, ReportMetric

class PartitionScheme(models.Model):
  name = models.CharField(max_length=64)
  description = models.TextField()
  content = models.TextField()

  def __str__(self):
    maxLength = 30
    if(len(self.description) > maxLength):
      return "%s (%s...)" % (self.name, self.getShortDescription(maxLength))
    else:
      return "%s (%s)" % (self.name, self.description)

  def getShortDescription(self, length=30):
    return self.description[0:length]

class Host(models.Model):
  STATUSES = (
    (0, "Operational"),
    (1, "Provisioning"),
    (2, "Installing"),
    (3, "Puppet-Sign"),
    (4, "Puppet-Ready"),
    (5, "Puppet-Timeout"),
    (6, "Puppet-Error"),
  )

  OPERATIONAL = 0
  PROVISIONING = 1
  INSTALLING = 2
  PUPPETSIGN = 3
  PUPPETREADY = 4
  TIMEOUT = 5
  ERROR = 6

  name = models.CharField(max_length=64)
  password = models.CharField(max_length=64, null=True)
  environment = models.ForeignKey(Environment)
  partition = models.ForeignKey(PartitionScheme, null=True, default=None)
  role = models.ForeignKey(Role, null=True)
  status = models.CharField(max_length=1, choices=STATUSES)

  def __str__(self):
    return "%s.%s" % (self.name, self.interface_set.filter(primary=True).\
        get().ipv4Lease.subnet.domain.name)

  def getPrimaryIf(self):
    try:
      return self.interface_set.filter(primary=True).get()
    except:
      return None

  def updatePuppetStatus(self):
    if(int(self.status) not in [self.OPERATIONAL, self.PUPPETREADY,
        self.TIMEOUT, self.ERROR]):
      return self.status

    report = self.report_set.last()

    if not report:
      self.status = self.PUPPETREADY
      self.save()
      return self.status

    delta = timezone.now() - report.time
    interval = parser.get('puppet', 'runinterval')
    match = re.match(r'(\d+)([hms])', interval)

    if(match):
      if(match.group(2) == 'h'):
        sec = int(match.group(1)) * 60 * 60
      elif(match.group(2) == 'm'):
        sec = int(match.group(1)) * 60
      elif(match.group(2) == 's'):
        sec = int(match.group(1))
      else:
        self.status = self.ERROR
        self.save()
        return self.status

    if(delta.seconds > sec * 2):
      self.status = self.TIMEOUT
    else:
      self.status = self.OPERATIONAL

    self.save()
    return self.status

  def getPuppetStatusIcon(self):
    status = self.status
    report = self.report_set.last()
    if(int(status) in [self.PROVISIONING, self.INSTALLING, self.PUPPETSIGN]):
      return "glyphicon-hourglass text-info"
    elif(int(status) in [self.TIMEOUT, self.ERROR]):
      return "glyphicon-remove-sign text-danger"
    elif(int(status) == self.PUPPETREADY):
      return "glyphicon-question-sign text-info"
    elif(int(status) == self.OPERATIONAL and report):
      met = report.reportmetric_set.filter(metricType=ReportMetric.TYPE_RESOURCE).all()
      metrics = {}
      for metric in met:
        if(metric.name in ['Changed', 'Failed', 'Skipped']):
          metrics[metric.name] = metric.value

      try:
        if(int(metrics['Failed']) > 0 or int(metrics['Skipped']) > 0):
          return "glyphicon-remove-sign text-danger"
        else:
          return "glyphicon-ok-sign text-success"
      except KeyError:
        return "glyphicon-question-sign text-info"
    else:
      return "glyphicon-question-sign text-info"

  def getTableColor(self):
    report = self.report_set.last()
    if report:
      return report.getTableColor()
    else:
      return ""

  def getStatusText(self):
    status = self.status
    for s in self.STATUSES:
      if s[0] == int(status):
        statusText = s[1]

    report = self.report_set.last()
    if(statusText == 'Operational' and report):
      met = report.reportmetric_set.filter(metricType=ReportMetric.TYPE_RESOURCE).all()
      metrics = {}
      for metric in met:
        if(metric.name in ['Changed', 'Failed', 'Skipped']):
          metrics[metric.name] = metric.value

      try:
        if(int(metrics['Failed']) > 0):
          statusText = "%d failed!" % int(metrics['Failed'])
        elif(int(metrics['Skipped']) > 0):
          statusText = "%d skipped!" % int(metrics['Skipped'])
        elif(int(metrics['Changed']) > 0):
          statusText = "%d changes" % int(metrics['Changed'])
        else:
          statusText = "OK"
      except KeyError:
        statusText = "MetricsMissing"

    if statusText:
      return statusText
    else:
      return "N/A"

  def deleteDNS(self):
    for interface in self.interface_set.all():
      # If this is the primary interface, delete the A record with the machine's
      # hostname.
      if(interface.primary):
        try:
          self.domain.deleteDomain(self.name)
        except AttributeError:
          pass

      # Delete the interface-specific A record
      try:
        self.domain.deleteDomain("%s.%s" % (interface.name, self.name))
      except AttributeError:
        pass

  def updateDNS(self):
    for interface in self.interface_set.all():
      # If this is the primary interface, add an A record with the machine's
      # hostname (Unless the host have the same domain as the primary interface)
      if(interface.primary):
        if(interface.ipv4Lease and 
            self.domain != interface.ipv4Lease.subnet.domain):
          self.domain.configure(self.name, interface.ipv4Lease.IP)
        if(interface.ipv6):
          self.domain.configure(self.name, interface.ipv6)

      if(interface.ipv4Lease):
        interface.ipv4Lease.subnet.domain.configure(self.name, interface.ipv4Lease.IP)

        # If we manage the reverse-zone, configure a reverse name for this
        # interface.
        ip = interface.ipv4Lease.IP.split('.')
        try:
          reverseDomain = "%s.%s.%s.in-addr.arpa" % (ip[2], ip[1], ip[0])
          domain = Domain.objects.get(name=reverseDomain)
          domain.configure(ip[3], "%s.%s." % (self.name, self.domain))
        except Domain.DoesNotExist:
          pass

        if(interface.ipv6):
          interface.ipv4Lease.subnet.domain.configure(self.name, interface.ipv6)

  def generatePassword(self):
    chars = string.ascii_letters + string.digits
    self.password = ''.join(choice(chars) for _ in range(16))
    self.save()

  def remove(self):
    self.deleteDNS()
    dhcp = Servers()
    for interface in self.interface_set.all():
      dhcp.configureLease(interface.ipv4Lease.IP, interface.ipv4Lease.MAC,
          present = False)
      lease = interface.ipv4Lease
      lease.present = False
      lease.lease = False
      lease.save()
      lease.subnet.free += 1
      lease.subnet.save()
      interface.delete()
    self.delete()

  class Meta:
    ordering = ['name']

class Interface(models.Model):
  ifname = models.CharField(max_length=20)
  mac = models.CharField(max_length=64)
  host = models.ForeignKey(Host)
  primary = models.BooleanField(default=False)
  ipv4Lease = models.OneToOneField(Lease, null=True)
  ipv6 = models.GenericIPAddressField(protocol='IPv6', null=True)

  def __str__(self):
    return "%s on %s" % (self.ifname, self.host)
