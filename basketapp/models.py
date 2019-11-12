from django.conf import settings
from django.db import models
from mainapp.models import Product
from django.utils.functional import cached_property


# класс для работы с QuerySet (2 метод изменения кол-ва на складе)
# class BasketQuerySet(models.QuerySet):
#
#     def delete(self, *args, **kwargs):
#         for object in self:
#             object.product.quantity += object.quantity
#             object.product.save()
#         super(BasketQuerySet, self).delete(*args, **kwargs)


class Basket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='basket')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='количество', default=0)
    add_datetime = models.DateTimeField(verbose_name='время', auto_now_add=True)
    # переменная для изменения продуктов на складе (2 метод изменения кол-ва на складе)
    # objects = BasketQuerySet.as_manager()

    # кеширование в корзине
    @cached_property
    def get_items_cached(self):
        returnself.user.basket.select_related()

    # кеширование кол-ва
    def get_tital_quantity(self):
        _items = self.get_items_cached
        return sum(list(map(lambda x: x.quantity, _items)))

    # кеширование общей стоимости
    def get_total_cost(self):
        _items = self.get_items_cached
        return sum(list(map(lambda x: x.product_cost, _items)))

    @property
    def product_cost(self):
        """возвращает цену продуктов одного типа (в корзине)"""
        return self.product.price * self.quantity

    @property
    def total_quantity(self):
        """возвращает кол-во продуктов в корзине"""
        return sum([el.quantity for el in self.user.basket.all()])

    @property
    def total_coast(self):
        """возвращает общую цену всех продуктов в корзине"""
        return sum([el.product_cost for el in self.user.basket.all()])

    @staticmethod
    def get_items(user):
        return Basket.objects.filter(user=user).order_by('product__category')

    @staticmethod
    def get_item(pk):
        return Basket.objects.filter(pk=pk).first()

    # переопределяем метод сохранения объекта (2 метод изменения кол-ва на складе)
    # def save(self, *args, **kwargs):
    #     if self.pk:
    #         self.product.quantity -= self.quantity - self.__class__.get_item(self.pk).quantity
    #     else:
    #         self.product.quantity -= self.quantity
    #     self.product.save()
    #     super(self.__class__, self).save(*args, **kwargs)

    # переопределяем метод удаления объекта (2 метод изменения кол-ва на складе)
    # def delete(self):
    #     self.product.quantity += self.quantity
    #     self.product.save()
    #     super(self.__class__, self).delete()
