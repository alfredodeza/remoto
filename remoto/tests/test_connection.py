from remoto import connection


class FakeSocket(object):

    def __init__(self, gethostname):
        self.gethostname = lambda: gethostname


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


class FakeGateway(object):

    def remote_exec(self, module):
        pass


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

    def test_more_than_one_argument(self):
        assert self.remote_module._convert_args(('foo', 'bar', 1)) == "'foo', 'bar', 1"

    def test_more_than_one_argument(self):
        assert self.remote_module._convert_args(('foo', 'bar', 1)) == "'foo', 'bar', 1"

    def test_more_than_one_argument(self):
        assert self.remote_module._convert_args(('foo', 'bar', 1)) == "'foo', 'bar', 1"

