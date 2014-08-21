"""JSON Framework Extension"""

import sys
import json
from ..core import output, backend, hook, handler
from ..utils.misc import minimal_logger
from ..ext.ext_configparser import ConfigParserConfigHandler

LOG = minimal_logger(__name__)


def add_json_option(app):
    """
    This is a ``post_setup`` hook that adds the ``--json`` argument to the
    argument object.

    :param app: The application object.

    """
    app.args.add_argument('--json', dest='output_handler',
                          action='store_const',
                          help='toggle json output handler',
                          const='json')


def set_output_handler(app):
    """
    This is a ``pre_run`` hook that overrides the configured output handler
    if ``--json`` is passed at the command line.

    :param app: The application object.

    """
    if '--json' in app._meta.argv:
        app._meta.output_handler = 'json'
        app._setup_output_handler()


class JsonOutputHandler(output.CementOutputHandler):

    """
    This class implements the :ref:`IOutput <cement.core.output>`
    interface.  It provides JSON output from a data dictionary using the
    `json <http://docs.python.org/library/json.html>`_ module of the standard
    library.

    Note: The cement framework detects the '--json' option and suppresses
    output (same as if passing --quiet).  Therefore, if debugging or
    troubleshooting issues you must pass the --debug option to see whats
    going on.

    """
    class Meta:

        """Handler meta-data"""

        interface = output.IOutput
        """The interface this class implements."""

        label = 'json'
        """The string identifier of this handler."""

    def __init__(self, *args, **kw):
        super(JsonOutputHandler, self).__init__(*args, **kw)

    def render(self, data_dict, template=None):
        """
        Take a data dictionary and render it as Json output.  Note that the
        template option is received here per the interface, however this
        handler just ignores it.

        :param data_dict: The data dictionary to render.
        :param template: This option is completely ignored.
        :returns: A JSON encoded string.
        :rtype: str

        """
        LOG.debug("rendering output as Json via %s" % self.__module__)
        sys.stdout = backend.__saved_stdout__
        sys.stderr = backend.__saved_stderr__
        return json.dumps(data_dict)


class JsonConfigHandler(ConfigParserConfigHandler):
    """
    This class implements the :ref:`IConfig <cement.core.config>`
    interface, and provides the same functionality of
    :ref:`ConfigParserConfigHandler <cement.ext.ext_configparser>`
    but with JSON configuration files.

    """
    class Meta:
        label = 'json'

    def __init__(self, *args, **kw):
        super(JsonConfigHandler, self).__init__(*args, **kw)

    def _parse_file(self, file_path):
        """
        Parse JSON configuration file settings from file_path, overwriting
        existing config settings.  If the file does not exist, returns False.

        :param file_path: The file system path to the JSON configuration file.
        :returns: boolean

        """
        self.merge(json.load(open(file_path)))

        # FIX ME: Should check that file was read properly, however if not it
        # will likely raise an exception anyhow.
        return True


def load(app):
    hook.register('post_setup', add_json_option)
    hook.register('pre_run', set_output_handler)
    handler.register(JsonOutputHandler)
    handler.register(JsonConfigHandler)
