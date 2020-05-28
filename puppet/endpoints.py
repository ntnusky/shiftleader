from django.conf.urls import url
from puppet.views import environment, role

urlpatterns = [
  url(r'^environment/$', environment.index, name="puppet_api_environments"),
  url(r'^environment/([0-9]+)/$', environment.index, name="puppet_api_environment"),
  url(r'^environment/([0-9]+)/roles$', role.index, name="puppet_api_roles"),
]
