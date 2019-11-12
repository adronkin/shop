from django.core.mail import send_mail
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from authapp.forms import ShopUserLoginForm, ShopUserRegisterForm, ShopUserUpdateForm, ShopUserProfileEditForm
from django.contrib import auth
from authapp.models import ShopUser
from mainapp.models import ProductCategory
from shop import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db import connection


def login(request):
    next = request.GET['next'] if 'next' in request.GET.keys() else None
    if request.method == 'POST':
        form = ShopUserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username,
                                     password=password)
            if user and user.is_active:
                next = request.POST['next'] if 'next' in request.POST.keys() else None
                # print(f'next: {next}')
                auth.login(request, user)
                return HttpResponseRedirect(reverse('main:index') if not next else next)
    else:
        form = ShopUserLoginForm()

    content = {
        'title': 'вход',
        'form': form,
        'next': next,
    }
    return render(request, 'authapp/login.html', content)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('main:index'))


def register(request):
    if request.method == 'POST':
        form = ShopUserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            if send_verify_mail(user):
                print('Сообщение подтверждения отправлено')
                return HttpResponseRedirect(reverse('authapp:login'))
            else:
                print('Ошибка отправки сообщения')
                return HttpResponseRedirect(reverse('authapp:login'))
    else:
        form = ShopUserRegisterForm()

    content = {
        'title': 'регистрация',
        'form': form,
    }
    return render(request, 'authapp/register.html', content)


def send_verify_mail(user):
    verify_link = reverse('authapp:verify', args=[user.email, user.activation_key])

    title = 'Подтверждение учетной записи пользователя ' + user.username
    message = 'Для подтверждения учетной записи пользователя ' + user.username + ' на портале ' + settings.DOMAIN_NAME + ' перейдите по ссылке: ' + settings.DOMAIN_NAME + verify_link

    print('from: ' + settings.EMAIL_HOST_USER + ', to: ' + user.email)
    return send_mail(title,
                     message,
                     settings.EMAIL_HOST_USER,
                     [user.email],
                     fail_silently=False,
                     )


def verify(request, email, activation_key):
    try:
        user = ShopUser.objects.get(email=email)
        if user.activation_key == activation_key and not user.is_activation_key_expired():
            print('user ', user, ' is activated')
            user.is_active = True
            user.save()
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return render(request, 'authapp/verification.html')
        else:
            print('error activation user: ' + user)
            return render(request, 'authapp/verification.html')
    except Exception as e:
        print('error activation user: ' + e.args)

    return HttpResponseRedirect(reverse('main:index'))


@login_required
@transaction.atomic
def edit(request):
    if request.method == 'POST':
        form = ShopUserUpdateForm(request.POST, request.FILES, instance=request.user)
        profile_form = ShopUserProfileEditForm(request.POST, instance=request.user.shopuserprofile)
        if form.is_valid() and profile_form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('authapp:update'))
    else:
        form = ShopUserUpdateForm(instance=request.user)
        profile_form = ShopUserProfileEditForm(instance=request.user.shopuserprofile)

    content = {
        'title': 'редактирование',
        'form': form,
        'profile_form': profile_form,
    }

    return render(request, 'authapp/update.html', content)


def db_profile_by_type(prefix, type, queries):
    update_queries = list(filter(lambda x: type in x['sql'], queries))
    print('db_profile {} for {}:'.format(type, prefix))
    # print('db_profile ' + type + ' for ' + prefix + ':')
    [print(query['sql']) for query in update_queries]


@receiver(pre_save, sender=ProductCategory)
def product_is_active_update_productcategory_save(sender, instance, **kwargs):
    if instance.pk:
        if instance.is_active:
            instance.product_set.update(is_active=True)
        else:
            instance.product_set.update(is_active=False)

# Атрибут «product_set Django» создан автоматически для связи с моделью Product по внешнему ключу. 
# В этом атрибуте получаем QuerySet, который позволяет получить все продукты в данной категории и применяем к нему метод «.update()».

        db_profile_by_type(sender, 'UPDATE', connection.queries)
