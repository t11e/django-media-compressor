"""
Support for running the JsTestDriver server.

Usage::

    ./manage.py runserver_js_test_driver

Optionally, you can specify the port of the test server (default is 4224)::

    ./manage.py runserver_js_test_driver -p 4224

Then point all the browsers that you want to test on to the server component
to register them::

  http://localhost:4224/capture

"""
from optparse import make_option
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Run the JsTestDriver server."""
    option_list = BaseCommand.option_list + (
        make_option('--port', '-p', action='store', dest='port', default='4224',
            help='The port on which to run'),
    )
    help = "Run the js-test-driver server."

    def handle(self, *_, **options):
        """Main entry point for the command."""
        subprocess.check_call(['java',
            '-jar', settings.JS_TEST_DRIVER_JAR_PATH,
            '--port', options['port']
        ])
