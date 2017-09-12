from django.conf.urls import include, url
from nameserver.views import main

urlpatterns = [
  url(r'^$', main.index, name="dnsIndex"),
]
