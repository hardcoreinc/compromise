# -*- coding: utf-8 -*-
from django.conf.urls import patterns, include, url
from compSite.views import *
from django.views.generic import TemplateView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	
    # Examples:
    # url(r'^$', 'compromise.views.home', name='home'),
    # url(r'^compromise/', include('compromise.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    #url(r"[A-z]", hello),
    url(r"^addevent/", saveCompromise),
    url(r"^newevent/", TemplateView.as_view(template_name='newevent.html')),
    url(r"^oauth2google/", oauth2google),
    url(r"^event/", renderAnswer),
    url(r"^$", index),
)
