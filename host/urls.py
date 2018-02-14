from django.conf.urls import url
from host.views import main, ajax

urlpatterns = [
  url(r'^$', main.index, name="hostIndex"),
  url(r'^([0-9]+)/$', main.single, name="singleHost"),
  url(r'^([0-9]+)/interface/$', main.interface, name="hostNewInterface"),
  url(r'^([0-9]+)/interface/([0-9]+)/$', main.interface, name="hostInterface"),
  url(r'^([0-9]+)/puppetlog/([0-9]+)/$', main.single, name="hostPuppetLog"),
  url(r'^partition/$', main.pform, name="hostPartitionNew"),
  url(r'^partition/([0-9]+)/$', main.pform, name="hostPartitionEdit"),

  # AJAX URL's
  url(r'^table/$', ajax.table, name='hostAjaxTable'),
  url(r'^form/$', ajax.form, name='hostAjaxForm'),
  url(r'^form/role/([0-9a-zA-Z:]+)/$', ajax.roleList, name='hostAjaxRole'),
  url(r'^menu/role/([0-9]+)/$', ajax.roleMenu, name='hostMenuRole'),

  # AJAX JSON URL's
  url(r'^new/$', ajax.new, name='hostNew'),
  url(r'^provision/$', ajax.provision, name='hostProvision'),
  url(r'^noprovision/$', ajax.noprovision, name='hostNoProvision'),
  url(r'^envrionment/$', ajax.environment, name='hostEnvironment'),
  url(r'^role/$', ajax.role, name='hostRole'),
  url(r'^remove/$', ajax.remove, name='hostDelete'),
  url(r'^([0-9]+)/partition/([0-9]+)/set$', ajax.setpartition, name='hostPart'),
  url(r'^([0-9]+)/interface/([0-9]+)/delete$', ajax.ifdelete,
      name="hostDelInterface"),

  # TFTP Boot URL's
  url(r'^([0-9]+)/tftp$', main.tftp, name="hostTftp"),
  url(r'^([0-9]+)/preseed$', main.preseed, name="hostPreseed"),
  url(r'^([0-9]+)/postinstall\.sh$', main.postinstall, name="hostPostinstall"),
]
