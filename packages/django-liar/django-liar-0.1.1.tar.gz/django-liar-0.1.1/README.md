django-liar
=======================

A simple django app with a ( modified ) url function that doesn't resolve invalid apps

In your ROOT_URLCONF module use liar.utils.url instead django url


    from django.conf.urls import patterns, include
    from liar.utils import url
    from django.contrib import admin

    admin.autodiscover()

    urlpatterns = patterns(
        '',
        url(r'^admin/', include(admin.site.urls)),
        url(r'^', include('invalidapp.urls')),
        url(r'^', include('validapp.urls')),
    )


In your settings put:

    INVALID_APPS = [
        'invalidapp'
    ]

Only works using include('app.url_file') notation.