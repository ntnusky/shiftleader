from django.conf.urls import url
from host.views import main

urlpatterns = [
  url(r'^$', main.main, name="hostMain"),
]
