from django.test import TestCase
from django.test.client import Client
from mainapp.models import Product, ProductCategory
from django.core.management import call_command

class TestMainappSmoke(TestCase):
	# Прописываем код подготовки к тест кейсам
	def setUp(self):
		# очищаем базу
		call_command('flush', '--noinput')
		# импортируем данные, имитирует команду в терминале "python​ ​manage​.py​ ​loaddata​ ​test_db​.json"
		call_command('loaddata', 'test_db.json')
		# создаем объект класса «Client» для отправки запросов
		self.client = Client()

	def test_mainapp_urls(self):
		# сохраняем в переменной объект ответа на запрос
		response = self.client.get('/')
		# assertEqual - метод сверки реального и ожидаемого ответа
		self.assertEqual(response.status_code, 200)

		response = self.client.get('/contact/')
		self.assertEqual(response.status_code, 200)

		response = self.client.get('/category/0/')
		self.assertEqual(response.status_code, 200)

		for category in ProductCategory.objects.all():
			response = self.client.get('/category/{}/'.format(category.pk))
			self.assertEqual(response.status_code, 200)

		for product in Product.objects.all():
			response = self.client.get('/product/{}/'.format(product.pk))
			self.assertEqual(response.status_code, 200)

	# Так как разные БД по-разному работают с индексами при создании новых элементов - добавили в метод «.tearDown()», 
	# выполняющийся всегда по завершении тестов в классе, команду сброса индексов:
	def tearDown(self):
		call_command('sqlsequencereset', 'mainapp', 'authapp', 'ordersapp', 'basketapp')
