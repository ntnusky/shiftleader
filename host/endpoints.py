from django.conf.urls import url
from host.views import host

urlpatterns = [
  url(r'^$', host.main, name="host_api_main"),
  url(r'^([0-9]+)/$', host.single, name="host_api_single"),
  url(r'^([0-9]+)/group$', host.group, name="host_api_group"),
  url(r'^([0-9]+)/puppet$', host.puppet, name="host_api_puppet"),
]
