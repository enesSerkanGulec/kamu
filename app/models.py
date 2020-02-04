from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from PIL import Image, ImageDraw, ImageFont
import os
import datetime
from datetime import timedelta
from django.db.models import F
from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage as storage
from kamu.settings import THUMB_SIZE
from io import BytesIO
from smart_selects.db_fields import ChainedForeignKey
from django.db.models import Q


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)
    kurum = models.CharField(max_length=100, verbose_name='Kurum', null=True)
    kurum_adres = models.CharField(max_length=200, verbose_name='Kurum adresi', null=True)
    phone_regex = RegexValidator(regex=r'^\+?[1-9][0-9]{2} ?[0-9]{3} ?[0-9]{2} ?[0-9]{2}$',
                                 message="Telefon numarası şu şeklillerden biri gibi olmalı: '+9999999999' veya "
                                         "'9999999999' veya '999 9999999' veya '999 999 9999' veya '999 999 99 99'.")
    kurum_telefon = models.CharField(validators=[phone_regex], max_length=17, null=True, verbose_name='Kurum telefonu')  # validators should be a list
    kurum_web_adres = models.URLField(verbose_name='Kurum web adresi', null=True)
    kurum_il = models.ForeignKey('il', on_delete=models.SET_NULL, null=True, blank=False)
    kurum_ilce = ChainedForeignKey('ilce', chained_field="kurum_il", chained_model_field="ill", show_all=False, auto_choose=True,
                                   sort=False, null=True, blank=False)
    kurum_mahalle = ChainedForeignKey('mahalle', chained_field="kurum_ilce", chained_model_field='ilcee', show_all=False,
                                    auto_choose=True, sort=False, null=True, blank=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def mesajNavBar_bilgileri_getir(self):
        pass
    #     sonuc = list()
    #     i = list(self.ilanlarim())
    #     benimMesajlarim = Mesajlar.objects.filter(gonderen=self) | Mesajlar.objects.filter(ilgili_ilan__in=i)
    #     sonuc.append(benimMesajlarim)
    #     toplamSayi = benimMesajlarim.count()
    #     gidenSayisi = benimMesajlarim.filter(gonderen=self).count()
    #     sonuc.append(gidenSayisi)
    #     gelenSayisi = toplamSayi - gidenSayisi
    #     sonuc.append(gelenSayisi)
    #     okunmamisSayisi = benimMesajlarim.filter(okundu=False).count()
    #     sonuc.append(okunmamisSayisi)
    #     okunmusSayisi = toplamSayi - okunmamisSayisi
    #     sonuc.append(okunmusSayisi)
    #     ilgili_ilanlar = list(benimMesajlarim.values('ilgili_ilan').distinct())
    #     kurumlar = list(benimMesajlarim.values('gonderen').distinct())
    #     xx = []
    #     for x in ilgili_ilanlar:
    #         xx.append([x['ilgili_ilan'], benimMesajlarim.filter(ilgili_ilanlar=x['ilgili_ilan']).count()])
    #     # ilgili_ilanlar = zip(ilgili_ilanlar, xx)
    #     sonuc.append(ilgili_ilanlar)
    #     xx = []
    #     for x in kurumlar:
    #         xx.append(benimMesajlarim.filter(gonderen=x).count())
    #     kurumlar = zip(kurumlar, xx)
    #     sonuc.append(kurumlar)
    #     return sonuc

    def ilanlarim(self):
        return ilan.objects.filter(sahip=self)

    def favori_ilanlarim(self):
        return favoriler.objects.filter(sahip=self)

    def mesajlar(self):
        m = []
        for x in self.ilanlarim():
            m = m + x.mesajlar()
        return m

    def __str__(self):
        return str(self.kurum)

    def delete(self, *args, **kwargs):
        for x in self.ilanlarim():
            x.delete()
        super(User, self).delete(*args, **kwargs)


class Kategori(models.Model):
    ust_kategori = models.ForeignKey('Kategori', null=True, blank=True, on_delete=models.CASCADE)
    ad = models.CharField(max_length=20, verbose_name='Kategori adı')

    class Meta:
        ordering = ('ust_kategori__ad',  'ad', )

    def __str__(self):
        if self.ust_kategori:
            return str(self.ust_kategori) + '/' + self.ad
        else:
            return self.ad


class ilan(models.Model):
    sahip = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    kategori = models.ForeignKey('Kategori', null=True, on_delete=models.SET_NULL)
    ad = models.CharField(max_length=40, verbose_name='ilan adı', null=True)
    adet = models.IntegerField(verbose_name='Adet', default=1, null=True)
    aciklama = models.TextField(verbose_name='Açıklama', blank=True)
    yayinda = models.BooleanField(verbose_name='Yayında', default=True)
    olusturma_tarihi = models.DateField(auto_now=True, null=False, blank=False)
    silme_tarihi = models.DateField(null=True, blank=True)
    kurum = models.CharField(max_length=200, null=True, blank=True)
    kucuk_resim = models.ImageField(upload_to='silinenilanlar', editable=False, blank=True, null=True)

    def etiket_yazisi_getir(self):
        if self.silme_tarihi is None:
            return '<span style="font-weight: bold">' + self.ad + '</span>' + '<br><span style="font-size:smaller">'+self.sahip.kurum + '</span><br>' + '<span style="font-size: xx-small; font-weight: lighter">' + self.sahip.kurum_il.adi + ',' + self.sahip.kurum_ilce.adi + '</span>'
        else:
            return self.kurum

    def ilan_sahip_bilgisi_getir(self):
        if self.silme_tarihi is None:
            return 'İlan Numarası: {}<br>Kurum: {}<br>Kurum İl/İlçe: {}/{}<br>Kurum Telefon: {}'.format(self.id,
             self.sahip.kurum, self.sahip.kurum_il, self.sahip.kurum_ilce, self.sahip.kurum_telefon)

        else:
            return self.kurum

    def ilan_bilgisi_getir(self):
        return 'Kategori: {}<br>İlan Adı: {}<br>Adet: {}<br>Açıklama: {}'.format(self.kategori, self.ad, self.adet, self.aciklama)

    def favorilerde(self, user):
        try:
            x = favoriler.objects.get(sahip=user, ilan=self)
            if x is None:
                return False
            return True
        except:
            return False

    def favorilere_ekle_cikar(self, user):
        if self.favorilerde(user):
            favoriler.objects.filter(sahip=user, ilan=self).delete()
        else:
            x = favoriler(sahip=user, ilan=self)
            x.save()

    def sil(self):
        self.kurum = self.etiket_yazisi_getir()
        self.sahip = None
        self.yayinda = False
        self.silme_tarihi = datetime.datetime.now()
        self.kucukResimOlustur(yazi='İlan Silinmiş')
        try:
            Resim.objects.filter(ilan=self).delete()
        finally:
            super(ilan, self).save()

    # def delete(self, *args, **kwargs):
    #     self.sil()

    def yayindami(self):
        return not self.silme_tarihi and self.yayinda

    def yayindan_cek(self):
        self.yayinda = False
        self.kucukResimOlustur()

    def yayinla(self):
        self.yayinda = True
        self.kucuk_resim.delete(save=True)

    def kucukResimOlustur(self, yazi='Yayında Değil'):
        if self.kucuk_resim:
            self.kucuk_resim.delete(save=True)

        r = Resim.objects.filter(ilan=self).first()
        if r is None:
            d_ismi = 'ilan_{}.jpeg'.format(self.id)
            image = Image.new('L', THUMB_SIZE, 'white')
        else:
            d_ismi = r.kucukResim.name
            image = Image.open(r.kucukResim).convert('L')

        width, height = image.size
        draw = ImageDraw.Draw(image)
        # .convert('L') ile gri tonlama yapıyoruz.
        text = yazi
        font = ImageFont.truetype('arial.ttf', 30)
        textwidth, textheight = draw.textsize(text, font)

        # calculate the x,y coordinates of the text
        margin = 5
        # Tam ortaya Alıyor
        x = (width - textwidth - margin * 2) / 2
        y = (height - textheight - margin * 2) / 2
        # Yazıdan önce siyah bir dikdörtgen çiziyor
        draw.rectangle([x - 3, y - 3, x + textwidth + 6, y + textheight + 6], fill='red')
        # yazıyı yazıyor
        draw.text((x, y), text, font=font)

        image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)

        thumb_name, thumb_extension = os.path.splitext(d_ismi)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + '_laMevcut' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False  # Unrecognized file type

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        self.kucuk_resim.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()
        return True

    def __str__(self):
        return str(self.kategori) + ' - ' + str(self.ad)

    def resimleri_getir(self):
        if self.sahip:
            return Resim.objects.filter(ilan=self)
        else:
            return None

    def resim_adet(self):
        return Resim.objects.filter(ilan=self).count()

    def mesajAdet(self):
        return Mesaj.objects.filter(ilgili_ilan=self).count()

    def okunmayanMesajAdet(self):
        return Mesaj.objects.filter(ilgili_ilan=self, okundu=False).count()

    def resim_ekle(self, resim):
        try:
            x = Resim.objects.get(ilan=self, resim=resim)
        except:
            yeniresim = Resim()
            yeniresim.ilan = self
            yeniresim.resim = resim
            # yeniresim.silinecek = False
            yeniresim.save()
            return ""
        else:
            # if x.silinecek:
            #     x.silinecek = False
            #     return ""
            # else:
            return "Bu resim zaten mevcut"

    def mesajlar(self):
        return Mesaj.objects.filter(ilgili_ilan=self)

    # def save(self, *args, **kwargs):
    #     Resim.objects.filter(ilan=self, silinecek=True).delete()
    #     super(ilan, self).save(*args, **kwargs)


