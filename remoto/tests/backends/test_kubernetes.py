from remoto.backends import kubernetes


class TestCommandTemplate(object):

    def test_using_podname_only(self):
        conn = kubernetes.KubernetesConnection('rook-ceph-asdf')
        tmpl = conn.command_template()
        assert tmpl == ['kubectl', 'exec', '-i', 'rook-ceph-asdf', '--', '/bin/sh', '-c']

    def test_using_namespace(self):
        conn = kubernetes.KubernetesConnection('rook-ceph-asdf', 'rook-ceph')
        tmpl = conn.command_template()
        assert tmpl == [
            'kubectl', 'exec', '-i', '-n', 'rook-ceph',
            'rook-ceph-asdf', '--', '/bin/sh', '-c'
        ]

    def test_using_context(self):
        conn = kubernetes.KubernetesConnection('rook-ceph-asdf', context='4')
        tmpl = conn.command_template()
        assert tmpl == [
            'kubectl', '--context', '4', 'exec', '-i',
            'rook-ceph-asdf', '--', '/bin/sh', '-c'
        ]

    def test_using_context_and_namespace(self):
        conn = kubernetes.KubernetesConnection('rook-ceph-asdf', 'rook-ceph', context='4')
        tmpl = conn.command_template()
        assert tmpl == [
            'kubectl', '--context', '4', 'exec', '-i', '-n', 'rook-ceph',
            'rook-ceph-asdf', '--', '/bin/sh', '-c'
        ]


class TestCommand(object):

    def test_podname_conn_appends(self):
        conn = kubernetes.KubernetesConnection('rook-ceph-asdf', 'rook-ceph')
        result = conn.cmd(['ceph', '--version'])
        assert result == [
            'kubectl', 'exec', '-i', '-n', 'rook-ceph',
            'rook-ceph-asdf', '--', '/bin/sh', '-c', 'ceph --version'
        ]

    def test_namespace_appends(self):
        conn = kubernetes.KubernetesConnection('rook-ceph-asdf', 'rook-ceph')
        result = conn.cmd(['ceph', 'health'])
        assert result == [
            'kubectl', 'exec', '-i', '-n', 'rook-ceph',
            'rook-ceph-asdf', '--', '/bin/sh', '-c', 'ceph health'
        ]
