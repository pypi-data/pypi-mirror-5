from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^notification/', include('test_project.notification.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
