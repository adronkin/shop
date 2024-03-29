from django.conf import settings
from django.db import models

from mainapp.models import Product


class Order(models.Model):
    FORMING = 'FM'
    SENT_TO_PROCEED = 'STP'
    PROCEEDED = 'PRD'
    PAID = 'PD'
    READY = 'RDY'
    CANCEL = 'CNC'

    ORDER_STATUS_CHOICES = (
        (FORMING, 'формируется'),
        (SENT_TO_PROCEED, 'отправлен в работу'),
        (PROCEEDED, 'обрабатывается'),
        (PAID, 'оплачен'),
        (READY, 'готов к выдаче'),
        (CANCEL, 'отменен'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created = models.DateTimeField(verbose_name='создан', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='обновлен', auto_now=True)
    status = models.CharField(verbose_name='статус',
                              max_length=3,
                              choices=ORDER_STATUS_CHOICES,
                              default=FORMING)
    is_active = models.BooleanField(verbose_name='активен', default=True, db_index=True)

    class Meta:
        ordering = ('-created',)  # сортировка в обратном порядке
        verbose_name = 'заказ'  # имя класса в единственном числе
        verbose_name_plural = 'заказы'  # имя класса во множественном числе

    def __str__(self):
        return 'Текущий заказ: ' + self.id

    # объединение get_total_quantity и get_total_cost для кеширования через with
    def get_summary(self):
        items = self.orderitems.select_related()
        return {
            'total_cost': sum(list(map(lambda x: x.quantity * x.product.price, items))),
            'total_quantity': sum(list(map(lambda x: x.quantity, items)))
        }


    def get_product_type_quantity(self):
        items = self.orderitems.select_related()
        return len(items)

    # переопределяем метод удаляющий объект
    def delete(self):
        for item in self.orderitems.select_related():
            # корректируем остатки продуктов на складе
            item.product.quantity += item.quantity
            item.product.save()

        self.is_active = False
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order,
                              related_name='orderitems',  # дает доступ к элементам заказа через атрибут 'orderitems'
                              on_delete=models.CASCADE)
    product = models.ForeignKey(Product,
                                verbose_name='продукт',
                                on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='количество',
                                           default=0)
    # переменная для изменения продуктов на складе (2 метод изменения кол-ва на складе)
    # objects = OrderItemQuerySet.as_manager()

    def get_product_cost(self):
        return self.product.price * self.quantity

    @staticmethod
    def get_item(pk):
        return OrderItem.objects.filter(pk=pk).first()
