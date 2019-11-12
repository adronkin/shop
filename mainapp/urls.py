from django.urls import path, re_path
from django.views.decorators.cache import cache_page  # кеширование для CBV
import mainapp.views as mainapp

app_name = 'mainapp'

urlpatterns = [
    re_path(r'^$', mainapp.index, name='index'),  # ловит пустую строку + переменная для динамического URL

    re_path(r'^category/(?P<pk>\d+)/$', mainapp.category, name='category'),
    re_path(r'^category/(?P<pk>\d+)/ajax/$', cache_page(60)(mainapp.category_ajax)),  # кеширование для CBV

    re_path(r'^product/(?P<pk>\d+)/$', mainapp.product, name='product'),
    re_path(r'^category/(?P<pk>\d+)/(?P<page>\d+)/$', mainapp.category, name='category_paginator'),
    re_path(r'^category/(?P<pk>\d+)/(?P<page>\d+)/ajax/$', cache_page(60)(mainapp.category_ajax)),

    re_path(r'^hot_deal/$', mainapp.hot_deal, name='hot_deal'),
    re_path(r'^contact/$', mainapp.contact, name='contact'),
]
