"""kamu URL Configuration

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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from app import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('logout/', views.logoutt, name='cikisislemi'),
    path('profil/', include('app.urls')),
    path('', views.welcomeislemi),
    path('welcome/<int:islem>/', views.welcomeislemi, name='karsilamaislemi'),
    path('anasayfa/', views.anasayfa, name='anasayfaislemi'),
    path('bilgiler/<str:islem>', views.bilgiler, name='hesapbilgileriislemi'),
    path('ilanlar/', views.ilanlarim, name='ilanlarimislemi'),
    path('ilandetay/<int:id>', views.ilan_detay, name='ilandetayislemi'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
