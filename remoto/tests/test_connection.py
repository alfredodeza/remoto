from mock import Mock
from py.test import raises
from remoto import connection
import fake_module


class FakeSocket(object):

    def __init__(self, gethostname, getfqdn=None):
        self.gethostname = lambda: gethostname
        self.getfqdn = lambda: getfqdn or gethostname


class TestNeedsSsh(object):

    def test_short_hostname_matches(self):
        socket = FakeSocket('foo.example.org')
        assert connection.needs_ssh('foo', socket) is False

    def test_long_hostname_matches(self):
        socket = FakeSocket('foo.example.org')
        assert connection.needs_ssh('foo.example.org', socket) is False

    def test_hostname_does_not_match(self):
        socket = FakeSocket('foo')
        assert connection.needs_ssh('meh', socket) is True

    def test_fqdn_hostname_matches_short_hostname(self):
        socket = FakeSocket('foo', getfqdn='foo.example.org')
        assert connection.needs_ssh('foo.example.org', socket) is False


class FakeGateway(object):

    def remote_exec(self, module):
        pass


class TestRemoteModule(object):

    def setup(self):
        self.conn = connection.Connection('localhost', sudo=True, eager=False)
        self.conn.gateway = FakeGateway()

    def test_importing_it_sets_it_as_remote_module(self):
        self.conn.import_module(fake_module)
        assert fake_module == self.conn.remote_module.module

    def test_importing_it_returns_the_module_too(self):
        remote_foo = self.conn.import_module(fake_module)
        assert remote_foo.module == fake_module


class TestModuleExecuteArgs(object):

    def setup(self):
        self.remote_module = connection.ModuleExecute(FakeGateway(), None)

    def test_single_argument(self):
        assert self.remote_module._convert_args(('foo',)) == "'foo'"

    def test_more_than_one_argument(self):
        args = ('foo', 'bar', 1)
        assert self.remote_module._convert_args(args) == "'foo', 'bar', 1"

    def test_dictionary_as_argument(self):
        args = ({'some key': 1},)
        assert self.remote_module._convert_args(args) == "{'some key': 1}"


class TestModuleExecuteGetAttr(object):

    def setup(self):
        self.remote_module = connection.ModuleExecute(FakeGateway(), None)

    def test_raise_attribute_error(self):
        with raises(AttributeError) as err:
            self.remote_module.foo()
        assert err.value.args[0] == 'module None does not have attribute foo'


class TestMakeConnectionString(object):

    def test_makes_sudo_python_no_ssh(self):
        conn = connection.Connection('localhost', sudo=True, eager=False)
        conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: False)
        assert conn_string == 'popen//python=sudo python'

    def test_makes_sudo_python_with_ssh(self):
        conn = connection.Connection('localhost', sudo=True, eager=False)
        conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: True)
        assert conn_string == 'ssh=localhost//python=sudo python'

    def test_makes_python_no_ssh(self):
        conn = connection.Connection('localhost', sudo=False, eager=False)
        conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: False)
        assert conn_string == 'popen//python=python'

    def test_makes_python_with_ssh(self):
        conn = connection.Connection('localhost', sudo=False, eager=False)
        conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: True)
        assert conn_string == 'ssh=localhost//python=python'

    def test_makes_sudo_python_with_forced_sudo(self):
        conn = connection.Connection('localhost', sudo=True, eager=False)
        conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: False, use_sudo=True)
        assert conn_string == 'popen//python=sudo python'

    def test_does_not_make_sudo_python_with_forced_sudo(self):
        conn = connection.Connection('localhost', sudo=True, eager=False)
        conn_string = conn._make_connection_string('localhost', _needs_ssh=lambda x: False, use_sudo=False)
        assert conn_string == 'popen//python=python'


class TestDetectSudo(object):

    def setup(self):
        self.execnet = Mock()
        self.execnet.return_value = self.execnet
        self.execnet.makegateway.return_value = self.execnet
        self.execnet.remote_exec.return_value = self.execnet

    def test_does_not_need_sudo(self):
        self.execnet.receive.return_value = 'root'
        conn = connection.Connection('localhost', sudo=True, eager=False)
        assert conn._detect_sudo(_execnet=self.execnet) is False

    def test_does_need_sudo(self):
        self.execnet.receive.return_value = 'alfredo'
        conn = connection.Connection('localhost', sudo=True, eager=False)
        assert conn._detect_sudo(_execnet=self.execnet) is True
