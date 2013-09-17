import socket
from .lib import execnet


#
# Connection Object
#

class Connection(object):

    def __init__(self, hostname, logger=None, sudo=False):
        self.hostname = hostname
        self.gateway = self._make_gateway(hostname)
        self.logger = logger or FakeRemoteLogger()
        self.sudo = sudo

    def _make_gateway(self, hostname):
        if needs_ssh(hostname):
            return execnet.makegateway('ssh=%s' % hostname)
        return execnet.makegateway()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()
        return False

    def execute(self, function, **kw):
        return self.gateway.remote_exec(function, **kw)

    def exit(self):
        self.gateway.exit()


#
# FIXME this is getting ridiculous
#

class FakeRemoteLogger:

    def error(self, *a, **kw):
        pass

    def debug(self, *a, **kw):
        pass

    def info(self, *a, **kw):
        pass

    def warning(self, *a, **kw):
        pass


def needs_ssh(hostname, _socket=None):
    """
    Obtains remote hostname of the socket and cuts off the domain part
    of its FQDN.
    """
    _socket = _socket or socket
    local_hostname = _socket.gethostname()
    local_short_hostname = local_hostname.split('.')[0]
    if local_hostname == hostname or local_short_hostname == hostname:
        return False
    return True
