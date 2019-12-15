from django import forms
from app.models import *
from app.models import User as userrr


class KayitFormu(forms.ModelForm):

    def clean_email(self):
        email = self.cleaned_data.get("email")
        try:
            userrr.objects.get(email=email)
            raise forms.ValidationError('Bu e-postayı kullanan birisi var.', )
        except userrr.DoesNotExist:
            try:
                KayitBekleyenler._default_manager.get(email=email)
                # if the user exists, then let's raise an error message
                raise forms.ValidationError('Bu e-posta ile kayıt isteği yapılmış', )
            except KayitBekleyenler.DoesNotExist:
                return email  # if user does not exist so we can continue the registration process

    class Meta:
        model = KayitBekleyenler
        fields = ['email', 'kurum', 'kurum_adres', 'kurum_telefon', 'kurum_web_adres']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['kurum_web_adres'].widget.attrs.update({'initial': "http://"})


class GirisFormu(forms.Form):
    email = forms.EmailField(label='E-posta')
    sifre = forms.CharField(label='Parola', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = userrr._default_manager.get(email=email)
            return email
        except userrr.DoesNotExist:
            raise forms.ValidationError('Bu e-posta kayıtlı değil')

    class Meta:
        fields = ['email', 'sifre']


class SifreUnuttumFormu(forms.Form):
    email = forms.EmailField(label='E-posta')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            user = userrr._default_manager.get(email=email)
            return email
        except userrr.DoesNotExist:
            raise forms.ValidationError('Bu e-posta kayıtlı değil')

    class Meta:
        fields = ['email']


class BilgilerFormu(forms.ModelForm):

    class Meta:
        model = userrr
        fields = ['email', 'first_name', 'last_name', 'kurum', 'kurum_telefon', 'kurum_adres', 'kurum_web_adres']


class İlanFormu(forms.ModelForm):

    class Meta:
        model = ilan
        widgets = {
            'aciklama': forms.Textarea(attrs={'rows': 4}),
        }
        fields = ['kategori', 'ad', 'adet', 'aciklama']

    def clean_kategori(self):
        if not self.cleaned_data['kategori']:
            raise forms.ValidationError("Kategori boş olamaz !!!")
        else:
            return self.cleaned_data['kategori']

    def clean_ad(self):
        if not self.cleaned_data['ad']:
            raise forms.ValidationError("İlan adı boş olamaz !!!")
        else:
            return self.cleaned_data['ad']

    def clean_adet(self):
        if self.cleaned_data['adet'] <= 0:
            raise forms.ValidationError("Adet sıfırdan  büyük olmalı !!!")
        else:
            return self.cleaned_data['adet']


class resimliİlanFormu(İlanFormu):
    resim = forms.ImageField(required=False)

    class Meta(İlanFormu.Meta):
        fields = İlanFormu.Meta.fields + ['resim', ]

    def __init__(self):
        self.resimler = []
        # burada resimID ve resim bilgisini içeren bir class oluşturulup bu class türünde bir liste oluşturulacak ve
        # ilanın resimleri buna yüklenecek
        # eğer resim veritabanında ise id si gelecek yok yeni eklendi ise id -1 olup kaydetme esnasında
        # bu id si -1 olanlar veritabanına eklenecek

# class ResimFormu(forms.Form):
#     resim = forms.FileField()
#     class Meta:
#         fields = ['resim']

    # class Meta:
    #     model = Resim
    #     fields = ('resim', 'ilan')
    #     exclude = ('ilan',)

    # def __init__(self, *args, **kwargs):
    #     self.ilan = kwargs.pop('hangi_ilan')
    #     super(ResimFormu, self).__init__(*args, **kwargs)

    # def clean_resim(self):
    #     r = self.cleaned_data['resim']
    #     if r:
    #         return r
    #     else:
    #         raise forms.ValidationError('Resim alanı boş')


    # def save(self, commit=True, *args, **kwargs):
    #     m = super(ResimFormu, self).save(commit=False, *args, **kwargs)
    #     m.ilan = hangi_ilan
    #     if commit:
    #         m.save()
    #     return m

