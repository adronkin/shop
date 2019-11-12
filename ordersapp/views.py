from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db import transaction
from django.db.models import F

from django.forms import inlineformset_factory

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from basketapp.models import Basket
from mainapp.models import Product
from ordersapp.models import Order, OrderItem
from ordersapp.forms import OrderItemForm

from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required


class OrderList(ListView):
	model = Order

	def get_queryset(self):  # переопределение метода, чтобы пользователь видел только свои заказы
		return Order.objects.filter(user=self.request.user)

	@method_decorator(login_required())
	def dispatch(self, *args, **kwargs):
		return super(ListView, self).dispatch(*args, **kwargs)


class OrderItemsCreate(CreateView):
	model = Order
	fields = []  # Список полей пустой, так как в соответствии с моделью все они, кроме пользователя «user»,
	# создаются автоматически.
	success_url = reverse_lazy('ordersapp:orders_list')

	def get_context_data(self, **kwargs):
		# получаем текущий контекст
		data = super(OrderItemsCreate, self).get_context_data(**kwargs)
		OrderFormSet = inlineformset_factory(Order,
											 OrderItem,
											 form=OrderItemForm,
											 extra=1)  # пустая форма для добавления продуктов в заказ

		# После того, как пользователь нажмет на форме кнопку «Сохранить», создаем набор форм заново на основе данных
		# формы, переданных методом POST
		if self.request.POST:
			formset = OrderFormSet(self.request.POST)
		else:
			basket_items = Basket.get_items(self.request.user)
			# если корзина не пустая
			if len(basket_items):
				# обеспечиваем создание элементов заказа одновременно с самим заказом
				OrderFormSet = inlineformset_factory(Order,  # родительский класс
													 OrderItem,
													 # класс, на основе которого будет создаваться набор форм класса,
													 # указанного в именованном аргументе «form=OrderItemForm»
													 form=OrderItemForm,
													 # создаем набор в котором число форм = числу объектов в корзине
													 extra=len(basket_items))
				formset = OrderFormSet()
				# Заполняем в каждой форме поля «product» и «quantity». Чистим корзину.
				for num, form in enumerate(formset.forms):
					form.initial['product'] = basket_items[num].product
					form.initial['quantity'] = basket_items[num].quantity
					form.initial['price'] = basket_items[num].product.price
				basket_items.delete()
			else:
				# Если корзина пустая - создаем набор с одной чистой формой.
				formset = OrderFormSet()

		# добавляем данные в контекст
		data['orderitems'] = formset
		return data

	# валидация формы
	def form_valid(self, form):
		# получаем набор форм из контекста
		context = self.get_context_data()
		orderitems = context['orderitems']

		# Сохранение заказа и его элементов лучше выполнять как атомарную операцию - если произойдет сбой,
		# вообще никакие данные не сохранятся. Воспользуемся для этого методом «atomic()» модуля
		# «django.db.transaction»
		with transaction.atomic():
			# Чтобы форма создания самого заказа прошла валидацию перед сохранением, необходимо задать обязательный
			# для модели класса «Order»  атрибут «user»
			form.instance.user = self.request.user
			self.object = form.save()
			if orderitems.is_valid():
				orderitems.instance = self.object
				orderitems.save()

		# удаляем пустой заказ
		get_sum = self.object.get_summary()
		if get_sum.get('total_cost') == 0:
			self.object.delete()

		return super(OrderItemsCreate, self).form_valid(form)

	@method_decorator(login_required())
	def dispatch(self, *args, **kwargs):
		return super(CreateView, self).dispatch(*args, **kwargs)


