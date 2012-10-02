"""
Builds any compressed media as specified in settings.py.

Usage::

    ./manage.py create_compressed_media

"""
from django.conf import settings
from django.core.management.base import BaseCommand

from media_compressor.media import compress_media, expand_source_filenames

class Command(BaseCommand):
    """Build the compressed media."""
    help = "Build the compressed media."

    def handle(self, *_, **options):
        """Main entry point for the command."""
        build_compressed_media('JavaScript', settings.COMPRESS_JS)
        build_compressed_media('CSS', settings.COMPRESS_CSS)

def build_compressed_media(media_name, media_options):
    """Run over all the compressed media in settings.py and
    trigger the manual build process for it."""
    print 'Building compressed %s media:' % (media_name,)
    for group_name, group_options in media_options.items():
        print '  %s:' % (group_name,)
        output_filename = group_options['output_filename']
        source_filenames = group_options['source_filenames']
        source_filenames = expand_source_filenames(source_filenames)
        output_path, changed = compress_media(output_filename,
            source_filenames, False)
        print '    Plain:'
        print '      changed: %s' % (changed,)
        print '      path: %s' % (output_path,)
        output_filename = group_options['output_filename_minified']
        output_path, changed = compress_media(output_filename,
            source_filenames, True)
        print '    Minified:'
        print '      changed: %s' % (changed,)
        print '      path: %s' % (output_path,)
