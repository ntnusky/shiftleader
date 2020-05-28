from django.conf.urls import url
from host.views import main, ajax, rest, tftp

urlpatterns = [
  url(r'^$', main.main, name="hostMain"),
]