class OrderItemsUpdate(UpdateView):
	model = Order
	fields = []  # Список полей пустой, так как в соответствии с моделью все они, кроме пользователя «user»,
	# создаются автоматически.
	success_url = reverse_lazy('ordersapp:orders_list')

	def get_context_data(self, **kwargs):
		# получаем текущий контекст
		data = super(OrderItemsUpdate, self).get_context_data(**kwargs)
		OrderFormSet = inlineformset_factory(Order,
											 OrderItem,
											 form=OrderItemForm,
											 extra=1)  # пустая форма для добавления продуктов в заказ

		# После того, как пользователь нажмет на форме кнопку «Сохранить», создаем набор форм заново на основе данных
		# формы, переданных методом POST
		if self.request.POST:
			data['orderitems'] = OrderFormSet(self.request.POST,
											  instance=self.object)
		else:
			# для вывода цены в форме
			queryset = self.object.orderitems.select_related()  # оптимизация запроса
			formset = OrderFormSet(instance=self.object, queryset=queryset)
			for form in formset.forms:
				if form.instance.pk:
					form.initial['price'] = form.instance.product.price
			data['orderitems'] = formset
		return data

	# валидация формы
	def form_valid(self, form):
		# получаем набор форм из контекста
		context = self.get_context_data()
		orderitems = context['orderitems']

		# Сохранение заказа и его элементов лучше выполнять как атомарную операцию - если произойдет сбой,
		# вообще никакие данные не сохранятся. Воспользуемся для этого методом «atomic()» модуля
		# «django.db.transaction»
		with transaction.atomic():
			# Чтобы форма создания самого заказа прошла валидацию перед сохранением, необходимо задать обязательный
			# для модели класса «Order»  атрибут «user»
			self.object = form.save()
			if orderitems.is_valid():
				orderitems.instance = self.object
				orderitems.save()

		# удаляем пустой заказ
		get_sum = self.object.get_summary()
		if get_sum.get('total_cost') == 0:
			self.object.delete()

		return super(OrderItemsUpdate, self).form_valid(form)

	@method_decorator(login_required())
	def dispatch(self, *args, **kwargs):
		return super(UpdateView, self).dispatch(*args, **kwargs)


class OrderRead(DetailView):
	model = Order

	def get_context_data(self, **kwargs):
		context = super(OrderRead, self).get_context_data(**kwargs)
		context['title'] = 'заказ/просмотр'
		return context

	@method_decorator(login_required())
	def dispatch(self, *args, **kwargs):
		return super(DetailView, self).dispatch(*args, **kwargs)


class OrderDelete(DeleteView):
	model = Order
	success_url = reverse_lazy('ordersapp:orders_list')


def order_forming_complete(request, pk):
	order = get_object_or_404(Order, pk=pk)
	# После перехода пользователя по ссылке ​«​совершить покупку​»​ будет установлен статус заказа:
	order.status = Order.SENT_TO_PROCEED
	order.save()
	return HttpResponseRedirect(reverse('ordersapp:orders_list'))


# обновление кол-ва товаров на складе
# «sender»​ - класс отправителя
# «update_fields»​ - имена обновляемых полей
# «instance»​ - сам обновляемый объек
@receiver(pre_save, sender=OrderItem)
@receiver(pre_save, sender=Basket)
def product_quantity_update_save(sender, update_fields, instance, raw, **kwargs):
	if update_fields is 'quantity' or 'product' and not raw:
		# Проверяем, новый это объект или уже существующий
		if instance.pk:
			instance.product.quantity = F('quantity') - (instance.quantity - sender.get_item(instance.pk).quantity)
			# instance.product.quantity -= instance.quantity - sender.get_item(instance.pk).quantity
		else:
			instance.product.quantity = F('quantity') - instance.quantity
			# instance.product.quantity -= instance.quantity
		instance.product.save()


@receiver(pre_delete, sender=OrderItem)
@receiver(pre_delete, sender=Basket)
def product_quantity_update_delete(sender, instance, **kwargs):
	instance.product.quantity = F('quantity') + instance.quantity
	instance.product.save()


# для автообновления цены при добавлении продукта в заказ
def get_product_price(request, pk):
	if request.is_ajax():
		product = Product.objects.filter(pk=int(pk)).first()
		if product:
			return JsonResponse({'price': product.price})
		else:
			return JsonResponse({'price': 0})
