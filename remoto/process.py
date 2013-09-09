from .log import reporting
from .util import admin_command


def _remote_run(channel, cmd):
    import subprocess
    import sys

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if process.stderr:
        while True:
            err = process.stderr.readline()
            if err == '' and process.poll() != None:
                break
            if err != '':
                channel.send({'error':err})
                sys.stderr.flush()
    if process.stdout:
        while True:
            out = process.stdout.readline()
            if out == '' and process.poll() != None:
                break
            if out != '':
                channel.send({'debug':out})
                sys.stdout.flush()


def run(conn, command, exit=False):
    """
    A real-time-logging implementation of a remote subprocess.Popen call where
    a command is just executed on the remote end and no other handling is done.
    """
    command = admin_command(conn.sudo, command)
    conn.logger.info('Running command: %s' % ' '.join(command))
    result = conn.execute(_remote_run, cmd=command)
    reporting(conn, result)
    if exit:
        conn.exit()


def _remote_check(channel, cmd):
    import subprocess

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stdout = [line.strip('\n') for line in process.stdout.readlines()]
    stderr = [line.strip('\n') for line in process.stderr.readlines()]
    channel.send((stdout, stderr, process.wait()))


def check(conn, command, exit=False):
    """
    Execute a remote command with ``subprocess.Popen`` but report back the
    results in a tuple with three items: stdout, stderr, and exit status.

    This helper function *does not* provide any logging as it is the caller's
    responsibility to do so.
    """
    command = admin_command(conn.sudo, command)
    conn.logger.info('Running command: %s' % ' '.join(command))
    result = conn.execute(_remote_check, cmd=command)
    return result.receive()
    if exit:
        conn.exit()
