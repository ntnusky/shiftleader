import re
import yaml

from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseServerError
from django.utils import dateparse
from django.views.decorators.csrf import csrf_exempt

from puppet.models import Report, ReportMetric, ReportTag, ReportLog, Environment
from host.models import Host
from nameserver.models import Domain

@csrf_exempt
def main(request):
  try:
    bodytext = request.body.decode('utf-8')
    body = re.sub(r'!ruby/object:Puppet::Transaction::Report', r'', bodytext)
    try:
      data = yaml.load(body)
    except Exception as e:
      print("Could not load yaml data")
      return HttpResponseServerError("Could not load yaml data")

    parts = data['host'].split('.')
    hostname = parts[0]
    domainname = '.'.join(parts[1:])
    try:
      environment = Environment.objects.get(name=data['environment'])
      domain = Domain.objects.get(name=domainname)
      for h in Host.objects.filter(name=hostname).all():
        if h.getDomain() == domain
          host = h
    except Exception as e:
      print("Could not find environment, domain and host")
      return HttpResponseServerError("Could not find environment, domain and host")

    status = 2
    for id, name in Report.STATUSES:
      if(name.lower() == data['status'].lower()):
        status = id

    time = dateparse.parse_datetime(data['time'])
    report = Report(host=host, environment=environment, noop=data['noop'],
        noop_pending=data['noop_pending'],
        configuration_version=data['configuration_version'],
        puppet_version=data['puppet_version'], status=status, time=time)
    report.save()

    allTags = {}
    for tag in ReportTag.objects.all():
      allTags[tag.name] = tag

    for log in data['logs']:
      level = None
      for id, name in ReportLog.LEVELS:
        if(name.lower() == log['level'].lower()):
          level = id

      print("%s, %s" % (str(level), log['level']))
      time = dateparse.parse_datetime(log['time'])
      entry = ReportLog(report=report, level=level, message=log['message'],
          source=log['source'], line=log['line'], file=log['file'], time=time)
      entry.save()

      # Removed storing of tags, as this takes too much time... Can be optimized
      # and enabled later.
      #for tag in log['tags']:
      #  if(tag not in allTags):
      #    allTags[tag] = ReportTag(name=tag)
      #    allTags[tag].save()
      #  entry.tags.add(allTags[tag])

    for id, name, value in data['metrics']['resources']['values']:
      m = ReportMetric(report=report, metricType=ReportMetric.TYPE_RESOURCE,
          name=name, value=value)
      m.save()

    for id, name, value in data['metrics']['events']['values']:
      m = ReportMetric(report=report, metricType=ReportMetric.TYPE_EVENT,
          name=name, value=value)
      m.save()

    for id, name, value in data['metrics']['changes']['values']:
      m = ReportMetric(report=report, metricType=ReportMetric.TYPE_CHANGE,
          name=name, value=value)
      m.save()

    for id, name, value in data['metrics']['time']['values']:
      m = ReportMetric(report=report, metricType=ReportMetric.TYPE_TIME,
          name=name, value=value)
      m.save()
  except Exception as e:
    print(e)
  

  return HttpResponse("")
