from . import BaseConnection


class KubernetesConnection(BaseConnection):

    executable = 'kubectl'
    remote_import_system = 'json'

    def __init__(self, pod_name, namespace=None, context=None, **kw):
        self.namespace = namespace
        self.context = context
        self.pod_name = pod_name
        super(KubernetesConnection, self).__init__(hostname='localhost', **kw)

    def command_template(self):
        base_command = [self.executable]
        if self.context:
            base_command.extend(['--context', self.context])

        base_command.extend(['exec', '-i'])

        if self.namespace:
            base_command.extend(['-n', self.namespace])

        base_command.extend([
            self.pod_name,
            '--',
            '/bin/sh',
            '-c'
        ])
        return base_command

    def cmd(self, cmd):
        tmpl = self.command_template()
        tmpl.append(' '.join(cmd))
        return tmpl
