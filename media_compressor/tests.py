"""
Unit tests for media_compressor.
"""

from django.conf import settings
from django.template import Context, Template
from django.test import TestCase

from media_compressor.templatetags import media_compressor_tags

class AsJsonTemplateFilterTest(TestCase): #pylint: disable-msg=R0904
    """Tests for the as_json filter"""

    def test_string(self):
        """Verify strings are converted to JSON correctly."""
        self.assertEqual('>foo<',
            Template('>{{ "foo" }}<').render(Context({})))
        self.assertEqual('>"foo"<',
            Template('>{{ "foo"|as_json }}<').render(Context({})))

    def test_list(self):
        """Verify lists are converted to JSON correctly."""
        self.assertEqual('>[1, 2, 3]<',
            Template('>{{ v|as_json }}<').render(Context({'v': [1,2,3]})))

    def test_dictionary(self):
        """Verify dictionaries are converted to JSON correctly."""
        self.assertEqual('>{"a": "A"}<',
            Template('>{{ v|as_json }}<').render(Context({'v': {'a': 'A'}})))

    def test_indent(self):
        """Verify indentation works correctly."""
        self.assertEqual('>[\n  1, \n  2, \n  3\n]<',
            Template('>{{ v|as_json:"indent=2" }}<').render(
                Context({'v': [1,2,3]})))


def _nop_compress_media(_output_filename, _source_filenames, compress):
    """Do nothing version of media_compressor.media.compress_media to make
    testing easier."""
    pass

class CompressedMediaTemplateTagTest(TestCase): #pylint: disable-msg=R0904
    """Verify the compressed_js and compressed_css tags work correctly,
    this test case disables the actual compression and concatenation code
    and just checks that the appropriate script tags are output."""

    def setUp(self): #pylint: disable-msg=C0103,C0111
        self.old_compress_debug = settings.COMPRESS_DEBUG
        self.old_compress = settings.COMPRESS
        self.old_compress_js = settings.COMPRESS_JS
        self.old_compress_css = settings.COMPRESS_CSS
        self.old_compress_media = media_compressor_tags.compress_media
        media_compressor_tags.compress_media = _nop_compress_media

        settings.COMPRESS_JS = {
            'empty_js': {
                 'source_filenames': (),
                 'output_filename': 'empty.js',
                 'output_filename_minified': 'empty.min.js',
             },
            'zab_js': {
                 'source_filenames': ('zzz.js', 'aaa.js', 'bbb.js'),
                 'output_filename': 'zab.js',
                 'output_filename_minified': 'zab.min.js',
             },
        }
        settings.COMPRESS_CSS = {
            'empty_css': {
                 'source_filenames': (),
                 'output_filename': 'empty.css',
                 'output_filename_minified': 'empty.min.css',
             },
            'zab_css': {
                 'source_filenames': ('zzz.css', 'aaa.css', 'bbb.css'),
                 'output_filename': 'zab.css',
                 'output_filename_minified': 'zab.min.css',
             },
        }

    def tearDown(self): #pylint: disable-msg=C0103,C0111
        settings.COMPRESS_DEBUG = self.old_compress_debug
        settings.COMPRESS = self.old_compress
        settings.COMPRESS_JS = self.old_compress_js
        settings.COMPRESS_CSS = self.old_compress_css
        media_compressor_tags.compress_media = self.old_compress_media

    def test_compress_debug_empty_js(self):
        """Test that compressed_js works when COMPRESS_DEBUG is True with
        an empty set of files."""
        settings.COMPRESS_DEBUG = True
        self.assertEqual('><' % {'media_url': settings.MEDIA_URL},
            Template('>{% compressed_js "empty_js" %}<').render(Context({})))

    def test_compress_empty_js(self):
        """Test that compressed_js works when COMPRESS_DEBUG is False with
        an empty set of files."""
        settings.COMPRESS_DEBUG = False
        self.assertEqual('><' % {'media_url': settings.MEDIA_URL},
            Template('>{% compressed_js "empty_js" %}<').render(Context({})))

    def test_compress_debug_empty_css(self):
        """Test that compressed_css works when COMPRESS_DEBUG is True with
        an empty set of files."""
        settings.COMPRESS_DEBUG = True
        self.assertEqual('><' % {'media_url': settings.MEDIA_URL},
            Template('>{% compressed_css "empty_css" %}<').render(Context({})))

    def test_compress_empty_css(self):
        """Test that compressed_css works when COMPRESS_DEBUG is False with
        an empty set of files."""
        settings.COMPRESS_DEBUG = False
        self.assertEqual('><' % {'media_url': settings.MEDIA_URL},
            Template('>{% compressed_css "empty_css" %}<').render(Context({})))

    def test_compress_debug_zab_js(self):
        """Test that compressed_js works when COMPRESS_DEBUG is True."""
        settings.COMPRESS_DEBUG = True
        self.assertEqual( \
            '>'
            '<script type="text/javascript" src="%(media_url)szzz.js" '
                'charset="utf-8"></script>'
            '<script type="text/javascript" src="%(media_url)saaa.js" '
                'charset="utf-8"></script>'
            '<script type="text/javascript" src="%(media_url)sbbb.js" '
                'charset="utf-8"></script>'
            '<' % {'media_url': settings.MEDIA_URL},
            Template('>{% compressed_js "zab_js" %}<').render(Context({})))

    def test_compress_zab_js(self):
        """Test that compressed_js works when COMPRESS_DEBUG is False."""
        settings.COMPRESS_DEBUG = False
        self.assertEqual( \
            '>'
            '<script type="text/javascript" src="%(media_url)szab.js" '
                'charset="utf-8"></script>'
            '<' % {'media_url': settings.MEDIA_URL},
            Template('>{% compressed_js "zab_js" %}<').render(Context({})))

    def test_compress_debug_zab_css(self):
        """Test that compressed_css works when COMPRESS_DEBUG is True."""
        settings.COMPRESS_DEBUG = True
        self.assertEqual( \
            '>'
            '<link href="%(media_url)szzz.css" rel="stylesheet" '
                'type="text/css" />'
            '<link href="%(media_url)saaa.css" rel="stylesheet" '
                'type="text/css" />'
            '<link href="%(media_url)sbbb.css" rel="stylesheet" '
                'type="text/css" />'
            '<' % {'media_url': settings.MEDIA_URL},
            Template('>{% compressed_css "zab_css" %}<').render(Context({})))

    def test_compress_zab_css(self):
        """Test that compressed_js works when COMPRESS_DEBUG is False."""
        settings.COMPRESS_DEBUG = False
        self.assertEqual( \
            '>'
            '<link href="%(media_url)szab.css" rel="stylesheet" '
                'type="text/css" />'
            '<' % {'media_url': settings.MEDIA_URL},
            Template('>{% compressed_css "zab_css" %}<').render(Context({})))
