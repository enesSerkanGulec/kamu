from django import template
from app.models import Mesaj

register = template.Library()


@register.filter
def yeni_filitre_olustur(eskiFiltre, eklenecek):
    e = eklenecek.split(':')
    f = eskiFiltre.split('-')
    if e[0] == 'ilgili':
        f[0] = 'ilgili:' + e[1]
    elif e[0] == 'yon':
        f[1] = 'yon:' + e[1]
    elif e[0] == 'durum':
        f[2] = 'durum:' + e[1]
    elif e[0] == 'zaman':
        f[3] = 'zaman:' + e[1]
    s = ''
    for x in f:
        if s:
            s = s + '-'
        s = s + x
    return s

@register.filter
def degerGetir(filitre, hangisini):
    f = filitre.split('-')
    x = ''
    if hangisini == 'ilgili':
        x = f[0].split(':')[1].upper()
    elif hangisini == 'yon':
        x = f[1].split(':')[1].upper()
    elif hangisini == 'durum':
        x = f[2].split(':')[1].upper()
    elif hangisini == 'zaman':
        x = f[3].split(':')[1].upper()

    if x == 'HEPSI':
        x = ''
    else:
        x = ': ' + x
    return x

@register.filter
def mesajSahisGetir(mesaj, user_id):
    s = mesaj.gonderenKim(user_id)
    if s != 'Ben':
        return s
    else:
        return mesaj.gonderilenKim(user_id)


@register.filter
def mesajGelenMi(mesaj, user_id):
    return mesaj.gonderilen_id == user_id


@register.filter
def mesajSahisBilgileriGetir(mesaj, user_id):
    s = mesajSahisGetir(mesaj,user_id)

@register.filter
def mesaj_gelen(mesaj, user_id):
    return mesaj.gonderilenKim(user_id) == 'Ben'


# @register.filter
# def birlestir(str1, str2):
#     return str(str1) + str(str2)


# @register.filter
# def deger_ben_degil(deger):
#     return deger != 'Ben'
#
#
# @register.filter()
# def mesajOkundu_yap(mesaj):
#     mesaj.okundu = True
#     mesaj.save()
#     return None
