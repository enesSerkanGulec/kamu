from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from PIL import Image


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
        for x in self.ilanlarım():
            x.geciciResimleriTemizle()

    def ilanlarım(self):
        return ilan.objects.filter(sahip=self)

    def mesajlar(self):
        m = []
        for x in self.ilanlarım():
            m = m + x.mesajlar()
        return m

    def __str__(self):
        return str(self.kurum)


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
    sahip = models.ForeignKey('User', null=True, on_delete=models.CASCADE)
    kategori = models.ForeignKey('Kategori', null=True, on_delete=models.SET_NULL)
    ad = models.CharField(max_length=40, verbose_name='ilan adı', null=True)
    adet = models.IntegerField(verbose_name='Adet', default=1, null=True)
    aciklama = models.TextField(verbose_name='Açıklama', blank=True)
    yayinda = models.BooleanField(verbose_name='Yayında', default=True)
    tarih = models.DateField(auto_now=True, null=False, blank=False)

    def __str__(self):
        return str(self.kategori) + ' - ' + str(self.ad)

    def resimler(self):
        return Resim.objects.filter(ilan=self)

    def geciciResimleriTemizle(self):
        GeciciResim.objects.filter(ilan=self).delete()

    def geciciResimleriDoldur(self):
        for x in self.resimler():
            self.geciciResimEkle(resim=x.resim, kayitliMi=True)
            # _geciciResim = GeciciResim(ilan=self, resim=x.resim)
            # _geciciResim.save()

    def geciciResimleriGetir(self):
        # self.geciciResimleriDoldur()
        return GeciciResim.objects.filter(ilan=self, silinecek=False)

    def geciciResimleriKaydet(self):
        _gr = GeciciResim.objects.filter(ilan=self)
        for x in _gr:
            if not x.kayitli and not x.silinecek:
                self.resimekle(resim=x.resim)
            if x.kayitli and x.silinecek:
                Resim.objects.get(ilan=self, resim=x.resim).delete()
            #x.delete()

    def geciciResimEkle(self, resim, kayitliMi=False):
        try:
            x = GeciciResim.objects.get(ilan=self, resim=resim)
        except:
            _ = GeciciResim(ilan=self, resim=resim, kayitli=kayitliMi)
            _.save()
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
        yeniresim.save()

    def mesajlar(self):
        return Mesajlar.objects.filter(ilan=self)

    def mesajAdet(self):
        return Mesajlar.objects.filter(ilan=self).count()

    def okunmayanMesajAdet(self):
        return Mesajlar.objects.filter(ilan=self, okundu=False).count()


class Resim(models.Model):
    ilan = models.ForeignKey('ilan', on_delete=models.CASCADE, null=True)
    resim = models.ImageField(verbose_name='Resim', null=True)

    class Meta:
        ordering = ['ilan']

    def __str__(self):
        return self.resim.name


class GeciciResim(models.Model):
    ilan = models.ForeignKey('ilan', on_delete=models.CASCADE, null=True)
    resim = models.ImageField(verbose_name='Resim', null=True)
    kayitli = models.BooleanField(default=True)
    silinecek = models.BooleanField(default=False)

    def sil(self):
        self.silinecek = True


class KayitBekleyenler(models.Model):
    email = models.EmailField(_('email address'), unique=True,)
    kurum = models.CharField(max_length=100, verbose_name='Kurum', null=True)
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



