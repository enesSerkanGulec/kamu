from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import Http404
from .forms import *
from django.contrib import messages
from .models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django import views
from django.forms import formset_factory, modelformset_factory


def welcomeislemi(request, islem=1):
    if islem == 1:
        form = GirisFormu(request.POST or None,)
    elif islem == 2:
        form = KayitFormu(request.POST or None)
    else: #elif islem == 'sifremiunuttum':
        form = SifreUnuttumFormu(request.POST or None)

    if form.is_valid():
        if islem == 1:
            data = form.cleaned_data
            user = authenticate(email=data['email'], password=data['sifre'])
            if user is not None:
                login(request, user)
                return redirect('anasayfaislemi')
            else:
                messages.error(request, "Parola Hatalı")
        elif islem == 2:
            eposta = request.POST['email']
            form.save()
            messages.success(request, 'Talebinizi aldık. E-posta hesabınıza bilgilendirme mesajı gönderilecektir.')
            return redirect(welcomeislemi)
        else:
            s = User.objects.make_random_password()
            adres = form.cleaned_data['email']
            try:
                user = User.objects.get(email=adres)
                send_mail(subject='Yeni Şifreniz..', message='Yeni şifreniz: {} dir.'.format(s),
                          from_email=settings.EMAIL_FROM, recipient_list=[adres, ], fail_silently=False)
                user.set_password(s)
                user.save()
                messages.success(request, "Yeni şifreniz e-posta hesabınıza ({}) gönderilmiştir.".format(adres))
                return welcomeislemi(request, 1)
            except:
                messages.error(request, 'Bir hata oluştu.')
    return render(request, 'karsilama.html', {'form': form, 'islem': islem})


# def kayit(request):
#     form = KayitFormu(request.POST or None)
#     if form.is_valid():
#         eposta = request.POST['email']
#         form.save()
#         messages.success(request, 'Talebinizi aldık. E-posta hesabınıza bilgilendirme mesajı gönderilecektir.')
#         return redirect('girisislemi')
#     return render(request, 'karsilama.html', {'form': form})


def logoutt(request):
    logout(request)
    return welcomeislemi(request, 1)


# def loginn(request):
#     form = GirisFormu(request.POST or None)
#     if form.is_valid():
#         data = form.cleaned_data
#         user = authenticate(email=data['email'], password=data['sifre'])
#         if user is not None:
#             login(request, user)
#             return anasayfa(request)
#         else:
#             messages.error(request, "Parola Hatalı")
#     return render(request, 'Silinecekler/login.html', {'form': form})


# def sifre_unuttum(request):
#     form = SifreUnuttumFormu(request.POST or None)
#     if form.is_valid():
#         s = User.objects.make_random_password()
#         adres = form.cleaned_data['email']
#         try:
#             user = User.objects.get(email=adres)
#             send_mail(subject='Yeni Şifreniz..', message='Yeni şifreniz: {} dir.'.format(s),
#                       from_email=settings.EMAIL_FROM, recipient_list=[adres, ], fail_silently=False)
#             user.set_password(s)
#             user.save()
#             messages.success(request, "Yeni şifreniz e-posta hesabınıza ({}) gönderilmiştir.".format(adres))
#             return redirect('girisislemi')
#         except:
#             messages.error(request, 'Bir hata oluştu.')
#     return render(request, 'Silinecekler/sifreunuttum.html', {'form': form})

@login_required(login_url='girisislemi')
def bilgiler(request, islem):
    if islem == 'bilgiler':
        form = BilgilerFormu(data=request.POST or None, instance=request.user)
    elif islem == 'parola':
        form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Yapılan değişiklikler kaydedildi.')
    return render(request, 'bilgiler.html', {'form': form})


@login_required(login_url='girisislemi')
def profil_sayfasi(request, islem, id=None):
    user = request.user
    form = None
    formset = None
    if islem == 'bilgiler':
        form = BilgilerFormu(request.POST or None, instance=request.user)
    elif islem == 'malzemeler':
        # malzeme_formset = modelformset_factory(ilan, İlanFormu)
        # formset = malzeme_formset(queryset=ilan.objects.filter(sahip=request.user))
        form = ilan.objects.filter(sahip=request.user)
    elif islem == 'parola':
        form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST':
        if id == 1 or id == 3:
            if form.is_valid():
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                messages.success(request, 'Yapılan değişiklikler kaydedildi.')
        else:
            silinecek_id = request.POST.get('silinecek')
            _malzeme = ilan.objects.get(id=silinecek_id)
            _malzeme.delete()
            messages.success(request, 'ilan silindi')
            # for f in formset:
            #     f.save()
            #     formset.sa
    return render(request, 'Silinecekler/tabprofil.html', {'form': form, 'islem': islem, 'id': id, 'formset': formset})


