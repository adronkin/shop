from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django.forms import HiddenInput

from authapp.models import ShopUser
from mainapp.models import ProductCategory, Product


class ShopUserAdminCreateForm(UserCreationForm):
    class Meta:
        model = ShopUser
        fields = ('username', 'first_name', 'password1', 'password2', 'email', 'age', 'avatar')

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            for field_name, field in self.fields.item():
                field.widget.attrs['class'] = 'form-control'
                field.help_text = ''

        def clean_age(self):
            data = self.cleaned_data['age']
            if data < 18:
                raise forms.ValidationError('Вы слишком молоды')

            return data


class ShopUserAdminUpdateForm(UserChangeForm):
    class Meta:
        model = ShopUser
        fields = ('username', 'first_name', 'last_name', 'email',
                  'age', 'avatar', 'password', 'is_superuser', 'is_active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.help_text = ''
            if field_name == 'password':
                field.widget = HiddenInput()

    def clean_age(self):
        data = self.cleaned_data['age']
        if data < 18:
            raise forms.ValidationError('Вы слишком молоды')

        return data


class ProductCategoryAdminUpdateForm(forms.ModelForm):
    discount = forms.IntegerField(label='скидка', 
        required=False,  # заполнять не обязательно (для исклчения проблем с валидацией)
        min_value=0, 
        max_value=90,
        initial=0)  # начальное значение

    class Meta:
        model = ProductCategory
        # fields = '__all__'
        exclude = ()  # кортеж с исключенными из отображения полями

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    # def __init__(self, *args, **kwargs):
    #     super(ProductCategoryEditForm, self).__init__(*args, **kwargs)
    #     for field_name, field in self.fields.items():
    #         field.widget.attrs['class'] = 'form-control'
    #         field.help_text = ''


class ProductAdminUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
