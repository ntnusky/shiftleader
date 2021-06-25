import ipaddress
import re
import string
from random import sample, choice

from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from dashboard.settings import parser
from dhcp.models import Lease, Subnet
from dhcp.omapi import Servers
from nameserver.models import Domain, Forward, Record
from puppet.models import Environment, Role, Report, ReportMetric
from netinstall.models import BootTemplate

# This class is deprecated, and will be removed soon. Same functionality is now
# placed in netboot.models.OperatingSystem
#
# This class is now not used anymore, and can be removed when all our
# installations are running the django2-version of shiftleader
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

class HostGroup(models.Model):
  name = models.CharField(max_length=64)

  def __str__(self):
    return "%s" % self.name

  def toJSON(self):
    return {
      'id': self.id,
      'name': self.name,
    }

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
  group = models.ForeignKey(HostGroup, null=True, on_delete=models.SET_NULL)
  password = models.CharField(max_length=64, null=True)
  os = models.ForeignKey(OperatingSystem, null=True, on_delete=models.SET_NULL)
  template = models.ForeignKey(BootTemplate, null=True,
                                on_delete=models.SET_NULL)
  bootfile = models.ForeignKey('BootFile', null=True, on_delete=models.SET_NULL)
  postinstallscript = models.ForeignKey('BootFile', null=True,
      related_name='scripthosts', on_delete=models.SET_NULL)
  environment = models.ForeignKey(Environment, null=True,
      on_delete=models.SET_NULL)
  role = models.ForeignKey(Role, null=True, on_delete=models.SET_NULL)
  status = models.CharField(max_length=1, choices=STATUSES)

  def __str__(self):
    return "%s.%s" % (self.name, self.getDomain()) 

  def getDomain(self):
    try:
      return self.interface_set.get(primary=True).network.domain
    except:
      return None

  def getPrimaryIf(self):
    try:
      return self.interface_set.filter(primary=True).get()
    except:
      return None

  def getStatusName(self):
    for id, name in self.STATUSES:
      if int(id) == int(self.status):
        return name
    return None

  def getTFTPConfig(self):
    if(int(self.status) == Host.PROVISIONING):
      try:
        return self.template.tftpconfig.getContent(self)
      except:
        return None
    else:
      return render_to_string('tftpboot/localboot.cfg', {})
 
  def toJSON(self):
    data = {
      'id': self.id,
      'name': self.name,
      'status': self.status,
      'statusName': self.getStatusName(),
      'url': reverse('host_api_single', args=[self.id]),
      'url-hostgroup': reverse('host_api_group', args=[self.id]),
      'url-installerconfig': reverse('host_api_installerconfig', args=[self.id]),
      'url-postinstall': reverse('host_api_postinstall', args=[self.id]),
      'url-puppetstatus': reverse('host_api_puppet', args=[self.id]),
      'url-tftp': reverse('host_api_tftp', args=[self.id]),
      'web': reverse('singleHost', args=[self.id]),
    }

    if(self.template):
      data['template'] = self.template.toJSON()
    else:
      data['template'] = None

    if(self.group):
      data['group'] = self.group.toJSON()
    else:
      data['group'] = None

    if(self.environment):
      data['environment'] = self.environment.toJSON()
    else:
      data['environment'] = None

    if(self.role):
      data['role'] = self.role.toJSON()
    else:
      data['role'] = None

    return data

  def updateInfo(self, data):
    changed = False
    if('template_id' in data):
      if(data['template_id'] == '0'):
        template = None
      else:
        try:
          template = BootTemplate.objects.get(id = data['template_id'])
        except BootTemplate.DoesNotExist:
          raise KeyError('No template with ID %s' % data['template_id'])

      if self.template != template:
        self.template = template
        changed = True

    if('environment_id' in data):
      if(data['environment_id'] == '0'):
        environment = None
      else:
        try:
          environment = Environment.objects.get(id = data['environment_id'])
        except Environment.DoesNotExist:
          raise KeyError('No environment with ID %s' % data['environment_id'])

      if(self.environment != environment):
        try:
          role = Role.objects.get(
                          name=self.role.name, environment = environment)
        except (Role.DoesNotExist, AttributeError):
          role = None

        self.environment = environment
        self.role = role
        changed = True

    if('role_id' in data):
      if(data['role_id'] == '0'):
        role = None
      else:
        try:
          role = Role.objects.get(id = data['role_id'])
        except Role.DoesNotExist:
          raise KeyError('No role with ID %s' % data['role_id'])

      if(self.role != role):
        if(self.environment != role.environment):
          raise AttributeError('Role %d don\'t belong to environment %d' % \
                  (role.id, self.environment.id))

        self.role = role
        changed = True

    if('rebuild' in data): 
      if(data['rebuild'] == '1'):
        self.status = Host.PROVISIONING
      else:
        self.status = Host.OPERATIONAL
      changed = True

    return changed

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
    try:
      report = self.report_set.last()
    except:
      report = None

    if(report):
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

      return statusText
    else:
      return "N/A"

  def updateDNS(self):
    for interface in self.interface_set.all():
      if(interface.ipv4Lease):
        ipv4 = interface.ipv4Lease.IP
      else:
        ipv4 = None

      try:
        record = Forward.objects.get(name=self.name, 
                                domain=interface.network.domain)
      except Forward.DoesNotExist:
        record = Forward(name=self.name, domain=interface.network.domain)

      try:
        v6 = ipaddress.IPv6Address(interface.ipv6)
        record.ipv6 = interface.ipv6
      except:
        record.ipv6 = None

      record.active = True
      record.record_type = Record.TYPE_HOST
      record.reverse = True
      record.ipv4 = ipv4
      record.configure()
      record.save()
      interface.dns = record
      interface.save()

  def generatePassword(self):
    chars = string.ascii_letters + string.digits
    self.password = ''.join(choice(chars) for _ in range(16))
    self.save()

  def remove(self):
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
      if interface.dns:
        interface.dns.delete()
      interface.delete()
    self.delete()

  class Meta:
    ordering = ['name']

