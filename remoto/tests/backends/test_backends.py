import sys
from mock import Mock, patch
import pytest
from remoto import backends
from remoto.backends import local
from remoto.tests import fake_module
from remoto.tests.conftest import Capture, Factory


class FakeSocket(object):

    def __init__(self, gethostname, getfqdn=None):
        self.gethostname = lambda: gethostname
        self.getfqdn = lambda: getfqdn or gethostname


class TestJsonModuleExecute(object):

    def test_execute_returns_casted_boolean(self):
        conn = local.LocalConnection()
        conn.remote_import_system = 'json'
        remote_fake_module = conn.import_module(fake_module)
        assert remote_fake_module.function(None) is True

    def test_execute_can_raise_remote_exceptions(self):
        conn = local.LocalConnection()
        conn.remote_import_system = 'json'
        remote_fake_module = conn.import_module(fake_module)
        with pytest.raises(Exception) as error:
            assert remote_fake_module.fails()
        assert 'Exception: failure from fails() function' in str(error.value)

    def test_execute_can_raise_unexpected_remote_exceptions(self):
        conn = local.LocalConnection()
        conn.remote_import_system = 'json'
        remote_fake_module = conn.import_module(fake_module)
        with pytest.raises(Exception) as error:
            remote_fake_module.unexpected_fail()
        assert 'error calling "unexpected_fail"' in str(error.value)
        assert 'Unexpected remote exception' in str(error.value)

    def test_execute_noop(self):
        conn = local.LocalConnection()
        conn.remote_import_system = 'json'
        remote_fake_module = conn.import_module(fake_module)
        assert remote_fake_module.noop() is None

    def test_execute_passes_is_none(self):
        conn = local.LocalConnection()
        conn.remote_import_system = 'json'
        remote_fake_module = conn.import_module(fake_module)
        assert remote_fake_module.passes() is None


class TestNeedsSsh(object):

    def test_short_hostname_matches(self):
        socket = FakeSocket('foo.example.org')
        assert backends.needs_ssh('foo', socket) is False

    def test_long_hostname_matches(self):
        socket = FakeSocket('foo.example.org')
        assert backends.needs_ssh('foo.example.org', socket) is False

    def test_hostname_does_not_match(self):
        socket = FakeSocket('foo')
        assert backends.needs_ssh('meh', socket) is True

    def test_fqdn_hostname_matches_short_hostname(self):
        socket = FakeSocket('foo', getfqdn='foo.example.org')
        assert backends.needs_ssh('foo.example.org', socket) is False

    @pytest.mark.parametrize('hostname', ['localhost', '127.0.0.1', '127.0.1.1'])
    def test_local_hostname(self, hostname):
        assert backends.needs_ssh(hostname) is False


class FakeGateway(object):

    def remote_exec(self, module):
        pass


class TestLegacyRemoteModule(object):

    def setup(self):
        self.conn = backends.BaseConnection('localhost', sudo=True, eager=False)
        self.conn.gateway = FakeGateway()

    def test_importing_it_sets_it_as_remote_module(self):
        self.conn.import_module(fake_module)
        assert fake_module == self.conn.remote_module.module

    def test_importing_it_returns_the_module_too(self):
        remote_foo = self.conn.import_module(fake_module)
        assert remote_foo.module == fake_module

    def test_execute_the_remote_module_send(self):
        stub_channel = Factory(send=Capture(), receive=Capture())
        self.conn.gateway.channel = self.conn.gateway
        remote_foo = self.conn.import_module(fake_module)
        remote_foo.channel = stub_channel
        remote_foo.function('argument')
        assert stub_channel.send.calls[0]['args'][0] == "function('argument')"

    def test_execute_the_remote_module_receive(self):
        stub_channel = Factory(receive=Capture(return_values=[True]), send=Capture())
        self.conn.gateway.channel = self.conn.gateway
        remote_foo = self.conn.import_module(fake_module)
        remote_foo.channel = stub_channel
        assert remote_foo.function('argument') is True


