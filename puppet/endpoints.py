from django.conf.urls import url
from puppet.views import environment, role

urlpatterns = [
  url(r'^environment/$', environment.index, name="puppet_api_environments"),
  url(r'^environment/discover/$', environment.discover, 
          name="puppet_api_environment_discover"),
  url(r'^environment/([0-9]+)/$', environment.index, name="puppet_api_environment"),
  url(r'^environment/([0-9]+)/roles$', role.index, name="puppet_api_roles"),
  url(r'^environment/([0-9]+)/deploy$', environment.deploy, 
          name="puppet_api_deploy"),
]
