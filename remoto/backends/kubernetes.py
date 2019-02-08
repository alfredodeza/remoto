from . import BaseConnection


class KubernetesConnection(BaseConnection):

    executable = 'kubectl'
    remote_import_system = 'json'

    def __init__(self, pod_name, namespace=None, **kw):
        self.namespace = namespace
        self.pod_name = pod_name
        super(KubernetesConnection, self).__init__(hostname='localhost', **kw)

    def command_template(self):
        if self.namespace:
            prefix = [
                self.executable, 'exec', '-i', '-n',
                self.namespace, self.pod_name, '--', '/bin/sh', '-c'
            ]
        else:
            prefix = [
                self.executable, 'exec', '-i',
                self.pod_name, '--', '/bin/sh', '-c'
            ]
        return prefix

    def cmd(self, cmd):
        tmpl = self.command_template()
        tmpl.append(' '.join(cmd))
        return tmpl
