"""
Manage locating jinja2 templates in the tiddlywebplugins
package or a local templates dir.

Jinja2 uses a 'loader' to locate requests templates. This
package sets up two loaders, tried in sequence. The first
loader looks in the 'templates' directory in the current
TiddlyWeb instances. This directory name be overridden by
setting plugin_local_templates in tiddlywebconfig.py to
some path.

The second loader looks inside the tiddlywebplugins.templates
package. TiddlyWeb plugins can package default templates into
this location (see tiddlywebplugins.wimporter for an example).

If template is not found in either location, the jinja
TemplateNotFound exception is raised, replicating the standard
jinja behavior.
"""
import os
import urllib

from jinja2 import (Environment, ChoiceLoader, FileSystemLoader,
        PackageLoader)
from tiddlyweb.model.tiddler import timestring_to_datetime
from tiddlyweb.web.util import http_date_from_timestamp

TEMPLATE_ENV = None


def uri(name):
    """URI escape a name."""
    return urllib.quote(name.encode('utf-8'), safe='')


def format_modified(modified_string):
    """Translate a tiddler modified or created string into an http date."""
    return http_date_from_timestamp(modified_string)


def rfc3339(modified_string):
    """Translate a tiddler modified or created string into a rfc3339 date."""
    datetime_object = timestring_to_datetime(modified_string)
    return datetime_object.isoformat('T') + 'Z'


def get_template(environ, template_name):
    """
    Get a template from the Jinja Environment. First try the file loader
    to get the template local to the instance running the code. If it isn't
    there, then try from the tiddlywebplugins package.
    """
    global TEMPLATE_ENV
    if not TEMPLATE_ENV:
        template_path = environ['tiddlyweb.config'].get(
                'plugin_local_templates', 'templates')
        if not os.path.isabs(template_path):
            template_path = os.path.join(environ['tiddlyweb.config'].get(
                'root_dir', ''), template_path)
        try:
            TEMPLATE_ENV = Environment(loader=ChoiceLoader([
                FileSystemLoader(template_path),
                PackageLoader('tiddlywebplugins.templates', 'templates')
                ]))
        except ImportError:  # deal with GAE
            TEMPLATE_ENV = Environment(loader=FileSystemLoader(template_path))
        TEMPLATE_ENV.filters['uri'] = uri
        TEMPLATE_ENV.filters['format_modified'] = format_modified
        TEMPLATE_ENV.filters['rfc3339'] = rfc3339
    return TEMPLATE_ENV.get_template(template_name)