class Resim(models.Model):
    ilan = models.ForeignKey('ilan', on_delete=models.CASCADE, null=True)
    resim = models.ImageField(verbose_name='Resim', null=True)
    # silinecek = models.BooleanField(default=False)
    kucukResim = models.ImageField(upload_to='thumbs', editable=False, blank=True, null=True)

    class Meta:
        ordering = ['ilan']

    def save(self, *args, **kwargs):
        if not self.make_thumbnail():
            # set to a default thumbnail
            raise Exception('Could not create thumbnail - is the file type valid?')
        super(Resim, self).save(*args, **kwargs)

    def make_thumbnail(self):

        image = Image.open(self.resim)
        image.thumbnail(THUMB_SIZE, Image.ANTIALIAS)

        thumb_name, thumb_extension = os.path.splitext(self.resim.name)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + '_thumb' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False  # Unrecognized file type

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        image.save(temp_thumb, FTYPE)
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        self.kucukResim.save(thumb_filename, ContentFile(temp_thumb.read()), save=False)
        temp_thumb.close()

        return True

    def __str__(self):
        return self.resim.name

    def sil(self):
        if self.ilan.resim_adet() > 1:
            self.delete()
            return ""
        else:
            return "İlanda en az bir resim olmalıdır."


class KayitBekleyenler(models.Model):
    # _('email address')
    email = models.EmailField('Kurum e-posta adresi', unique=True,)
    kurum = models.CharField(max_length=100, verbose_name='Kurum adı', null=True)
    kurum_adres = models.CharField(max_length=200, verbose_name='Kurum adresi', null=True)
    phone_regex = RegexValidator(regex=r'^\+?[1-9][0-9]{2} ?[0-9]{3} ?[0-9]{2} ?[0-9]{2}$',
                                 message="Telefon numarası şu şeklillerden biri gibi olmalı: '+9999999999' veya "
                                         "'9999999999' veya '999 9999999' veya '999 999 9999' veya '999 999 99 99'. ")
    kurum_telefon = models.CharField(validators=[phone_regex], max_length=17, null=True, verbose_name='Kurum telefonu')  # validators should be a list
    kurum_web_adres = models.URLField(verbose_name='Kurum web adresi', null=True, blank=True)
    kurum_il = models.ForeignKey('il', on_delete=models.PROTECT, null=True, blank=False)
    kurum_ilce = ChainedForeignKey('ilce', chained_field="kurum_il", chained_model_field="ill", null=True,
                                   blank=False)
    kurum_mahalle = ChainedForeignKey('mahalle', chained_field="kurum_ilce", chained_model_field='ilcee',
                                      show_all=False, null=True, blank=False)

    def __str__(self):
        return self.email


