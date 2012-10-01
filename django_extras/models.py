"""
No models as of yet but auto-registers the django_extras_tags so you don't
need to use {% load django_extras_tags %} in your templates to use them.
"""
from django import template

template.add_to_builtins('django_extras.templatetags.django_extras_tags')
