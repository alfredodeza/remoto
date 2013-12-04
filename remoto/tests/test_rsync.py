from mock import Mock, patch
from remoto import file_sync


class TestRsync(object):

    def make_fake_sync(self):
        fake_sync = Mock()
        fake_sync.return_value = fake_sync
        fake_sync.targets = []
        fake_sync.add_target = lambda gw, destination: fake_sync.targets.append(destination)
        return fake_sync

    @patch('remoto.file_sync.Connection', Mock())
    def test_rsync_fallback_to_host_list(self):
        fake_sync = self.make_fake_sync()
        with patch('remoto.file_sync._RSync', fake_sync):
            file_sync.rsync('host1', '/source', '/destination')

        # should've added just one target
        assert len(fake_sync.targets) == 1

    @patch('remoto.file_sync.Connection', Mock())
    def test_rsync_use_host_list(self):
        fake_sync = self.make_fake_sync()
        with patch('remoto.file_sync._RSync', fake_sync):
            file_sync.rsync(
                ['host1', 'host2'], '/source', '/destination')

        # should've added just one target
        assert len(fake_sync.targets) == 2
