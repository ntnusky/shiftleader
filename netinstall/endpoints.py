from django.conf.urls import url

from netinstall.views import configfile, operatingsystem, template

urlpatterns = [
  url(r'^configfile/$', configfile.main, name="netinstall_rest_files"),
  url(r'^configfile/([0-9]+)/$', configfile.main, name="netinstall_rest_file"),
  url(r'^configfile/type/$', configfile.filetype, 
                              name="netinstall_rest_file_types"),
  url(r'^configfile/type/([0-9]+)/$', configfile.filetype, 
                              name="netinstall_rest_file_type"),
  url(r'^os/$', operatingsystem.main, name="netinstall_rest_oss"),
  url(r'^os/([0-9a-zA-Z\.]+)/$', operatingsystem.main, 
                              name="netinstall_rest_os"),
  url(r'^template/$', template.main, name="netinstall_rest_templates"),
  url(r'^template/([0-9]+)/$', template.main, name="netinstall_rest_template"),
]
