"""
No models as of yet but auto-registers the media_compressor_tags so you don't
need to use {% load media_compressor_tags %} in your templates to use them.
"""
from django import template

template.add_to_builtins('media_compressor.templatetags.media_compressor_tags')
