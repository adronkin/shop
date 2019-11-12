from django.contrib import admin

# Регистрирую моели на сайте админки
from django.contrib import admin
from .models import ProductCategory, Product

admin.site.register(ProductCategory)
admin.site.register(Product)
