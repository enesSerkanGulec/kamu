from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from PIL import Image, ImageDraw, ImageFont
import os
import datetime
from django.core.files.base import ContentFile
# from django.core.files.storage import default_storage as storage
from kamu.settings import THUMB_SIZE
from io import BytesIO


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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def geciciResimlerimiTemizle(self):
        for x in self.ilanlarim():
            x.geciciResimleriTemizle()

    def ilan_temizligi(self):
        ilan.objects.filter(sahip=self, silme_tarihi__isnull=False, yayinda=True).delete()

    def ilanlarim(self):
        return ilan.objects.filter(sahip=self)

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
    kurum = models.CharField(max_length=100,null=True,blank=True)
    kucuk_resim = models.ImageField(upload_to='silinenilanlar', editable=False, blank=True, null=True)

    def sil(self):
        self.kurum = self.sahip.kurum
        self.sahip = None
        self.yayinda = False
        self.silme_tarihi = datetime.datetime.now()
        self.kucukResimOlustur(yazi='İlan Silinmiş')
        Resim.objects.filter(ilan=self).delete()

    def yayindami(self):
        return not self.silme_tarihi and self.yayinda

    def delete(self, *args, **kwargs):
        if self.silme_tarihi and self.yayinda:
            super(ilan, self).delete(*args, **kwargs)
        else:
            self.sil()

    def yayindan_cek(self):
        self.yayinda = False
        self.kucukResimOlustur()

    def yayinla(self):
        self.yayinda=True
        self.kucuk_resim.delete(save=True)

    def kucukResimOlustur(self, yazi='Yayında Değil'):
        if self.kucuk_resim:
            self.kucuk_resim.delete(save=True)

        r = Resim.objects.filter(ilan=self).first()
        image = Image.open(r.kucukResim)

        width, height = image.size
        draw = ImageDraw.Draw(image).convert('L')
        # .convert('L') ile gri tonlama yapıyoruz.
        text = yazi
        font = ImageFont.truetype('arial.ttf', 33)
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

        thumb_name, thumb_extension = os.path.splitext(r.kucukResim.name)
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

    def tum_resimleri_getir(self):
        return Resim.objects.filter(ilan=self)

    def silinmeyecek_resimler(self):
        return Resim.objects.filter(ilan=self, silinecek=False)

    def resim_adet(self):
        return Resim.objects.filter(ilan=self, silinecek=False).count()

    def mesajAdet(self):
        return Mesajlar.objects.filter(ilan=self).count()

    def okunmayanMesajAdet(self):
        return Mesajlar.objects.filter(ilan=self, okundu=False).count()

    # def kacFavorideKayitli(self):
    #     return favoriler.objects.filter(ilan=self).count()
    #

    def geciciResimleriTemizle(self):
        Resim.objects.filter(ilan=self, kayitli=False).delete()
        Resim.objects.filter(ilan=self, silinecek=True).update(silinecek=False)

    def geciciResimEkle(self, resim):
        try:
            x = Resim.objects.get(ilan=self, resim=resim)
        except:
            self.resimekle(resim)
            return ""
        else:
            if x.silinecek:
                x.silinecek = False
                return ""
            else:
                return "Bu resim zaten mevcut"

    def resimekle(self, resim):
        yeniresim = Resim()
        yeniresim.ilan = self
        yeniresim.resim = resim
        yeniresim.kayitli = False
        yeniresim.silinecek = False
        yeniresim.save()

    def mesajlar(self):
        return Mesajlar.objects.filter(ilan=self)

    def save(self, *args, **kwargs):
        if not(self.silme_tarihi and self.yayinda):
            Resim.objects.filter(ilan=self, silinecek=True).delete()
            Resim.objects.filter(ilan=self, kayitli=False).update(kayitli=True)
        super(ilan, self).save(*args, **kwargs)


class Resim(models.Model):
    ilan = models.ForeignKey('ilan', on_delete=models.CASCADE, null=True)
    resim = models.ImageField(verbose_name='Resim', null=True)
    kayitli = models.BooleanField(default=False)
    silinecek = models.BooleanField(default=False)
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

    def kaydet(self):
        self.kayitli = True
        self.silinecek = False

    def sil(self):
        if self.ilan.resim_adet()>1:
            self.silinecek = True
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

    def __str__(self):
        return self.email


yon_secimi = [('gelen', 'gelen'), ('giden', 'giden')]


class Mesajlar(models.Model):
    ilan = models.ForeignKey('ilan', null=False, blank=False, on_delete=models.CASCADE)
    yon = models.CharField(max_length=5, null=False, blank=False, choices=yon_secimi, default='gelen')
    mesaj_metni = models.TextField(blank=False, default='')
    tarih = models.DateTimeField(auto_now_add=True)
    okundu = models.BooleanField(default=False)

    def kurum(self):
        return self.sahip.kurum

    def __str__(self):
        return '{} ({})'.format(self.ilan.ad, self.yon)


class favoriler(models.Model):
    sahip = models.ForeignKey('User', null=False, blank=False, on_delete=models.CASCADE)
    ilan = models.ForeignKey('ilan', null=False, blank=False, on_delete=models.CASCADE)



