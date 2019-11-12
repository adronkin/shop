from django.urls import path, re_path
import basketapp.views as basketapp

app_name = 'basketapp'

urlpatterns = [
    re_path(r'^$', basketapp.index, name='index'),
    re_path('add/(?P<pk>\d+)/', basketapp.basket_add, name='add'),
    re_path('delete/(?P<pk>\d+)/', basketapp.basket_delete, name='delete'),
    re_path('update/(?P<pk>\d+)/(?P<quantity>\d+)/', basketapp.basket_update, name='update'),
]