class TestLegacyModuleExecuteArgs(object):

    def setup(self):
        self.remote_module = backends.LegacyModuleExecute(FakeGateway(), None)

    def test_single_argument(self):
        assert self.remote_module._convert_args(('foo',)) == "'foo'"

    def test_more_than_one_argument(self):
        args = ('foo', 'bar', 1)
        assert self.remote_module._convert_args(args) == "'foo', 'bar', 1"

    def test_dictionary_as_argument(self):
        args = ({'some key': 1},)
        assert self.remote_module._convert_args(args) == "{'some key': 1}"


class TestLegacyModuleExecuteGetAttr(object):

    def setup(self):
        self.remote_module = backends.LegacyModuleExecute(FakeGateway(), None)

    def test_raise_attribute_error(self):
        with pytest.raises(AttributeError) as err:
            self.remote_module.foo()
        assert err.value.args[0] == 'module None does not have attribute foo'


class TestMakeConnectionString(object):

    def test_makes_sudo_python_no_ssh(self):
        conn = backends.BaseConnection('localhost', sudo=True, eager=False, interpreter='python')
        conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: False)
        assert conn_string == 'popen//python=sudo python'

    def test_makes_sudo_python_with_ssh(self):
        conn = backends.BaseConnection('localhost', sudo=True, eager=False, interpreter='python')
        conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: True)
        assert conn_string == 'ssh=localhost//python=sudo python'

    def test_makes_sudo_python_with_ssh_options(self):
        conn = backends.BaseConnection(
            'localhost', sudo=True, eager=False,
            interpreter='python', ssh_options='-F vagrant_ssh_config')
        conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: True)
        assert conn_string == 'ssh=-F vagrant_ssh_config localhost//python=sudo python'

    def test_makes_python_no_ssh(self):
        conn = backends.BaseConnection('localhost', sudo=False, eager=False, interpreter='python')
        conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: False)
        assert conn_string == 'popen//python=python'

    def test_makes_python_with_ssh(self):
        conn = backends.BaseConnection('localhost', sudo=False, eager=False, interpreter='python')
        conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: True)
        assert conn_string == 'ssh=localhost//python=python'

    def test_makes_sudo_python_with_forced_sudo(self):
        conn = backends.BaseConnection('localhost', sudo=True, eager=False, interpreter='python')
        conn_string = conn._make_connection_string(
            'localhost', _needs_ssh=lambda x: False, use_sudo=True
        )
        assert conn_string == 'popen//python=sudo python'

    def test_does_not_make_sudo_python_with_forced_sudo(self):
        conn = backends.BaseConnection('localhost', sudo=True, eager=False, interpreter='python')
        conn_string = conn._make_connection_string(
            'localhost', _needs_ssh=lambda x: False, use_sudo=False
        )
        assert conn_string == 'popen//python=python'

    def test_detects_python3(self):
        with patch.object(sys, 'version_info', (3, 5, 1)):
            conn = backends.BaseConnection('localhost', sudo=True, eager=False)
            conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: False)
            assert conn_string == 'popen//python=sudo python3'

    def test_detects_python2(self):
        with patch.object(sys, 'version_info', (2, 7, 11)):
            conn = backends.BaseConnection('localhost', sudo=False, eager=False)
            conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: True)
            assert conn_string == 'ssh=localhost//python=python2'


class TestDetectSudo(object):

    def setup(self):
        self.execnet = Mock()
        self.execnet.return_value = self.execnet
        self.execnet.makegateway.return_value = self.execnet
        self.execnet.remote_exec.return_value = self.execnet

    def test_does_not_need_sudo(self):
        self.execnet.receive.return_value = 'root'
        conn = backends.BaseConnection('localhost', sudo=True, eager=False)
        assert conn._detect_sudo(_execnet=self.execnet) is False

    def test_does_need_sudo(self):
        self.execnet.receive.return_value = 'alfredo'
        conn = backends.BaseConnection('localhost', sudo=True, eager=False)
        assert conn._detect_sudo(_execnet=self.execnet) is True