class Network(models.Model):
  name = models.CharField(max_length=64)
  domain = models.ForeignKey(Domain, on_delete=models.PROTECT)
  v4subnet = models.ForeignKey(Subnet, related_name="v4network", null=True,
                                on_delete=models.PROTECT)
  v6subnet = models.ForeignKey(Subnet, related_name="v6network", null=True,
                                on_delete=models.PROTECT)

  def __str__(self):
    if(self.v4subnet):
      v4 = str(self.v4subnet)
    else:
      v4 = "None"

    if(self.v6subnet):
      v6 = str(self.v6subnet)
    else:
      v6 = "None"

    return "%s - v4:%s - v6:%s" % (self.name, v4, v6)

class Interface(models.Model):
  V6TYPES = (
    (0, 'None'),
    (1, 'EUI-64'),
    (2, 'Static'),
  )
  
  V6TYPE_NONE = 0
  V6TYPE_EUI64 = 1
  V6TYPE_STATIC = 2

  ifname = models.CharField(max_length=20)
  mac = models.CharField(max_length=64)
  host = models.ForeignKey(Host, on_delete=models.PROTECT)
  dns = models.ForeignKey(Forward, default=None, null=True,
                           on_delete=models.PROTECT)
  primary = models.BooleanField(default=False)
  network = models.ForeignKey(Network, null=True, default=None,
                           on_delete=models.PROTECT)
  ipv4Lease = models.OneToOneField(Lease, null=True, on_delete=models.SET_NULL)
  ipv6 = models.GenericIPAddressField(protocol='IPv6', null=True)

  def __str__(self):
    return "%s on %s" % (self.ifname, self.host)

# This class is deprecated, and will be removed soon. Same functionality is now
# placed in netboot.models.ConfigFile
# 
# This class is now not used anymore, and can be removed when all our
# installations are running the django2-version of shiftleader
class BootFile(models.Model):
  UNSET = 0
  BOOTFILE = 1
  POSTINSTALLSCRIPT = 2

  filetypes = (
    (UNSET, 'Unset'),
    (BOOTFILE, 'Bootfile'),
    (POSTINSTALLSCRIPT, 'Postinstall script'),
  )

  name = models.CharField(max_length=64)
  description = models.TextField()
  filetype = models.IntegerField(choices = filetypes, default = 0)
  
  class Meta:
    ordering = ['name']

  def __str__(self):
    return self.name

  def getType(self):
    for t in self.filetypes:
      if(t[0] == self.filetype):
        return t[0]
    return self.UNSET

  def getTypeTxt(self):
    for t in self.filetypes:
      if(t[0] == self.filetype):
        return t[1]
    return 'Unset'

  def getContent(self, replaces = {}):
    content = []
    for fragment in self.bootfilefragment_set.order_by('order').all():
      s = fragment.fragment.content

      for key in replaces:
        s = s.replace('%%%s%%' % key, replaces[key])

      content.append(s)

    return re.sub(r'\r\n', '\n', '\n'.join(content)) 

# This class is deprecated, and will be removed soon. Same functionality is now
# placed in netboot.models.ConfigFile
# 
# This class is now not used anymore, and can be removed when all our
# installations are running the django2-version of shiftleader
class BootFragment(models.Model):
  name = models.CharField(max_length=64)
  description = models.TextField()
  content = models.TextField()
  
  class Meta:
    ordering = ['name']

  def __str__(self):
    return self.name

# This class is deprecated, and will be removed soon. Same functionality is now
# placed in netboot.models.ConfigFile
# 
# This class is now not used anymore, and can be removed when all our
# installations are running the django2-version of shiftleader
class BootFileFragment(models.Model):
  bootfile = models.ForeignKey(BootFile, on_delete=models.PROTECT)
  fragment = models.ForeignKey(BootFragment, on_delete=models.PROTECT)
  order = models.IntegerField()

  class Meta:
    ordering = ['order']
