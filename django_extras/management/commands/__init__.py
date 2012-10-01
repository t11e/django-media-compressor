"""
Commands module for django_extras.
"""
import os.path
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import django.db.models.loading

class AppsCommand(BaseCommand):
    """Useful variant of BaseCommand that works across all installed Django
    applications or only across the ones named on the command line."""
    option_list = BaseCommand.option_list
    args = '[appname appname ...]'
    label = 'application name'

    def handle(self, *app_labels, **options):
        """Main entry point for the command."""
        explicit_apps = True
        if not app_labels:
            app_labels = list(settings.INSTALLED_APPS)
            explicit_apps = False

        apps = []
        for app_name in app_labels:
            if app_name == app_name.split('.')[-1]:
                app_module = django.db.models.loading.load_app(app_name, False)
                if app_module is None and explicit_apps:
                    raise CommandError("The application %s couldn't be located"
                        % app_name)
                if app_module is not None:
                    apps.append((app_name, app_module))

        output = []
        for app_name, app_module in apps:
            app_path = os.path.dirname(app_module.__file__)
            if os.path.basename(app_module.__file__).startswith('__init__.'):
                app_path = os.path.abspath(os.path.join(app_path, '..'))
            app_output = self.handle_app(app_name, app_module, app_path,
                explicit_apps, **options)
            if app_output:
                output.append(app_output)
        return '\n'.join(output)


    def handle_app(self, app_name, app_module, app_path, explicit_apps,
        **options):
        """Hook to be overridden which is called for every application that
        should be processed."""
        pass

class MediaAppsCommand(AppsCommand):
    """Base class for media related AppsCommands."""

    def __init__(self, media_dir, media_name):
        super(MediaAppsCommand, self).__init__()
        self.media_dir = media_dir
        self.media_name = media_name

    def handle_app(self, app_name, app_module, app_path, explicit_app,
        **options):
        """Main entry point for the command."""
        media_path = os.path.join(app_path, 'media', 'apps', app_name,
            self.media_dir)
        if not os.path.isdir(media_path):
            if not explicit_app:
                # We are an autodetected app with no configuration,
                # don't do anything
                return
            else:
                raise CommandError("The application has no %s files in %s" % \
                    (self.media_name, media_path,))
        self.handle_app_media(app_name, media_path, **options)

    def handle_app_media(self, app_name, media_path, **options):
        """Abstract method that performs the command."""
        pass
