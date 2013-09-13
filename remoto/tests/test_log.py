from pytest import raises
from remoto import log
from remoto.exc import TimeoutError
from mock import Mock


class TestReporting(object):

    def test_reporting_when_channel_is_empty(self):
        conn = Mock()
        result = Mock()
        result.receive.side_effect = EOFError
        log.reporting(conn, result)

    def test_write_debug_statements(self):
        conn = Mock()
        result = Mock()
        result.receive.side_effect = [{'debug': 'a debug message'}, EOFError]
        log.reporting(conn, result)
        assert conn.logger.debug.called is True
        assert conn.logger.info.called is False

    def test_write_info_statements(self):
        conn = Mock()
        result = Mock()
        result.receive.side_effect = [{'error': 'an error message'}, EOFError]
        log.reporting(conn, result)
        assert conn.logger.debug.called is False
        assert conn.logger.error.called is True

    def test_strip_new_lines(self):
        conn = Mock()
        result = Mock()
        result.receive.side_effect = [{'error': 'an error message\n\n'}, EOFError]
        log.reporting(conn, result)
        message = conn.logger.error.call_args[0][0]
        assert message == 'an error message'

    def test_timeout_error(self):
        conn = Mock()
        result = Mock()
        result.receive.side_effect = TimeoutError
        log.reporting(conn, result)
        message = conn.logger.warning.call_args[0][0]
        assert 'No data was received after ' in message

    def test_raises_other_errors(self):
        conn = Mock()
        result = Mock()
        result.receive.side_effect = OSError
        with raises(OSError):
            log.reporting(conn, result)
