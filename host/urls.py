from django.conf.urls import url
from host.views import main, ajax

urlpatterns = [
  url(r'^$', main.index, name="hostIndex"),
  url(r'^([0-9]+)/$', main.single, name="singleHost"),

  # AJAX URL's
  url(r'^table/$', ajax.table, name='hostAjaxTable'),
  url(r'^form/$', ajax.form, name='hostAjaxForm'),

  # AJAX JSON URL's
  url(r'^new/$', ajax.new, name='hostNew'),

  # TFTP Boot URL's
  url(r'^([0-9]+)/tftp$', main.tftp, name="hostTftp"),
  url(r'^([0-9]+)/preseed$', main.preseed, name="hostPreseed"),
]
