from . import BaseConnection


class DockerConnection(BaseConnection):
    """
    This connection class allows to (optionally) define a remote hostname
    to connect that holds a given container::

        >>> conn = DockerConnection(hostname='srv-1', container_id='asdf-lkjh')

    Either ``container_id`` or ``container_name`` can be provided to connect to
    a given container.

    .. note:: ``hostname`` defaults to 'localhost' when undefined
    """

    executable = 'docker'
    remote_import_system = 'json'

    def __init__(self, hostname=None, container_id=None, container_name=None, user=None, **kw):
        self.hostname = hostname or 'localhost'
        self.identifier = container_id or container_name
        if not self.identifier:
            raise TypeError('Either container_id or container_name must be provided')
        self.user = user
        super(DockerConnection, self).__init__(hostname=self.hostname, **kw)

    def command_template(self):
        if self.user:
            prefix = [
                self.executable, 'exec', '-i',
                '-u', self.user,
                self.identifier, '/bin/sh', '-c'
            ]
        else:
            prefix = [
                self.executable, 'exec', '-i',
                self.identifier, '/bin/sh', '-c'
            ]
        return prefix

    def cmd(self, cmd):
        tmpl = self.command_template()
        tmpl.append(' '.join(cmd))
        return tmpl
