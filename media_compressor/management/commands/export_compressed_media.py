"""Runs compresses media files and copies them to an export directory.
Usage::

    ./manage.py export_compressed_media --tag=1.0 /path/to/export/dir
"""
import os, re
import shutil

from optparse import make_option

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

import media_compressor.media

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
    make_option('-t', '--tag', action='store', dest='version', type='string',
        help='Append a version string to the output files.'),
    )
    help = """
    Exports compressed media to an external directory with an
    optional version string.

    Usage:

        ./manage.py export_compressed_media --tag=1.0 /path/to/export

    """
    args = '[export directory]'

    def handle(self, *args, **options):
        self.image_ref = r'/\*!MEDIA_URL\*/[^\)]*/images/([^\)]*)'
        self.image_dir = r'images'
        self.version = options.get('version', None)

        if not len(args)==1:
            raise CommandError('An output directory must be provided.')

        self.export_dir = args[0]
        if not os.path.exists(self.export_dir):
            raise CommandError('The export directory does not exist: %s' % self.export_dir)
        elif not os.path.isdir(self.export_dir):
            raise CommandError('Export directory is not a directory: %s' % self.export_dir)

        self.image_output_dir = os.path.join(self.export_dir, self.image_dir)
        if not os.path.exists(self.image_output_dir):
            os.mkdir(self.image_output_dir)

        self.media_root = settings.MEDIA_ROOT
        self.project_root = settings.PROJECT_ROOT

        call_command('jslint')
        call_command('create_compressed_media')

        css_files = ['widgets.css', 'widgets.min.css']
        js_files = ['widgets.js', 'widgets.min.js']

        self.remove_old_media(css_files)
        self.remove_old_media(js_files)

        app_dirs = ['template_widget', 'discovery_widget']

        self.copy_css(css_files, app_dirs)
        self.copy_js(js_files)

    def remove_old_media(self, media_files):
        """Deletes old CSS/JS files in the export directory."""
        for media_file in media_files:
            path = os.path.join(self.export_dir, media_file)
            if os.path.exists(path):
                print 'Deleting: %s' % path
                os.remove(path)

    def copy_images(self, app_dirs, images):
        """Copies CSS-related images into an image directory in the export
        directory.
        """
        for dir in app_dirs:
            src_dir = '%s/%s/media/apps/%s/css/%s' % (self.project_root, dir, dir, self.image_dir)
            print 'Copying images from: %s' % src_dir
            for image in images:
                from_file = os.path.join(src_dir, image)
                if os.path.exists(from_file):
                    if os.path.exists(self.image_output_dir):
                        shutil.copy(from_file, self.image_output_dir)

    def copy_css(self, css_files, app_dirs):
        """Copies CSS files and associated images to the export directory."""
        print 'Copying CSS files.'
        images = []
        for css_file in css_files:
            export_css_file = css_file
            if self.version:
                export_css_file = self.version_file(css_file)

            widget_file = os.path.join(self.media_root, css_file)
            output_file = os.path.join(self.export_dir, export_css_file)
            in_file = open(widget_file, 'r')
            out_file = open(output_file, 'w')
            regex = re.compile(self.image_ref)
            for line in in_file:
                match = regex.search(line)
                if not match is None:
                    images.append(match.groups()[0])
                out_file.write(regex.sub(r'%s/\1' % self.image_dir, line))
            in_file.close()
            out_file.close()
        self.copy_images(app_dirs, images)

    def copy_js (self, js_files):
        """Copies Javascript files to the export directory."""
        print 'Copying Javascript files.'
        for js_file in js_files:
            export_js_file = js_file
            if self.version:
                export_js_file = self.version_file(js_file)
            from_file = os.path.join(self.media_root, js_file)
            shutil.copy(from_file, os.path.join(self.export_dir, export_js_file))

    def version_file(self, file_name):
        file_parts = os.path.splitext(file_name)
        version = self.version.strip()
        if not version == '':
            version = '-%s' % version
        return version.join(file_parts)
