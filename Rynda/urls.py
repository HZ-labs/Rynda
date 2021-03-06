# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

from users.views import CreateUser

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'RyndaRebuild.views.home', name='home'),
    # url(r'^RyndaRebuild/', include('RyndaRebuild.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', 'message.views.list'),
    url(r'', include('social_auth.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin-tools/', include('admin_tools.urls')),
    url(r'^info/', include('core.urls')),
    url(r'^logout$', 'message.views.logout_view'),
    url(r'^message/', include('message.urls')),
    url(r'^register$', CreateUser.as_view()),
    url(r'^t/(?P<slug>[a-z_0-9-]+)$', 'message.views.list'),
    url(r'^t/(?P<slug>)message/', include('message.urls')),
    url(r'^user/', include('users.urls')),
)

urlpatterns += patterns('django.contrib.auth.views',
    url(r'^login$', 'login',
        {'template_name': 'login.html'}),
    url(r'^password/reset$', 'password_reset',
        ),
    url(r'^password/reset/confirm/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'password_reset_confirm',),
    url(r'^password/reset/complete$',
        'password_reset_complete'),
    url(r'^password/reset/done',
        'password_reset_done', ),
)
urlpatterns += patterns('core.views',

)

urlpatterns += patterns('',
    (r'^api/', include('api.urls')),
)
