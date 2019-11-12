from django.test import TestCase
from mainapp.models import Product, ProductCategory

class ProductsTestCase(TestCase):
	def setUp(self):
		category = ProductCategory.objects.create(name='коробки на 4 кольца')
		self.product_1 = Product.objects.create(name='коробка 1',
			category=category,
			price=777,
			quantity=111)

		self.product_2 = Product.objects.create(name='коробка 2',
			category=category,
			price=888.5,
			quantity=222,
			is_active=False)

		self.product_3 = Product.objects.create(name='коробка 3',
			category=category,
			price=123.1,
			quantity=87)

	def test_product_get(self):
		product_1 = Product.objects.get(name='коробка 1')
		product_2 = Product.objects.get(name='коробка 2')
		self.assertEqual(product_1, self.product_1)
		self.assertEqual(product_2, self.product_2)

	def test_product_print(self):
		product_1 = Product.objects.get(name='коробка 1')
		product_2 = Product.objects.get(name='коробка 2')
		self.assertEqual(str(product_1), 'коробка 1 (коробки на 4 кольца)')
		self.assertEqual(str(product_2), 'коробка 2 (коробки на 4 кольца)')

	def test_product_get_items(self):
		product_1 = Product.objects.get(name='коробка 1')
		product_3 = Product.objects.get(name='коробка 3')
		products = product_1.get_items()

		self.assertEqual(list(products), [product_1, product_3])
		