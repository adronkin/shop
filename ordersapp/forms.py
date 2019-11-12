from django import forms

from mainapp.models import Product, ProductCategory
from ordersapp.models import Order, OrderItem


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('user',)  # поля, которые необходимо исключить из формы

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class OrderItemForm(forms.ModelForm):
    price = forms.CharField(label='цена', required=False)  # для вывода цены товара в форму

    class Meta:
        model = OrderItem
        exclude = ()  # поля, которые необходимо исключить из формы
        # поле не должно сохраняться в базу и проходить валидацию - задаем аргумент «required=False​»

    def __init__(self, *args, **kwargs):
        super(OrderItemForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        self.fields['product'].queryset = Product.get_items().select_related()  # Убираем из каталога неактивные продукты
