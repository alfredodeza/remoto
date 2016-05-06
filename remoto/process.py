import traceback
from .log import reporting
from .util import admin_command, RemoteError


def _remote_run(channel, cmd, **kw):
    import subprocess
    import sys
    from select import select
    stop_on_nonzero = kw.pop('stop_on_nonzero', True)

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True,
        **kw
    )

    while True:
        reads, _, _ = select(
            [process.stdout.fileno(), process.stderr.fileno()],
            [], []
        )

        for descriptor in reads:
            if descriptor == process.stdout.fileno():
                read = process.stdout.readline()
                if read:
                    channel.send({'debug': read})
                    sys.stdout.flush()

            if descriptor == process.stderr.fileno():
                read = process.stderr.readline()
                if read:
                    channel.send({'warning': read})
                    sys.stderr.flush()

        if process.poll() is not None:
            # ensure we do not have anything pending in stdout or stderr
            # unfortunately, we cannot abstract this repetitive loop into its
            # own function because execnet does not allow for non-global (or
            # even nested functions). This must be repeated here.
            while True:
                err_read = out_read = None
                for descriptor in reads:
                    if descriptor == process.stdout.fileno():
                        out_read = process.stdout.readline()
                        if out_read:
                            channel.send({'debug': out_read})
                            sys.stdout.flush()

                    if descriptor == process.stderr.fileno():
                        err_read = process.stderr.readline()
                        if err_read:
                            channel.send({'warning': err_read})
                            sys.stderr.flush()
                # At this point we have gone through all the possible
                # descriptors and `read` was empty, so we now can break out of
                # this since all stdout/stderr has been properly flushed to
                # logging
                if not err_read and not out_read:
                    break

            break

    returncode = process.wait()
    if returncode != 0:
        if stop_on_nonzero:
            raise RuntimeError(
                "command returned non-zero exit status: %s" % returncode
            )
        else:
            channel.send({'warning': "command returned non-zero exit status: %s" % returncode})


def extend_path(conn, arguments):
    """
    get the remote environment's env so we can explicitly add the path without
    wiping out everything
    """
    # retrieve the remote environment variables for the host
    try:
        result = conn.gateway.remote_exec("import os; channel.send(os.environ.copy())")
        env = result.receive()
    except Exception:
        conn.logger.exception('failed to retrieve the remote environment variables')
        env = {}

    # get the $PATH and extend it (do not overwrite)
    path = env.get('PATH', '')
    env['PATH'] = path + '/usr/local/bin:/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/sbin'
    arguments['env'] = env

    return arguments


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
    if not kw.get('env'):
        # get the remote environment's env so we can explicitly add
        # the path without wiping out everything
        kw = extend_path(conn, kw)

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
    stdout = process.stdout.read().splitlines()
    stderr = process.stderr.read().splitlines()
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
    if not kw.get('env'):
        # get the remote environment's env so we can explicitly add
        # the path without wiping out everything
        kw = extend_path(conn, kw)

    conn.logger.info('Running command: %s' % ' '.join(admin_command(conn.sudo, command)))
    result = conn.execute(_remote_check, cmd=command, **kw)
    response = None
    try:
        response = result.receive(timeout)
    except Exception as err:
        # the things we need to do here :(
        # because execnet magic, we cannot catch this as
        # `except TimeoutError`
        if err.__class__.__name__ == 'TimeoutError':
            msg = 'No data was received after %s seconds, disconnecting...' % timeout
            conn.logger.warning(msg)
            # there is no stdout, stderr, or exit code but make the exit code
            # an error condition (non-zero) regardless
            return [], [], -1
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
    return response

