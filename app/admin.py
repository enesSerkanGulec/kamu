from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from smart_selects.db_fields import ChainedForeignKey

from .models import *


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (_('email'), {'fields': ('email',)}),
        #, 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Kurum Bilgileri'), {'fields': ('kurum', 'kurum_telefon', 'kurum_web_adres')}),
        (_('Kurm Adres Bilgileri'), {'fields': ('kurum_il', 'kurum_ilce', 'kurum_mahalle')}),
        #(_('Malzemeler'), {('_malzemeler')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
                                       #,'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


class ilanAdmin(admin.ModelAdmin):
    #fieldsets = (
    #    (None, {'fields': ('ad',)}),
    #    (_('Adet'))
    #)
    list_display = ('ad', 'adet', 'sahip', 'kategori', 'resim_sayisi', 'olusturma_tarihi')

    class Meta:
        model = ilan

    def resim_sayisi(self, obj):
        x = Resim.objects.filter(ilan=obj).count()
        return str(x)


class KategoriAdmin(admin.ModelAdmin):
    list_display = ('isimgetir', 'adetgetir')

    class Meta:
        model = Kategori

    def adetgetir(self, obj):
        x = ilan.objects.filter(kategori=obj).aggregate(Sum('adet'))
        if x['adet__sum'] is None:
            return 0
        else:
            return x['adet__sum']

    def isimgetir(self, obj):
        return str(obj)


class ResimAdmin(admin.ModelAdmin):
    list_display = ('resim', 'kategoriadi')

    class Meta:
        model = Resim

    def kategoriadi(self, obj):
        return str(obj.ilan)


class MesajAdmin(admin.ModelAdmin):
    list_display = ('ilgili_ilan', 'mesaj_metni', 'okundu', 'silindi')

    class Meta:
        model = Mesaj

class SikayetNedenleriAdmin(admin.ModelAdmin):
    list_display = ['neden']

    class Meta:
        model = sikayet_nedenleri

class SikayetlerAdmin(admin.ModelAdmin):
    list_display = ['kim', 'hangi_ilan', 'sikayet_nedeni', 'tarih']
    list_display_links = ['sikayet_nedeni']

    class Meta:
        model = sikayet


admin.site.register(ilan, ilanAdmin)
admin.site.register(Kategori, KategoriAdmin)
admin.site.register(Resim, ResimAdmin)
admin.site.register(KayitBekleyenler)
admin.site.register(Mesaj, MesajAdmin)
admin.site.register(sikayet_nedenleri, SikayetNedenleriAdmin)
admin.site.register(sikayet, SikayetlerAdmin)