class Mesaj(models.Model):
    gonderen_id = models.IntegerField(null=True, blank=False)
    gonderilen_id = models.IntegerField(null=True, blank=False)
    mesaj_metni = models.TextField(null=True, blank=False)
    ilgili_ilan = models.ForeignKey('ilan', null=True, blank=True, on_delete=models.SET_NULL)
    okundu = models.BooleanField(default=False)
    silindi = models.IntegerField(null=True, blank=True, default=0)
    tarih = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ilgili_ilan.ad

    def sil(self, user_id):
        if self.gonderen_id == user_id: #Giden mesaj
            if self.silindi in [0, 2]:
                self.silindi = self.silindi + 1

        if self.gonderilen_id == user_id: #Gelen Mesaj
            if self.silindi in [0, 1]:
                self.silindi = self.silindi + 2

        self.save()

        if self.silindi == 3:
            self.delete()


    def gonderenKim(self, ben_id):
        if self.gonderen_id == ben_id:
            return 'Ben'
        else:
            try:
                x = User.objects.get(id=self.gonderen_id)
                return x.kurum
            except:
                return 'Gönderen Silinmiş'

    def gonderilenKim(self, ben_id):
        if self.gonderilen_id == ben_id:
            return 'Ben'
        else:
            try:
                x = User.objects.get(id=self.gonderilen_id)
                return x.kurum
            except:
                return 'Gönderilen Silinmiş'

    def mesaj_getir(sahip, filtre):
        ilgi = yon = durum = zaman = ""
        x = filtre.split('-')
        ilgi = x[0].split(':')[1]
        yon = x[1].split(':')[1]
        durum = x[2].split(':')[1]
        zaman = x[3].split(':')[1]

        s = Mesaj.objects.filter((Q(gonderilen_id=sahip.id) & Q(silindi__in=[0, 1])) | (Q(gonderen_id=sahip.id) & Q(silindi__in=[0, 2])))

        if ilgi == 'kurum':
            s = s.filter(ilgili_ilan__isnull=True)
        elif ilgi == 'ilan':
            s = s.filter(ilgili_ilan__isnull=False)

        if yon == 'giden':
            s = s.filter(gonderen_id=sahip.id)
        elif yon == 'gelen':
            s = s.filter(gonderilen_id=sahip.id)

        if durum == 'okunmadi':
            s = s.filter(okundu=False)
        elif durum == 'okundu':
            s = s.filter(okundu=True)

        bugun_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        if zaman == 'bugun':
            bugun_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
            s = s.filter(tarih__range=(bugun_min, bugun_max))
        elif zaman == 'buhafta':
            buhafta_max = bugun_min + timedelta(weeks=1)
            s = s.filter(tarih__range=(bugun_min, buhafta_max))
        elif zaman == 'buay':
            buay_max = bugun_min + timedelta(days=30)
            s = s.filter(tarih__range=(bugun_min, buay_max))

        return s

