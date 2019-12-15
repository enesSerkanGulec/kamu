from django.urls import path
from .views import *

urlpatterns = [
    # path('bilgiler/', profil_sayfasi, {'islem': 'bilgiler'}, name='profil_bilgiler'),
    # path('parola/', profil_sayfasi, {'islem': 'parola'}, name='profil_parola'),
    path('malzemeler/', profil_sayfasi, {'islem': 'malzemeler'}, name='profil_malzemeler'),
    path('malzemeler/<int:id>', profil_sayfasi, {'islem': 'malzemeler', 'id': id}, name='profil_malzeme'),

    ]
