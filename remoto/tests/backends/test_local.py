import sys
from remoto.backends import local


class TestLocalConnection(object):

    def test_hostname_gets_ignored(self):
        conn = local.LocalConnection(hostname='node1')
        assert conn.hostname == 'localhost'

    def test_defaults_to_localhost_name(self):
        conn = local.LocalConnection()
        assert conn.hostname == 'localhost'


class TestMakeConnectionstring(object):

    def test_makes_sudo_python_no_ssh(self):
        conn = local.LocalConnection(sudo=True, eager=False, interpreter='python')
        conn_string = conn._make_connection_string('srv1', _needs_ssh=lambda x: False)
        assert conn_string == 'popen//python=sudo python'

    def test_makes_sudo_python_with_ssh(self):
        conn = local.LocalConnection(sudo=True, eager=False, interpreter='python')
        conn_string = conn._make_connection_string('srv1', _needs_ssh=lambda x: True)
        assert conn_string == 'popen//python=sudo python'

    def test_makes_sudo_python_with_ssh_options_ignored(self):
        conn = local.LocalConnection(
            sudo=True, eager=False,
            interpreter='python', ssh_options='-F vagrant_ssh_config')
        conn_string = conn._make_connection_string('srv1', _needs_ssh=lambda x: True)
        assert conn_string == 'popen//python=sudo python'

    def test_makes_python_no_ssh(self):
        conn = local.LocalConnection(sudo=False, eager=False, interpreter='python')
        conn_string = conn._make_connection_string('srv1', _needs_ssh=lambda x: False)
        assert conn_string == 'popen//python=python'

    def test_makes_sudo_python_with_forced_sudo(self):
        conn = local.LocalConnection(sudo=True, eager=False, interpreter='python')
        conn_string = conn._make_connection_string(
            'srv1',
            _needs_ssh=lambda x: False, use_sudo=True
        )
        assert conn_string == 'popen//python=sudo python'

    def test_does_not_make_sudo_python_with_forced_sudo(self):
        conn = local.LocalConnection(sudo=True, eager=False, interpreter='python')
        conn_string = conn._make_connection_string(
            'srv1',
            _needs_ssh=lambda x: False, use_sudo=False
        )
        assert conn_string == 'popen//python=python'

    def test_detects_python3(self, monkeypatch):
        monkeypatch.setattr(sys, 'version_info', (3, 5, 1))
        conn = local.LocalConnection(sudo=True, eager=False)
        conn_string = conn._make_connection_string('srv1', _needs_ssh=lambda x: False)
        assert conn_string == 'popen//python=sudo python3'

    def test_detects_python2(self, monkeypatch):
        monkeypatch.setattr(sys, 'version_info', (2, 7, 11))
        conn = local.LocalConnection(sudo=False, eager=False)
        conn_string = conn._make_connection_string('srv1', _needs_ssh=lambda x: True)
        assert conn_string == 'popen//python=python2'
