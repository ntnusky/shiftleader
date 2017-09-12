"""dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url

from dashboard.views import main

urlpatterns = [
  url(r'^$', main.index, name="index"),
  url(r'^login/$', main.loginPage, name="login"),
  url(r'^logout/$', main.logoutPage, name="logout"),

  url(r'^puppet/', include('puppet.urls')),
  url(r'^dhcp/', include('dhcp.urls')),
  url(r'^dns/', include('nameserver.urls')),
]
