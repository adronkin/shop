from django.test import TestCase
from django.test.client import Client
from authapp.models import ShopUser
from django.core.management import call_command
from django.conf import settings


class TestUserManagement(TestCase):
	# Прописываем код подготовки к тест кейсам
	def setUp(self):
		# очищаем базу
		call_command('flush', '--noinput')
		# импортируем данные, имитирует команду в терминале "python​ ​manage​.py​ ​loaddata​ ​test_db​.json"
		call_command('loaddata', 'test_db.json')
		# создаем объект класса «Client» для отправки запросов
		self.client = Client()

		# создаем новых пользователей
		self.superuser = ShopUser.objects.create_superuser('django2', 'django2@shop.local', 'geekbrains')
		self.user = ShopUser.objects.create_user('ivan', 'ivan@shop.local', 'geekbrains')
		self.user_with_first_name = ShopUser.objects.create_user('petr', 'petr@shop.local', 'geekbrains', first_name='Петр')

	def test_user_login(self):
		# главная без логина
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)
		# Благодаря работе контекстного процессора «django.contrib.auth.context_processors.auth» объект пользователя всегда есть 
		# в контексте. Получаем его по ключу и проверяем при помощи метода «.assertTrue()» атрибут анонимности
		self.assertTrue(response.context['user'].is_anonymous)
		# Проверка заголовка
		self.assertEqual(response.context['page_title'], 'главная')
		# Если пользователь не залогинен - в меню не должно быть личного кабинета
		# Проверяет, что в ответе нет заданного текста, и код ответа
		self.assertNotContains(response, 'Пользователь', status_code=200)
		# Так же можно проверить при помощи метода «.assertNotIn()» - аналог Python-кода «not in», но передавать нужно
		# уже декодированный контент «response.content.decode()»
		# self.assertNotIn('Пользователь', response.context.decode())

		# данные пользователя
		self.client.login(username='ivan', password='geekbrains')

		# логинимся
		response = self.client.get('/auth/login/')
		self.assertFalse(response.context['user'].is_anonymous)
		self.assertEqual(response.context['user'], self.user)

		# главная после логина
		response = self.client.get('/')
		self.assertContains(response, 'Пользователь', status_code=200)
		self.assertEqual(response.context['user'], self.user)
		# self.assertIn('Пользователь', response.context.decode())

	def test_basket_login_redirect(self):
		# без логина должен переадресовывать
		response = self.client.get('/basket/')
		# через значение атрибута «.url» объекта ответа response проверяем правильность переадресации
		self.assertEqual(response.url, '/auth/login/?next=/basket/')
		self.assertEqual(response.status_code, 302)

		# с логином переходим в корзину
		self.client.login(username='ivan', password='geekbrains')

		response = self.client.get('/basket/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(list(response.context['basket']), [])
		self.assertEqual(response.request['PATH_INFO'], '/basket/')
		self.assertIn('Ваша корзина, Пользователь', response.content.decode())

	def test_user_logout(self):

		self.client.login(username='ivan', password='geekbrains')

		# логинимся
		response = self.client.get('/auth/login/')
		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.context['user'].is_anonymous)

		# выходим из системы
		response = self.client.get('/auth/logout/')
		self.assertEqual(response.status_code, 302)

		# главная после выхода
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.context['user'].is_anonymous)

	# регистрация пользователя с отправкой подтверждения по почте
	def test_user_register(self):
		# логин без данных пользователя
		response = self.client.get('/auth/register/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['title'], 'регистрация')
		self.assertTrue(response.context['user'].is_anonymous)

		new_user_data = {
			'username': 'soso',
			'first_name': 'Сосо',
			'last_name': 'Павлиашвили',
			'password1': 'geekbrains',
			'password2': 'geekbrains',
			'email': 'soso@shop.local',
			'age': '55'
		}

		# Передачу данных регистрируемого пользователя с формы реализуем при помощи метода «.post()», 
		# в который передаем их по ключу «data»
		response = self.client.post('/auth/register/', data=new_user_data)
		self.assertEqual(response.status_code, 302)

		new_user = ShopUser.objects.get(username=new_user_data['username'])

		# После подтверждения регистрации необходимо залогиниться и проверить ссылку на личный кабинет 
		# в меню на главной странице - в ней должно быть имя пользователя.
		activation_url = settings.DOMAIN_NAME + '/auth/verify/' + new_user_data['email'] + '/' + new_user.activation_key + '/'

		response = self.client.get(activation_url)
		self.assertEqual(response.status_code, 200)

		# данные нового пользователя
		self.client.login(username=new_user_data['username'],
			password=new_user_data['password1'])

		# логинимся
		response = self.client.get('/auth/login/')
		self.assertEqual(response.status_code, 200)
		self.assertFalse(response.context['user'].is_anonymous)

		# проверяем главную страницу
		response = self.client.get('/')
		self.assertContains(response, text=new_user_data['first_name'], status_code=200)

	def test_user_wrong_register(self):
		new_user_data = {
			'username': 'ignat',
			'first_name': 'Игнат',
			'last_name': 'Игнатов',
			'password1': 'geekbrains',
			'password2': 'geekbrains',
			'email': 'ignat@shop.local',
			'age': '17'
		}

		# Передачу данных регистрируемого пользователя с формы реализуем при помощи метода «.post()», 
		# в который передаем их по ключу «data»
		response = self.client.post('/auth/register/', data=new_user_data)
		self.assertEqual(response.status_code, 200)
		# ввели некорректный возраст и проверили ошибку формы при помощи метода «.assertFormError()»:
		# второй аргумент - имя формы, третий - поле. В четвертом - передаем текст ожидаемой ошибки.
		self.assertFormError(response, 'form', 'age', 'Вы слишком молоды')

	def tearDown(self):
		call_command('sqlsequencereset', 'mainapp', 'authapp', 'ordersapp', 'basketapp')
