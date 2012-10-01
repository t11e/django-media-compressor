"""
Media module that provides methods to get the paths for all installed
Django applications, serve static media from those paths and compress
JavaScript and CSS files.
"""
import os.path
import fnmatch
import yaml
import pkg_resources
import subprocess


from django.conf import settings
from django.http import Http404
from django.views.static import serve

def _find_app_roots():
    """Return a list of root paths for each installed Django Application."""
    resource_manager = pkg_resources.ResourceManager()
    apps = list(settings.INSTALLED_APPS)
    apps.reverse()
    app_roots = []
    for app in apps:
        provider = pkg_resources.get_provider(app)
        try:
            app_root = provider.get_resource_filename(resource_manager, 'media')
        except KeyError:
            app_root = None
        if app_root is not None and os.path.isdir(app_root):
            if not app_root.endswith('/'):
                app_root += '/'
            app_roots.append(app_root)
    return app_roots

def find_media(root_dir, pattern):
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if fnmatch.fnmatch(filename, pattern):
                yield os.path.join(os.path.pardir, dirpath, filename)

_APP_ROOTS = None
def get_app_roots():
    """Return a list of root paths for each installed Django Application,
    cached for speed."""
    global _APP_ROOTS #pylint: disable-msg=W0603
    if _APP_ROOTS is None:
        _APP_ROOTS = _find_app_roots()
    return _APP_ROOTS

def serve_from_apps(request, path, document_root=None):
    """Wrapper around django.views.static.serve that tries the generic
    view first and then falls back to the various media directories in
    any installed applications before giving up."""
    if document_root is not None and document_root != '':
        try:
            return serve(request, path, document_root=document_root)
        except Http404:
            pass # Try from an app instead
    for app_root in get_app_roots():
        try:
            return serve(request, path, document_root=app_root)
        except Http404:
            pass # Try the next app
    raise Http404, '"%s" does not exist' % path

def expand_source_filenames(source_filenames):
    """
    Expands django application references in the source_filenames list to a
    list of source files by loading the media.conf file for that django
    application, if it exists.

    """
    resource_manager = pkg_resources.ResourceManager()
    new_source_list = []

    for source in source_filenames:
        if isinstance(source, tuple):
            try:
                new_source = source[0]
                new_group = source[1]
                # TODO: This code should use a variant of get_app_roots
                # so the resource access is better cached. I'd advise
                # altering get_app_roots to return an array of tuples
                # which can then be filtered by app name.
                if new_source in settings.INSTALLED_APPS:
                    try:
                        provider = pkg_resources.get_provider(new_source)
                        media_conf = provider.get_resource_string(
                            resource_manager, 'media.conf')
                        media_data = yaml.load(media_conf)
                        if media_data:
                            group = media_data[new_group]
                            if group:
                                new_source_list.extend(group)
                    except IOError:
                        pass
            except IndexError:
                pass
        else:
            new_source_list.append(source)
    return new_source_list

def resolve_media_paths(paths):
    """For each given path convert it to the first matching path in any
    installed applications media directory. Raises an error if any of the
    paths can't be found."""
    converted_paths = {}
    for media_root in get_app_roots():
        for path in paths:
            if path not in converted_paths:
                candidate = os.path.join(media_root, path)
                if os.path.isfile(candidate):
                    converted_paths[path] = candidate
    new_paths = []
    for path in paths:
        try:
            converted = converted_paths[path]
        except KeyError:
            raise IOError("Couldn't locate media file: %s" % path)
        new_paths.append(converted)
    return new_paths

def compress_media(output_filename, source_filenames, compress):
    """Compress and concatenate all the source_filenames into the
    output_filename if any have changed or the output is missing."""
    source_filenames = resolve_media_paths(source_filenames)
    source_mtime = max([os.stat(f).st_mtime for f in source_filenames])
    output_path = os.path.join(settings.MEDIA_ROOT, output_filename)
    try:
        output_stat = os.stat(output_path)
        output_mtime = output_stat.st_mtime
    except OSError:
        output_mtime = None
    changed = False
    if output_mtime is None or source_mtime >= output_mtime:
        changed = True
        output_file = open(output_path, 'w')
        try:
            for source_filename in source_filenames:
                source_path = source_filename
                if not os.path.isfile(source_path):
                    raise IOError("Couldn't locate media file: %s" %
                        (source_path,))
                if compress:
                    # TODO This would be quicker if we keep a copy of each shrunk
                    # file and only shrink the ones that have changed, concatenating
                    # them all at the end.
                    subprocess.check_call(
                        ['java', '-jar', settings.YUI_COMPRESSOR_PATH, source_path],
                        stdout=output_file)
                else:
                    source_file = open(source_path, 'r')
                    source_data = source_file.read()
                    source_file.close()
                    output_file.write(source_data)
        finally:
            output_file.close()
    return (output_path, changed,)
