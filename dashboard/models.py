from django.db import models

class APIToken(models.Model):
  name = models.CharField(max_length=200)
  token = models.CharField(max_length=200)

  def __str__(self):
    return "%s (%s)" % (self.name, self.token)

class Task(models.Model):
  SYSTEMS = (
    (0, 'Undefined'),
    (1, 'DNS'),
    (2, 'Puppet'),
  )
  UNDEFINED = 0
  DNS = 1
  PUPPET = 2
  
  STATUSES = (
    (0, 'Ready'),
    (1, 'In-Progress'),
    (2, 'Finished'),
  )
  READY = 0
  PROGRESS = 1
  FINISHED = 2

  system  = models.IntegerField(choices=SYSTEMS)
  created = models.DateTimeField(auto_now_add=True, null=True)
  updated = models.DateTimeField(auto_now=True, null=True)
  status  = models.IntegerField(choices=STATUSES, default=0)
  typeid  = models.IntegerField()
  payload = models.TextField()

  def __str__(self):
    system = "N/A"
    status = "N/A"

    for id, name in self.SYSTEMS:
      if(id == self.system):
        system = name
    for id, name in self.STATUSES:
      if(id == self.status):
        status = name

    return "Task: %s-%d (%s) Created:%s Updated:%s" % (system, self.typeid, 
                          status, self.created, self.updated)
