"""shop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
	1. Add an import:  from my_app import views
	2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
	1. Add an import:  from other_app.views import Home
	2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
	1. Import the include() function: from django.urls import include, path
	2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, re_path
from django.conf import settings  # чтобы Django раздавал медиафайлы на этапе разработки
from django.conf.urls.static import static  # чтобы Django раздавал медиафайлы на этапе разработки

urlpatterns = [
	re_path(r'^', include('mainapp.urls', namespace='main')),
	re_path(r'^auth/', include('authapp.urls', namespace='auth')),
	re_path(r'^basket/', include('basketapp.urls', namespace='basket')),
	re_path(r'^myadmin/', include('adminapp.urls', namespace='myadmin')),
	re_path(r'^order/', include('ordersapp.urls', namespace='order')),

	re_path(r'^', include('social_django.urls', namespace='social')),  # аутентификация через соц сети

	re_path(r'^admin/', admin.site.urls),
]

if settings.DEBUG:

	import debug_toolbar

	urlpatterns += [re_path(r'^__debug__/', include(debug_toolbar.urls))]
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
	# сообщить Django, что нужно папку на диске ​MEDIA_ROOT ​сделать доступной по сетевому адресу ​MEDIA_URL