@login_required(login_url='/welcome/1/')
def anasayfa(request, id=None, islem=None):
    mesaj_formu = mesajFormu(request.POST or None)
    if id:
        i = get_object_or_404(ilan, id=id)
        if islem == 'favorieklecikar':
            if not i.yayinda:
                raise Http404("İlan yayında değil. Silinmişde olabilir.")
            else:
                i.favorilere_ekle_cikar(user=request.user)
    elif request.method == 'POST':
        if 'mesaj' in request.POST:
            if mesaj_formu.is_valid():
                id = request.POST.get('mesaj').strip()
                i = get_object_or_404(ilan, id=id)
                xx = mesaj_formu.save(commit=False)
                xx.gonderen = request.user
                xx.ilgili_ilan = i
                xx.save()
                mesaj_formu = mesajFormu()
                messages.success(request, 'Mesaj gönderildi..')

    ilanlar = ilan.objects.filter(yayinda=True)
    return render(request, 'ilanlarim.html', {'form': ilanlar, 'islem': 'anasayfa', 'sahip': request.user, 'mesaj_formu':mesaj_formu})


    # bilgiler = BilgilerFormu(request.POST or None, instance=request.user)
    # if request.method == 'POST':
    #     value = request.POST.get('bilgiler')
    #     if value:
    #         if bilgiler.is_valid():
    #             user = bilgiler.save()
    #             update_session_auth_hash(request, user)  # Important!
    #             messages.success(request, 'Yapılan değişiklikler kaydedildi.')
    #
    # return render(request, 'Silinecekler/anasayfa.html', {'islem': 1, 'user': request.user, 'bilgiler_formu': bilgiler})


@login_required(login_url='girisislemi')
def favorilerim(request, id=None, islem=None):
    mesaj_formu = mesajFormu(request.POST or None)
    if id:
        i = get_object_or_404(favoriler, id=id)
        if islem == 'favoricikar':
            i.delete()
    elif request.method == 'POST':
        if 'mesaj' in request.POST:
            if mesaj_formu.is_valid():
                id = request.POST.get('mesaj').strip()
                i = get_object_or_404(ilan, id=id)
                xx = mesaj_formu.save(commit=False)
                xx.gonderen = request.user
                xx.ilgili_ilan = i
                xx.save()
                mesaj_formu = mesajFormu()
                messages.success(request, 'Mesaj gönderildi..')
    favori_ilanlarim = request.user.favori_ilanlarım()
    return render(request, 'ilanlarim.html', {'form': favori_ilanlarim, 'islem': 'favorilerim', 'sahip': request.user, 'mesaj_formu': mesaj_formu})



@login_required(login_url='girisislemi')
def ilanlarim(request):
    # request.user.silinecek_resimleri_iptal_et()
    # form = ilan.objects.filter(sahip=request.user)
    # form = request.user.ilanlarim()
    if request.method == 'POST':
        ilan_veri = request.POST.get('ilan').split(';')
        if ilan_veri[0] == 'yeni':
            pass
        else:
            _ilan = ilan.objects.get(id=ilan_veri[1])
            if ilan_veri[0] == 'sil':
                _ilan.sil()
                messages.warning(request, 'ilan silindi')
            elif ilan_veri[0] == 'yayinla':
                if _ilan.yayinda:
                    _ilan.yayindan_cek()
                    messages.warning(request, 'İlan yayından kaldırıldı.')
                else:
                    _ilan.yayinla()
                    messages.success(request, 'İlan yayınlandı.')
                _ilan.save()
    # else:
    #     request.user.geciciResimlerimiTemizle()
    form = request.user.ilanlarim()
    return render(request, 'ilanlarim.html', {'form': form, 'islem': 'ilanlarım'})

@login_required(login_url='girisislemi')
def ilan_incele(request, id, islem=None):
    x = get_object_or_404(ilan, id=id)
    sikayet_formu = sikayetFormu(request.POST or None)
    mesaj_formu = mesajFormu(request.POST or None)
    if islem == 'favori':
        x.favorilere_ekle_cikar(user=request.user)
    if request.method == 'POST':
        if 'sikayet' in request.POST:
            if sikayet_formu.is_valid():
                xx = sikayet_formu.save(commit=False)
                xx.kim = request.user
                xx.hangi_ilan = x
                xx.save()
                sikayet_formu = sikayetFormu()
                messages.warning(request, 'Şikayet kaydınız oluşturuldu.')
        elif 'mesaj' in request.POST:
            if mesaj_formu.is_valid():
                xx = mesaj_formu.save(commit=False)
                xx.gonderen = request.user
                xx.ilgili_ilan = x
                xx.save()
                mesaj_formu = mesajFormu()
                messages.success(request, 'Mesaj gönderildi..')
    r_adet = x.resimleri_getir().count()
    return render(request, 'ilan_inceleme.html', {'form':  x, 'resim_adet': r_adet, 'sahip': request.user, 'sikayet_formu': sikayet_formu, 'mesaj_formu': mesaj_formu, 'nereden':islem})

