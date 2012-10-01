"""
Generate project documentation using Sphinx (http://sphinx.pocoo.org/).

Generate documentation for all installed applications::

    ./manage.py pydoc

Generate documentation for a specific app or apps::

    ./manage.py pydoc django_extras dynamic_model

"""
import subprocess
import os
import sys

from django_extras.management.commands import AppsCommand

class Command(AppsCommand):
    """Run sphinx over the Django applications to generate documentation from
    docstrings.
    """
    help = "Generate documentation from docstrings."

    def handle_app(self, app_name, app_module, app_path, _explict_apps,
        **options):
        """Main entry point for the command."""
        cwd = os.path.join(app_path, 'docs')
        if not os.path.exists(cwd):
            print "Documentation directory does not exist for %s:" % app_name
            print "    %s" % cwd
            return
        else:
            print 'Running sphinx over %s' % app_name

        cmd = [
               'sphinx-build',
               '-b', 'html',
               cwd,
               os.path.join(app_path, cwd, '_build', 'html'),
               ]
        # Poke in our current Python path so the Django apps can be
        # found from the subprocess.
        env = dict(os.environ)
        env['PYTHONPATH'] = os.pathsep.join(sys.path)
        subprocess.check_call(cmd, env=env, cwd=cwd)