class favoriler(models.Model):
    sahip = models.ForeignKey(User, null=False, blank=False, on_delete=models.CASCADE)
    ilan = models.ForeignKey(ilan, null=False, blank=False, on_delete=models.CASCADE)


class il(models.Model):
    adi = models.CharField(max_length=20)

    def __str__(self):
        return self.adi


class ilce(models.Model):
    ill = models.ForeignKey(il, on_delete=models.CASCADE)
    adi = models.CharField(max_length=35)

    def __str__(self):
        return self.adi


class mahalle(models.Model):
    ilcee = models.ForeignKey(ilce, on_delete=models.CASCADE)
    adi = models.CharField(max_length=50)

    def __str__(self):
        return self.adi


class sikayet_nedenleri(models.Model):
    neden = models.CharField(max_length=40)

    def __str__(self):
        return self.neden


class sikayet(models.Model):
    kim = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    hangi_ilan = models.ForeignKey('ilan', on_delete=models.PROTECT)
    sikayet_nedeni = models.ForeignKey('sikayet_nedenleri', verbose_name='Şikayet Nedeni', on_delete=models.PROTECT, null=False, blank=False)
    aciklama = models.TextField(blank=True, verbose_name='Açıklama')
    tarih = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}(İlan:{}, Kim:{})'.format(self.sikayet_nedeni, self.hangi_ilan, self.kim)