@login_required(login_url='girisislemi')
def mesajlarim(request):
    x = request.user.mesajNavBar_bilgileri_getir()
    return render(request, 'mesajlar.html', {'islem': 'mesajlar'})


# @login_required(login_url='girisislemi')
# def ilan_detay1(request, id):
#     hangi_ilan = ilan.objects.get(id=id)
#     form = resimliİlanFormu(request.POST or None, request.FILES or None, instance=hangi_ilan)
#     if request.method == 'POST':
#         islem = request.POST.get('btn')
#         if islem == 'resim':
#             hangi_ilan.resimekle(resim=request.FILES['resim'])
#             messages.success(request, 'Resim eklendi')
#         elif islem == 'kaydet':
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, 'Değişiklikler kaydedildi')
#                 return redirect(ilanlarim)
#     return render(request, 'ilanDetay.html', {'form': form, 'resimler': hangi_ilan.resimler()})


# class resimlerSinifi():
#
#     def __init__(self, hangi_ilan=None):
#         self.kayitliResimler = {}
#         self.geciciResimler = []
#         if hangi_ilan:
#             for r in hangi_ilan.resimler():
#                 self.kayitliResimler = self.kayitliResimler + {'resim': r, 'silinecek': False}
#             for r in hangi_ilan.geciciResimleriGetir():
#                 self.geciciResimler = self.geciciResimler + [r]
#         else:
#             hangi_ilan.geciciResimleriDoldur()
#
#
# s = None
@login_required(login_url='girisislemi')
def yeni_ilan(request):
    form = İlanFormu(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            x = ilan()
            x.sahip = request.user
            x.kategori = data['kategori']
            x.ad = data['ad']
            x.adet = data['adet']
            x.aciklama = data['aciklama']
            x.save()
            return redirect(ilan_detay, x.id)
    return render(request, 'yeniilan.html', {'form': form})


@login_required(login_url='girisislemi')
def ilan_detay(request, id):
    hangi_ilan = ilan.objects.get(id=id)
    form = resimliİlanFormu(data=request.POST or None, files=request.FILES or None, instance=hangi_ilan)
    if request.method == 'POST':
        islem = request.POST.get('btn')
        if islem == 'resimekle':
            s = hangi_ilan.resim_ekle(resim=request.FILES['resim'])
            if s:
                messages.error(request, s)
            else:
                messages.success(request, 'Resim eklendi.')
        elif islem == 'kaydet':
            if form.is_valid():
                # hangi_ilan.silme_tarihi = None
                form.save()
                messages.success(request, 'Değişiklikler kaydedildi')
                return redirect(ilanlarim)
        else:
            islem, resim_id = islem.split(';')
            if islem == 'resimsil':
                Resim.objects.filter(id=resim_id).delete()
    _resimler = hangi_ilan.resimleri_getir()
    resimAdet = _resimler.count()
    return render(request, 'ilanDetay.html', {'form': form, 'resimler': _resimler, 'resimAdet': resimAdet})

def il_ilce_veritanamını_aktar(request):
    pass
    # file_il = open(file='iller.txt', mode='r', encoding='latin5')
    # for s in file_il:
    #     id, adi = s.split(';')
    #     x = il(adi=adi.strip())
    #     x.save()
    # file_il.close()
    # file_ilce = open(file='ilceler.txt', mode='r', encoding='latin5')
    # for s in file_ilce:
    #     id, il_id, ilce_adi = s.split(';')
    #     # i = il.objects.filter(id=id).first()
    #     ilce_adi = ilce_adi.strip()
    #     x = ilce(adi=ilce_adi, ill_id=il_id)
    #     x.save()
    # file_ilce.close()
    # file_mahalle = open(file='Mahalle.txt', mode='r', encoding='latin5')
    # satir = file_mahalle.readline()
    # while satir:
    #     id, ilce_id, mahalle_adi = satir.split(';')
    #     # i = il.objects.filter(id=id).first()
    #     mahalle_adi = mahalle_adi.strip()
    #     x = mahalle(adi=mahalle_adi, ilcee_id=ilce_id)
    #     x.save()
    #     x=None
    #     satir = file_mahalle.readline()
    # file_mahalle.close()
    # messages.success(request, "Veritabanı dolduruldu")
    # return redirect('anasayfaislemi')
