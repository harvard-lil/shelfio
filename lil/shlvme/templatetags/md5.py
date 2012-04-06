from django import template
import hashlib
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter
@stringfilter
def md5(value):
    return hashlib.md5(value).hexdigest()