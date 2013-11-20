from remoto import util


class TestAdminCommand(object):

    def test_prepend_list_if_sudo(self):
        result = util.admin_command(True, ['ls'])
        assert result == ['sudo', 'ls']

    def test_skip_prepend_if_not_sudo(self):
        result = util.admin_command(False, ['ls'])
        assert result == ['ls']

    def test_command_that_is_not_a_list(self):
        result = util.admin_command(True, 'ls')
        assert result == ['sudo', 'ls']


class TestRemoteError(object):

    def test_exception_name(self):
        traceback = ('\n').join([
            'Traceback (most recent call last):',
            '  File "<string>", line 1, in <module>',
            "NameError: name 'foo' is not defined"
        ])
        error = util.RemoteError(traceback)
        error.exception_name == 'NameError'
