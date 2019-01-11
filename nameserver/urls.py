from django.conf.urls import include, url
from nameserver.views import main

urlpatterns = [
  url(r'^$', main.index, name="dnsIndex"),
  url(r'^form/$', main.form, name='dnsNew'),
  url(r'^form/([0-9]+)/$', main.form, name='dnsEdit'),

  # AJAX
  url(r'^table/$', main.table, name='dnsAjaxTable'),
  url(r'^delete/([0-9]+)/$', main.delete, name='dnsAjaxDelete'),
  url(r'^activate/([0-9]+)/$', main.activate, name='dnsAjaxActivate'),
  url(r'^deactivate/([0-9]+)/$', main.deactivate, name='dnsAjaxDeactivate'),
]
