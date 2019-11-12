from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now


class ShopUser(AbstractUser):
    avatar = models.ImageField(upload_to='users_avatar',
                               blank=True)
    age = models.PositiveIntegerField(verbose_name='возраст', default=18)

    # код для email-подтверждения регистрации
    activation_key = models.CharField(verbose_name='ключ подтверждения',
                                      max_length=128,
                                      blank=True)
    activation_key_expires = models.DateTimeField(verbose_name='актуальность ключа',
                                                  default=(now() + timedelta(hours=48)))

    def is_activation_key_expired(self):
        if now() <= self.activation_key_expires:
            return False
        else:
            return True


class ShopUserProfile(models.Model):
    MALE = 'M'
    FEMALE = 'W'

    GENDER_CHOICES = (
        (MALE, 'М'),
        (FEMALE, 'Ж'),
    )

    user = models.OneToOneField(ShopUser,  # создание связи "один-к-одному"
                                unique=True,
                                null=False,
                                db_index=True,  # создает индекс для поля
                                on_delete=models.CASCADE)
    tagline = models.CharField(verbose_name='теги', max_length=128, blank=True)
    aboutMe = models.TextField(verbose_name='о себе', max_length=512, blank=True)
    gender = models.CharField(verbose_name='пол', max_length=1, choices=GENDER_CHOICES, blank=True)

    @receiver(post_save, sender=ShopUser)  # декоратор синхронизирования действий со связанной моделью
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            ShopUserProfile.objects.create(user=instance)

    @receiver(post_save, sender=ShopUser)
    def save_user_profile(sender, instance, **kwargs):
        instance.shopuserprofile.save()
        # Из модели ​ShopUser получить доступ к связанной модели по ее имени как к атрибуту
