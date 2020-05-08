from django.conf.urls import url

from netinstall.views import web, configfile, operatingsystem, template

urlpatterns = [
  url(r'^configfile/$', web.file, name="netinstall_file"),
  url(r'^template/$',   web.template, name="netinstall_template"),
]
