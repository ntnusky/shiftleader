from django.conf.urls import include, url
from nameserver.views import main

urlpatterns = [
  url(r'^records/$', main.records, name='dns_records'),
]
