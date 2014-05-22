import traceback
from .log import reporting
from .util import admin_command, RemoteError


def _remote_run(channel, cmd, **kw):
    import subprocess
    import sys
    stop_on_nonzero = kw.pop('stop_on_nonzero', True)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
        **kw
    )

    if process.stdout:
        while True:
            out = process.stdout.readline()
            if out == '' and process.poll() is not None:
                break
            if out != '':
                channel.send({'debug': out})
                sys.stdout.flush()

    if process.stderr:
        while True:
            err = process.stderr.readline()
            if err == '' and process.poll() is not None:
                break
            if err != '':
                channel.send({'warning': err})
                sys.stderr.flush()

    returncode = process.wait()
    if returncode != 0:
        if stop_on_nonzero:
            raise RuntimeError("command returned non-zero exit status: %s" % returncode)
        else:
            channel.send({'warning': "command returned non-zero exit status: %s" % returncode})


def run(conn, command, exit=False, timeout=None, **kw):
    """
    A real-time-logging implementation of a remote subprocess.Popen call where
    a command is just executed on the remote end and no other handling is done.

    :param conn: A connection oject
    :param command: The command to pass in to the remote subprocess.Popen
    :param exit: If this call should close the connection at the end
    :param timeout: How many seconds to wait after no remote data is received
                    (defaults to wait for ever)
    """
    stop_on_error = kw.pop('stop_on_error', True)
    kw.setdefault(
        'env',
        {
            'PATH':
            '/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin'
        }
    )
    timeout = timeout or conn.global_timeout
    conn.logger.info('Running command: %s' % ' '.join(admin_command(conn.sudo, command)))
    result = conn.execute(_remote_run, cmd=command, **kw)
    try:
        reporting(conn, result, timeout)
    except Exception:
        remote_trace = traceback.format_exc()
        remote_error = RemoteError(remote_trace)
        if remote_error.exception_name == 'RuntimeError':
            conn.logger.error(remote_error.exception_line)
        else:
            for tb_line in remote_trace.split('\n'):
                conn.logger.error(tb_line)
        if stop_on_error:
            raise RuntimeError(
                'Failed to execute command: %s' % ' '.join(command)
            )
    if exit:
        conn.exit()


def _remote_check(channel, cmd, **kw):
    import subprocess

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kw
    )
    stdout = [line.strip('\n') for line in process.stdout.readlines()]
    stderr = [line.strip('\n') for line in process.stderr.readlines()]
    channel.send((stdout, stderr, process.wait()))


def check(conn, command, exit=False, timeout=None, **kw):
    """
    Execute a remote command with ``subprocess.Popen`` but report back the
    results in a tuple with three items: stdout, stderr, and exit status.

    This helper function *does not* provide any logging as it is the caller's
    responsibility to do so.
    """
    stop_on_error = kw.pop('stop_on_error', True)
    timeout = timeout or conn.global_timeout
    kw.setdefault(
        'env',
        {
            'PATH':
            '/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin'
        }
    )
    conn.logger.info('Running command: %s' % ' '.join(admin_command(conn.sudo, command)))
    result = conn.execute(_remote_check, cmd=command, **kw)
    try:
        return result.receive(timeout)
    except Exception as err:
        # the things we need to do here :(
        # because execnet magic, we cannot catch this as
        # `except TimeoutError`
        if err.__class__.__name__ == 'TimeoutError':
            msg = 'No data was received after %s seconds, disconnecting...' % timeout
            conn.logger.warning(msg)
            return
        else:
            remote_trace = traceback.format_exc()
            remote_error = RemoteError(remote_trace)
            if remote_error.exception_name == 'RuntimeError':
                conn.logger.error(remote_error.exception_line)
            else:
                for tb_line in remote_trace.split('\n'):
                    conn.logger.error(tb_line)
            if stop_on_error:
                raise RuntimeError(
                    'Failed to execute command: %s' % ' '.join(command)
                )
    if exit:
        conn.exit()
