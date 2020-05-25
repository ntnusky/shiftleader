from django.conf.urls import url
from host.views import host, group, main

urlpatterns = [
  url(r'^$', host.main, name="host_api_main"),
  url(r'^group$', group.main, name="host_api_groups"),
  url(r'^([0-9]+)/$', host.single, name="host_api_single"),
  url(r'^([0-9]+)/group$', host.group, name="host_api_group"),
  url(r'^([0-9]+)/installerconfig$', main.installerconfig, 
                                    name="host_api_installerconfig"),
  url(r'^([0-9]+)/postinstall$', main.postinstall, 
                                    name="host_api_postinstall"),
  url(r'^([0-9]+)/puppet$', host.puppet, name="host_api_puppet"),
  url(r'^([0-9]+)/tftp$', main.tftp, name="host_api_tftp"),
]
