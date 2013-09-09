from .lib import execnet


#
# Connection Object
#

class Connection(object):

    def __init__(self, hostname, logger=None, sudo=False):
        self.hostname = hostname
        self.gateway = execnet.makegateway('ssh=%s' % hostname)
        self.logger = logger or FakeRemoteLogger()
        self.sudo = sudo

    def execute(self, function, **kw):
        return self.gateway.remote_exec(function, **kw)

    def exit(self):
        self.gateway.exit()


class FakeRemoteLogger:

    def error(self, *a, **kw):
        pass

    def debug(self, *a, **kw):
        pass

    def info(self, *a, **kw):
        pass
