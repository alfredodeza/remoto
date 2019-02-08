from . import BaseConnection
import socket


class LocalConnection(BaseConnection):

    def __init__(self, **kw):
        # hostname gets ignored, and forced to be localhost always
        kw.pop('hostname', None)
        super(LocalConnection, self).__init__(
            hostname='localhost',
            detect_sudo=False,
            **kw
        )

    def _make_connection_string(self, hostname, _needs_ssh=None, use_sudo=None):
        interpreter = self.interpreter
        if use_sudo is not None:
            if use_sudo:
                interpreter = 'sudo ' + interpreter
        elif self.sudo:
            interpreter = 'sudo ' + interpreter
        return 'popen//python=%s' % interpreter
