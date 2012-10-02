"""
Template tags package for media_compressor, adds tags for converting to JSON and
compressing JS/CSS.
"""
import locale

from django.conf import settings
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.utils.http import urlquote
from django import template
from media_compressor.media import compress_media, expand_source_filenames

locale.setlocale(locale.LC_ALL, '')
register = template.Library() #pylint: disable-msg=C0103

def as_json(value, arg=None):
    """Converts the arg_value to JSON."""
    indent = None
    if arg is not None:
        for arg_name, arg_value in [pair.split('=') for pair in arg.split(',')]:
            if 'indent' == arg_name:
                indent = int(arg_value)
    return mark_safe(simplejson.dumps(value, indent=indent))
register.filter('as_json', as_json)

def currency(value):
    """Localizes currency."""
    return locale.currency(value, grouping=True)
register.filter('currency', currency)

def render_compressed(filename, template_name, context):
    """Render the template for the compressed media, altering the
    URL as appropriate."""
    context = dict(context)
    if filename.startswith('http://') or filename.startswith('https://'):
        context['url'] = filename
    else:
        context['url'] = settings.MEDIA_URL + urlquote(filename)
    return template.loader.render_to_string(template_name, context)

class CompressedMediaNode(template.Node):
    """
    CompressedMediaNodes are configured in a project's settings.py file.

        COMPRESS_DEBUG = False
        COMPRESS = True
        COMPRESS_CSS = {
            'template_widget': {
                 'source_filenames': (
                    'path/to/style/css',
                    ('discovery_widget', 'css'),
                 ),
             'output_filename': 'discovery_widget.css',
             'output_filename_minified': 'discovery_widget.min.css',
             },
        }

    Additionally, applications can configure media settings in a YAML
    media.conf file in the top-level application directory. References to
    application-level settings are listed in the project settings.py file as
    a tuple in the form:

        COMPRESS_CSS = {
            'template_widget': {
                 'source_filenames': (
                    ('discovery_widget', 'css'),
                 ),
             'output_filename': 'discovery_widget.css',
             'output_filename_minified': 'discovery_widget.min.css',
             },
        }

    'css' refers to a key in the YAML media.conf file:

        css:
            - path/to/style.css
    """

    def __init__(self, group_var, media_type, media_settings):
        super(CompressedMediaNode, self).__init__()
        self.group_var = template.Variable(group_var)
        self.media_type = media_type
        self.media_settings = media_settings

    def render(self, context):
        """Main entry point, renders the node."""
        group = self.group_var.resolve(context)
        config = self.media_settings.get(group, None)
        response = ''
        if config is not None:
            render_context = config.get('extra_context', {})
            condition = render_context.get('condition', None)
            template_suffix = self.media_type
            if condition:
                # If a condition is set, then the ie-specific template is
                # required.
                template_suffix += '_ie'
            template_name = 'media_compressor/compressed_%s.html' % \
                (template_suffix,)

            source_filenames = config['source_filenames']
            expanded_source_filenames = \
                expand_source_filenames(source_filenames)
            if len(expanded_source_filenames) > 0:
                if not settings.COMPRESS_DEBUG:
                    if settings.COMPRESS:
                        output_filename = config['output_filename_minified']
                    else:
                        output_filename = config['output_filename']
                    compress_media(output_filename, expanded_source_filenames,
                        settings.COMPRESS)
                    response += render_compressed(output_filename, template_name,
                        render_context)
                else:
                    for source_filename in expanded_source_filenames:
                        response += render_compressed(source_filename,
                            template_name, render_context)
        return response

def compressed_helper(token, media_settings):
    """Helper function used by the various tag implementations."""
    try:
        tag_name, group = token.split_contents()
        media_type = tag_name.replace('compressed_', '')
    except ValueError:
        raise template.TemplateSyntaxError, \
            "Usage: {%% %s js_group %%}" % tag_name
    return CompressedMediaNode(group, media_type, media_settings)

def compressed_js(_, token):
    """
    This outputs script tags for all the JavaScript files in the given group
    if settings.COMPRESSED is False, otherwise it dynamically compresses the
    JavaScript and outputs a single script tag. Groups are defined in
    settings.COMPRESS_JS.

    Usage::

        {% compressed_js project.js %}

    Non compressed output::

        <script type="text/javascript" src="{{ MEDIA_URL }}file1.js" charset="utf-8"></script>
        <script type="text/javascript" src="{{ MEDIA_URL }}file2.js" charset="utf-8"></script>
        <script type="text/javascript" src="{{ MEDIA_URL }}file3.js" charset="utf-8"></script>

    Compressed output::

        <script type="text/javascript" src="{{ MEDIA_URL }}project.js" charset="utf-8"></script>
    """
    return compressed_helper(token, settings.COMPRESS_JS)
register.tag('compressed_js', compressed_js)

def compressed_css(_, token):
    """
    This outputs link elements for all the CSS files in the given group
    if settings.COMPRESSED is False, otherwise it dynamically compresses the
    CSS and outputs a single link element. Groups are defined in
    settings.COMPRESS_CSS.

    Usage::

        {% compressed_css project.css %}

    Non compressed output::

        <link href="{{ MEDIA_URL }}file1.css" rel="stylesheet" type="text/css" />'
        <link href="{{ MEDIA_URL }}file2.css" rel="stylesheet" type="text/css" />'
        <link href="{{ MEDIA_URL }}file3.css" rel="stylesheet" type="text/css" />'

    Compressed output::

        <link href="{{ MEDIA_URL }}project.css" rel="stylesheet" type="text/css" />'
    """
    return compressed_helper(token, settings.COMPRESS_CSS)
register.tag('compressed_css', compressed_css)

