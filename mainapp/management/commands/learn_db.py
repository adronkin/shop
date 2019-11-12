from django.core.management.base import BaseCommand
from mainapp.models import ProductCategory, Product
from ordersapp.models import Order, OrderItem
from django.db import connection
from django.db.models import Q, F, When, Case, DecimalField, IntegerField
from adminapp.views import db_profile_by_type
from datetime import timedelta


class Command(BaseCommand):
	def handle(self, *args, **options):
		# test_products = Product.objects.filter(
		# 	Q(category__name='на 1 кольцо') |
		# 	Q(category__name='на 2 кольца')
		# 	)

		# print(test_products)
		# # print(len(test_products))

		# db_profile_by_type('learn db', '', connection.queries)

		# Выводим данные о величине скидки на каждый элемент заказа с учетом акции. Сначала выводим позиции, которые попали под первую акцию
		# в порядке увеличения выгоды. Затем позиции, которые попали под вторую акцию в порядке уменьшения выгоды. 
		# Потом - остальные позиции, в порядке увеличения выгоды. Таким образом получим своего рода волны, по которым можно найти самые выгодные
		# товары на границах акций. Чтобы сэкономить время и не создавать новых атрибутов модели, будем считать датой оплаты заказа значение
		# его атрибута «updated». На самом деле в будущем для хранения даты оплаты можем создать, например, атрибут «paid».

		# Создаем константы для сортировки результатов
		ACTION_1 = 1
		ACTION_2 = 2
		ACTION_EXPIRED = 3

		# Создаем параметры для сортировки результатов
		# Параметр времени действия акции
		action_1__time_delta = timedelta(hours=12)
		action_2__time_delta = timedelta(days=1)

		# Параметр скидки по акции
		action_1__discount = 0.3
		action_2__discount = 0.15
		action_expired__discount = 0.05

		# Условия выполнения акции
		action_1__condition = Q(order__updated__lte=F('order__created') + action_1__time_delta)
		action_2__condition = Q(order__updated__gt=F('order__created') + action_1__time_delta) &\
							  Q(order__updated__lte=F('order__created') + action_2__time_delta)
		action_expired__condition = Q(order__updated__gt=F('order__created') + action_2__time_delta)

		# When - возвращает данные при выполнении условия. Элемент 1 - условие, 2 - возвращаемое значение.
		# Возвращаем константу для сортировки
		action_1__order = When(action_1__condition, then=ACTION_1)
		action_2__order = When(action_2__condition, then=ACTION_2)
		action_expired__order = When(action_expired__condition, then=ACTION_EXPIRED)

		# Возвращаем цену с учетом скидки
		action_1__price = When(action_1__condition, 
			then=F('product__price') * F('quantity') * action_1__discount)
		action_2__price = When(action_2__condition, 
			then=F('product__price') * F('quantity') * action_2__discount)
		action_expired__price = When(action_expired__condition, 
			then=F('product__price') * F('quantity') * action_expired__discount)

		# При помощи метода «.annotate()» добавляем поля аннотаций «action_order» и «total_price» к каждому объекту QuerySet. 
		# Сортируем результаты по этим полям и подгружаем данные связанных моделей для уменьшения количества запросов.

		# Для заполнения полей аннотаций используем объект Django-ORM класса «​Case​», который позволяет реализовать в запросах логику 
		# условного оператора «if», «then», «elif», «then».

		# В конструктор «Case» позиционными аргументами передаем заранее созданные объекты классе «​When​», 
		# возвращающие данные при выполнении определенного условия.
		test_orders = OrderItem.objects.annotate(
			action_order=Case(
				action_1__order,
				action_2__order,
				action_expired__order,
				output_field=IntegerField(),
				)).annotate(
				total_price=Case(
					action_1__price,
					action_2__price,
					action_expired__price,
					output_field=DecimalField(),
					)).order_by('action_order', 'total_price').select_related()

		# for orderitem in test_orders:
		# 	print('{}: заказ №{}:\
		# 		{}: скидка\
		# 		{} руб. | \
		# 		{}'.format(orderitem.action_order:2, orderitem.pk:3, orderitem.product.name:15,\
		# 		 abs(orderitem.total_price):6.2f, orderitem.order.updated - orderitem.order.created)

		for orderitem in test_orders:
			print(orderitem.action_order, ' : заказ №:', orderitem.order.pk, \
				orderitem.product.name, ': скидка ', \
				round(abs(orderitem.total_price), 2), ' руб. | ', \
				orderitem.order.updated - orderitem.order.created)
