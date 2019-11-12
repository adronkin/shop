from django.urls import path, re_path
import adminapp.views as adminapp

app_name = 'adminapp'

urlpatterns = [
    # re_path(r'^$', adminapp.index, name='index'),
    re_path(r'^$', adminapp.ShopUserListView.as_view(), name='index'),

    re_path(r'^shopuser/create/$', adminapp.shopuser_create, name='shopuser_create'),
    re_path(r'^shopuser/update/(?P<pk>\d+)/$', adminapp.shopuser_update, name='shopuser_update'),
    re_path(r'^shopuser/delete/(?P<pk>\d+)/$', adminapp.shopuser_delete, name='shopuser_delete'),

    re_path(r'^productcategory/list/$', adminapp.productcategory_list,
            name='productcategory_list'),
    re_path(r'^productcategory/create/$', adminapp.ProductCategoryCreateView.as_view(),
            name='productcategory_create'),
    re_path(r'^productcategory/update/(?P<pk>\d+)/$', adminapp.ProductCategoryUpdateView.as_view(),
            name='productcategory_update'),
    re_path(r'^productcategory/delete/(?P<pk>\d+)/$', adminapp.ProductCategoryDeleteView.as_view(),
            name='productcategory_delete'),
    re_path(r'^productcategory/products/(?P<pk>\d+)/$', adminapp.productcategory_products,
            name='productcategory_products'),

    re_path(r'^product/create/(?P<pk>\d+)/$', adminapp.product_create,
            name='product_create'),
    re_path(r'^product/read/(?P<pk>\d+)/$', adminapp.ProductDetailView.as_view(),
            name='product_read'),
    re_path(r'^product/update/(?P<pk>\d+)/$', adminapp.product_update,
            name='product_update'),
    re_path(r'^product/delete/(?P<pk>\d+)/$', adminapp.product_delete,
            name='product_delete'),
]
