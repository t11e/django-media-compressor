"""
Support for running the JsTestDriver tests.

Usage::

    ./manage.py test_js_test_driver

Note that you'll want to run the runserver_js_test_driver command first
and registered at least one browser with it before running this
"""
from optparse import make_option
import os
import re
import subprocess

from django.conf import settings
from django.core.management.base import CommandError

from django_extras.management.commands import AppsCommand

_SUMMARY_PATTERN = re.compile(r"""^Total (?P<total>\d+) tests """
    """\(Passed: (?P<passed>\d+); Fails: (?P<failed>\d+); Errors: """
    """(?P<error>\d+)\)""")

_BROWSER_PATTERN = re.compile(r"""^  .*: Run \d+ tests """)

class Command(AppsCommand):
    """Command to run JavaScript tests using JsTestDriver."""
    option_list = AppsCommand.option_list + (
        make_option('--tests', '-t', action='store', dest='tests',
            default='all',
            help='The tests to run, defaults to all'),
    )
    help = "Run the JavaScript unit tests for the named applications."

    def handle_app(self, app_name, app_module, app_path, explicit_app,
        **options):
        """Main entry point for the command."""
        config_path = os.path.join(app_path, 'jsTestDriver.conf')
        if not os.path.isfile(config_path):
            if not explicit_app:
                # We are an autodetected app with no configuration,
                # don't do anything
                return
            else:
                raise CommandError("The application js-test-driver config"
                    " couldn't be found %s" % (config_path,))

        print 'Running js-test-driver tests on %s' % app_name

        report_count = 0
        tests_run = 0
        tests_failed = 0
        tests_erred = 0

        out = subprocess.Popen(
            ['java', '-jar', settings.JS_TEST_DRIVER_JAR_PATH,
            '--config', config_path,
            '--tests', options['tests']],
            cwd=app_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT)
        for line in out.stdout:
            print '  %s' % line,
            match = _SUMMARY_PATTERN.match(line)
            if match is not None:
                data = match.groupdict()
                tests_run += int(data['total'])
                tests_failed += int(data['failed'])
                tests_erred += int(data['error'])
            if _BROWSER_PATTERN.match(line) is not None:
                report_count += 1

        out.wait()
        if out.returncode != 0:
            raise CommandError('js-test-driver failed to run, are you running'
                'your server?')

        if report_count == 0:
            raise CommandError('No browsers are attached to the test server')
        if tests_run == 0:
            raise CommandError('No tests were run, is there an error in the'
                ' config file? %s' % (config_path,))
        if tests_failed > 0 or tests_erred > 0:
            raise CommandError('Tests failed: %s failed, %s erred, %s ran.' %
                (tests_failed, tests_erred, tests_run))
        print 'Tests passed: %s tests total across %s browsers' % \
            (tests_run, report_count)
