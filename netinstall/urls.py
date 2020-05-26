from django.conf.urls import url

from netinstall.views import web, configfile, operatingsystem, template

urlpatterns = [
  url(r'^configfile/$', web.file, name="netinstall_file"),
  url(r'^configfile/([0-9]+)/$', web.filepreview, name="netinstall_filepreview"),
  url(r'^os/$',   web.os, name="netinstall_os"),
  url(r'^template/$',   web.template, name="netinstall_template"),
]
