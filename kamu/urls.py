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
    path('chaining/', include('smart_selects.urls')),
    path('logout/', views.logoutt, name='cikisislemi'),
    path('', views.welcomeislemi),
    path('', views.welcomeislemi, name='girisislemi'),
    path('welcome/<int:islem>/', views.welcomeislemi, name='karsilamaislemi'),
    path('anasayfa/', views.anasayfa, name='anasayfaislemi'),
    path('islem/<int:id>/<str:islem>', views.anasayfa, name='islemler'),
    path('bilgiler/<str:islem>', views.bilgiler, name='hesapbilgileriislemi'),
    path('ilanlar/', views.ilanlarim, name='ilanlarimislemi'),
    path('ilandetay/<int:id>', views.ilan_detay, name='ilandetayislemi'),
    path('yeniilan/', views.yeni_ilan, name='yeniilanislemi'),
    path('favoriler/', views.favorilerim, name='favoriislemi'),
    path('favoricikar/<int:id>/<str:islem>', views.favorilerim, name='favoricikar'),
    path('iller/', views.il_ilce_veritanamını_aktar),
    path('ilan_inceleme/<int:id>/<str:islem>', views.ilan_incele, name='ilan_inceleme'),
    path('ilan/<int:id>/<str:islem>', views.ilan_incele, name='ilan_inceleme_favori'),
    path('mesajlarim/<str:filitre>', views.mesajlarim, name='mesajlarimislemi'),
    path('mesajlarim/', views.mesajlarim, name='tummesajlarimislemi'),
    path('mesajlarim/<str:filitre>/<int:id>/<str:islem>', views.mesajlarim, name='mesajdaislemyap'),
    path('ilan_mesajlari/<int:mesaj_id>', views.ilanMesajlari, name='ilanMesajlari'),
    path('gorus/', views.gorusSayfasi),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
