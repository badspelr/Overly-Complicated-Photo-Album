from django import template
import time

register = template.Library()

@register.simple_tag
def timestamp():
    return int(time.time())
