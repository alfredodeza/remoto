from mock import Mock
from remoto import process


class TestExtendPath(object):

    def setup(self):
        self.path = '/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin'

    def test_no_environment_sets_path(self):
        fake_conn = Mock()
        fake_conn.gateway.remote_exec.return_value = fake_conn
        fake_conn.receive.return_value = {}
        result = process.extend_env(fake_conn, {})
        assert result['env']['PATH'] == self.path

    def test_custom_path_does_not_get_overridden(self):
        fake_conn = Mock()
        fake_conn.gateway.remote_exec.return_value = fake_conn
        fake_conn.receive.return_value = {'PATH': '/home/alfredo/bin'}
        result = process.extend_env(fake_conn, {})
        new_path = result['env']['PATH']
        assert new_path.endswith(self.path)
        assert '/home/alfredo/bin' in new_path

    def test_custom_env_var_extends_existing_env(self):
        fake_conn = Mock()
        fake_conn.gateway.remote_exec.return_value = fake_conn
        fake_conn.receive.return_value = {'PATH': '/home/alfredo/bin'}
        result = process.extend_env(fake_conn, {'extend_env': {'CEPH_VOLUME_DEBUG': '1'}})
        new_path = result['env']['PATH']
        assert result['env']['PATH'].endswith(self.path)
        assert result['env']['CEPH_VOLUME_DEBUG'] == '1'

    def test_extend_env_gets_removed(self):
        fake_conn = Mock()
        fake_conn.gateway.remote_exec.return_value = fake_conn
        fake_conn.receive.return_value = {'PATH': '/home/alfredo/bin'}
        result = process.extend_env(fake_conn, {'extend_env': {'CEPH_VOLUME_DEBUG': '1'}})
        assert result.get('extend_env') is None
