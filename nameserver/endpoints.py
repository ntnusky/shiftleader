from django.conf.urls import url
from nameserver.views import domain

urlpatterns = [
  url(r'^domain/$', domain.main, name="nameserver_domain"),
]
