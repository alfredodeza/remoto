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
