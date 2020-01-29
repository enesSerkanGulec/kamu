from django import template
from app.models import favoriler

register = template.Library()
@register.filter
def favorilerde_mevcut_mu(ilan, user):
    try:
        x = favoriler.objects.get(ilan=ilan, sahip=user)
        return True
    except:
        return False
