from django.conf.urls import url
from nameserver.views import domain, record

urlpatterns = [
  url(r'^domain/$', domain.main, name="nameserver_domain"),
  url(r'^record/$', record.all, name="nameserver_records"),
  url(r'^record/cname/$', record.cname, name="nameserver_cname"),
  url(r'^record/forward/$', record.forward, name="nameserver_forward"),
  url(r'^record/reverse/$', record.reverse, name="nameserver_reverse"),
]
