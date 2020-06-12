from pytest import raises
from remoto.backends import docker


class TestDockerConnection(object):

    def test_missing_container_identifier(self):
        with raises(TypeError):
            docker.DockerConnection(hostname='node1')

    def test_defaults_to_localhost_name(self):
        conn = docker.DockerConnection(container_name='container-1')
        assert conn.hostname == 'localhost'

    def test_defaults_to_localhost_id(self):
        conn = docker.DockerConnection(container_id='asdf-lkjh')
        assert conn.hostname == 'localhost'


class TestCommandTemplate(object):

    def test_with_user(self):
        conn = docker.DockerConnection(container_id='asdf-lkjh', user='root')
        tmpl = conn.command_template()
        assert tmpl == [
            'docker', 'exec', '-i',
            '-u', 'root',
            'asdf-lkjh', '/bin/sh', '-c']

    def test_no_user(self):
        conn = docker.DockerConnection(container_id='asdf-lkjh')
        tmpl = conn.command_template()
        assert tmpl == [
            'docker', 'exec', '-i',
            'asdf-lkjh', '/bin/sh', '-c'
        ]


class TestCommand(object):

    def test_user_conn_appends(self):
        conn = docker.DockerConnection(container_id='asdf-lkjh', user='root')
        result = conn.cmd(['ceph', '--version'])
        assert result == [
            'docker', 'exec', '-i', '-u', 'root',
            'asdf-lkjh', '/bin/sh', '-c', 'ceph --version'
        ]

    def test_default_appends(self):
        conn = docker.DockerConnection(container_id='asdf-lkjh')
        result = conn.cmd(['ceph', 'health'])
        assert result == [
            'docker', 'exec', '-i',
            'asdf-lkjh', '/bin/sh', '-c', 'ceph health'
        ]
