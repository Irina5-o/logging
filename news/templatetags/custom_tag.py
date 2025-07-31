from django.utils import timezone
from django import template

register = template.Library()

@register.simple_tag()
def current_time(format_string='%b %d %Y'):
   return timezone.now().strftime(format_string)