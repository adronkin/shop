import random

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render, get_object_or_404
import json

from .models import ProductCategory, Product
from django.conf import settings
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.cache import never_cache
from django.template.loader import render_to_string
from django.http import JsonResponse


def index(request):
    products = get_products()[:6]  # берем из кешированных продуктов

    context = {
        'page_title': 'главная',
        'products': products,
    }
    return render(request, 'mainapp/index.html', context)


def get_basket(request):
    if request.user.is_authenticated:
        return request.user.basket.all().order_by('product__category')
    else:
        return []


def get_same_products(hot_product):
    # Выбираю другие продукты из категории товара hot_product, исключаю из списка hot_product
    same_products = Product.objects.filter(category=hot_product.category, is_active=True).exclude(pk=hot_product.pk)[:3]

    return same_products


@never_cache
def category(request, pk, page=1):
    pk = int(pk)

    if pk == 0:
        category = {
            'pk': 0,
            'name': 'все'
        }
        products = get_products_ordered_by_price()
    else:
        category = get_category(pk)
        products = get_products_in_category_ordered_by_price(pk)

    paginator = Paginator(products, 3)
    try:
        products_paginator = paginator.page(page)
    except PageNotAnInteger:
        products_paginator = paginator.page(1)
    except EmptyPage:
        products_paginator = paginator.page(paginator.num_pages)

    context = {
        'products_menu': get_links_meny(),  # берем из кешированного меню
        'category': category,
        'category_products': products_paginator,
        'page_title': 'каталог',
    }
    return render(request, 'mainapp/category_products.html', context)


# @cache_page(3600)
def category_ajax(request, pk, page=1):
    if request.is_ajax():
        pk = int(pk)

        if pk == 0:
            category = {
                'pk': 0,
                'name': 'все'
            }
            products = get_products_ordered_by_price()
        else:
            category = get_category(pk)
            products = get_products_in_category_ordered_by_price(pk)

        paginator = Paginator(products, 3)
        try:
            products_paginator = paginator.page(page)
        except PageNotAnInteger:
            products_paginator = paginator.page(1)
        except EmptyPage:
            products_paginator = paginator.page(paginator.num_pages)

        context = {
            'products_menu': get_links_meny(),  # берем из кешированного меню
            'category': category,
            'category_products': products_paginator,
            'page_title': 'каталог',
        }

        result = render_to_string(
            'mainapp/includes/inc__products_list_content.html',
            context=context,
            request=request)
        return JsonResponse({'result':result})


def hot_deal(request):
    hot_product = get_hot_product()

    context = {
        'page_title': 'товар',
        'products_menu': get_products_menu(),
        'hot_product': hot_product,
        'same_products': get_same_products(hot_product),
    }
    return render(request, 'mainapp/hot_deal.html', context)


def product(request, pk):
    product = get_product(pk)

    context = {
        'page_title': 'страница продукта',
        'products_menu': get_links_meny(),  # берем из кешированного меню
        'category': product.category,
        'object': product,
        'same_products': get_same_products(product),
    }

    return render(request, 'mainapp/product_page.html', context)


def contact(request):
    if settings.LOW_CACHE:
        key = 'locations'
        locations = cache.get(key)
        if locations is None:
            with open('mainapp/json/locations.json', 'r', encoding='utf-8') as f:
                locations = json.load(f)  # dump
            cache.set(key, locations)
    else:
        with open('mainapp/json/locations.json', 'r', encoding='utf-8') as f:
            locations = json.load(f)  # dump

    context = {
        'page_title': 'контакты',
        'locations': locations,
    }

    return render(request, 'mainapp/contact.html', context)


# кеширование меню (memcached)
def get_links_meny():
    if settings.LOW_CACHE:
        key = 'links_menu'
        links_menu = cache.get(key)
        if links_menu is None:
            links_menu = ProductCategory.objects.filter(is_active=True)
            cache.set(key, links_menu)
        return links_menu
    else:
        return ProductCategory.objects.filter(is_active=True)


# кеширование категорий (memcached)
def get_category(pk):
    if settings.LOW_CACHE:
        key = 'category_' + str(pk)
        category = cache.get(key)
        if category is None:
            category = get_object_or_404(ProductCategory, pk=pk)
            cache.set(key, category)
        return category
    else:
        return get_object_or_404(ProductCategory, pk=pk)


# кеширование продуктов (memcached)
def get_products():
    if settings.LOW_CACHE:
        key = 'products'
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(is_active=True, category__is_active=True).select_related('category')
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(is_active=True, category__is_active=True).select_related('category')


# кеширование продукта (memcached)
def get_product(pk):
    if settings.LOW_CACHE:
        key = 'product_' + pk
        product = cache.get(key)
        if product is None:
            product = get_object_or_404(Product, pk=pk)
            cache.set(key, product)
        return product
    else:
        return get_object_or_404(Product, pk=pk)


# кеширование (memcached)
def get_products_ordered_by_price():
    if settings.LOW_CACHE:
        key = 'products_ordered_by_price'
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(is_active=True, category__is_active=True).order_by('price')
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(is_active=True, category__is_active=True).order_by('price')


# кеширование (memcached)
def get_products_in_category_ordered_by_price(pk):
    if settings.LOW_CACHE:
        key = 'products_in_category_ordered_by_price_' + str(pk)
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(category__pk=pk, 
                is_active=True, category__is_active=True).order_by('price')
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(category__pk=pk, 
            is_active=True, category__is_active=True).order_by('price')


def get_hot_product():
    products = get_products()

    return random.sample(list(products), 1)[0]