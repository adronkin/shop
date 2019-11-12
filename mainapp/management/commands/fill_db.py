import json
import os

from django.core.management.base import BaseCommand

from authapp.models import ShopUser
from mainapp.models import ProductCategory, Product
from django.conf import settings


def load_from_json(file_name):
    with open(os.path.join(settings.JSON_PATH, file_name + '.json'),
              'r',
              encoding='utf-8') as infile:
        return json.load(infile)


class Command(BaseCommand):
    help = 'Fill DB new data'

    def handle(self, *args, **options):
        categories = load_from_json('categories')

        ProductCategory.objects.all().delete()
        for category in categories:
            ProductCategory.objects.create(**category)
            new_category = ProductCategory(**category)

        products = load_from_json('products')
        Product.objects.all().delete()
        for product in products:
            # Заменяем название категории объектом
            product['category'] = ProductCategory.objects.get(name=product['category'])
            Product.objects.create(**product)

        # Проверяем есть ли пользователь в базе и создаем с помощью менеджера модели
        if not ShopUser.objects.filter(username='django').exists():
            super_user = ShopUser.objects.create_superuser('django',
                                                           'django@shop.local',
                                                           'geekbrains',
                                                           age=31)
