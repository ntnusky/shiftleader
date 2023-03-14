from django.conf.urls import url
from host.views import main, ajax, tftp

urlpatterns = [
  # Still to be replaced views:
  url(r'^([0-9]+)/$', main.single, name="singleHost"),
  url(r'^([0-9]+)/interface/$', main.interface, name="hostNewInterface"),
  url(r'^([0-9]+)/interface/([0-9]+)/$', main.interface, name="hostInterface"),
  url(r'^([0-9]+)/puppetlog/([0-9]+)/$', main.single, name="hostPuppetLog"),
  url(r'^group/$', main.hostgroupform, name="hostGroupNew"),
  url(r'^group/([0-9]+)/$', main.hostgroupform, name="hostGroupEdit"),
  url(r'^list/$', main.list, name="hostlist"),

  # AJAX JSON URL's still in use
  url(r'^([0-9]+)/interface/([0-9]+)/delete$', ajax.ifdelete,
      name="hostDelInterface"),

  # TFTP Boot URL's - New URL's exist, but we need to update boot-templates to
  # use them. The views is the same though.
  url(r'^([0-9]+)/tftp$', main.tftp, name="hostTftp"),
  url(r'^([0-9]+)/preseed$', main.installerconfig, name="hostPreseed"),
  url(r'^([0-9]+)/installconfig$', main.installerconfig, name="hostInstallConfig"),
  url(r'^([0-9]+)/postinstall\.sh$', main.postinstall, name="hostPostinstall"),

  # Still used by the kernel-deploy-script on dhcp-servers
  url(r'^tftp/kernels/$', tftp.kernels, name='hostTftpKernels'),
]
