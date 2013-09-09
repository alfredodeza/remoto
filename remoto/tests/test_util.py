from remoto import util


class TestAdminCommand(object):

    def test_prepend_list_if_sudo(self):
        result = util.admin_command(True, ['ls'])
        assert result == ['sudo', 'ls']

    def test_skip_prepend_if_not_sudo(self):
        result = util.admin_command(False, ['ls'])
        assert result == ['ls']
