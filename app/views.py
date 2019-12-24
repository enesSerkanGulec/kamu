from django.shortcuts import render, HttpResponse, redirect
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
                return anasayfa(request)
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
    form = None
    if islem == 'bilgiler':
        form = BilgilerFormu(request.POST or None, instance=request.user)
    elif islem == 'parola':
        form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
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
def anasayfa(request):
    # resimlerFormSet = modelformset_factory(GeciciResim, exclude=())
    # formSet = resimlerFormSet(queryset=GeciciResim.objects.all())
    # return render(request, 'anasayfa.html', {'user': request.user.kurum, 'resimler': formSet})

    return render(request, 'anasayfa.html', {'user': request.user.kurum, 'resimler': Resim.objects.all()})


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
def ilanlarim(request):
    # form = ilan.objects.filter(sahip=request.user)
    form = request.user.ilanlarım()
    request.user.geciciResimlerimiTemizle()
    if request.method == 'POST':
        ilan_veri = request.POST.get('ilan').split(';')
        _ilan = ilan.objects.get(id=ilan_veri[1])
        if ilan_veri[0] == 'sil':
            _ilan.delete()
            messages.success(request, 'ilan silindi')
        elif ilan_veri[0] == 'yayinla':
            _ilan.yayinda = not _ilan.yayinda
            _ilan.save()
            if _ilan.yayinda:
                messages.success(request, 'İlan yayınlandı.')
            else:
                messages.warning(request, 'İlan yayından kaldırıldı.')
        form = ilan.objects.filter(sahip=request.user)
    return render(request, 'ilanlarim.html', {'form': form})


@login_required(login_url='girisislemi')
def ilan_detay1(request, id):
    hangi_ilan = ilan.objects.get(id=id)
    form = resimliİlanFormu(request.POST or None, request.FILES or None, instance=hangi_ilan)
    if request.method == 'POST':
        islem = request.POST.get('btn')
        if islem == 'resim':
            hangi_ilan.resimekle(resim=request.FILES['resim'])
            messages.success(request, 'Resim eklendi')
        elif islem == 'kaydet':
            if form.is_valid():
                form.save()
                messages.success(request, 'Değişiklikler kaydedildi')
                return redirect(ilanlarim)
    return render(request, 'ilanDetay.html', {'form': form, 'resimler': hangi_ilan.resimler()})


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
def ilan_detay(request, id):
    hangi_ilan = ilan.objects.get(id=id)
    resimAdet=0
    if request.method == 'GET':
        hangi_ilan.geciciResimleriDoldur()
        _resimler = hangi_ilan.geciciResimleriGetir()
        resimAdet = _resimler.count()
    #     _resimler = hangi_ilan.geciciResimleriGetir()
    # else:




    form = resimliİlanFormu(request.POST or None, request.FILES or None, instance=hangi_ilan)

    if request.method == 'POST':
        islem = request.POST.get('btn')
        if islem == 'resim':
            s = hangi_ilan.geciciResimEkle(resim=request.FILES['resim'])
            _resimler = hangi_ilan.geciciResimleriGetir()
            resimAdet = _resimler.count()
            if s:
                messages.error(request, s)
        elif islem == 'kaydet':
            if form.is_valid():
                form.save()
                hangi_ilan.geciciResimleriKaydet()
                messages.success(request, 'Değişiklikler kaydedildi')
                return redirect(ilanlarim)
    return render(request, 'ilanDetay.html', {'form': form, 'resimler': _resimler, 'resimAdet': resimAdet})
