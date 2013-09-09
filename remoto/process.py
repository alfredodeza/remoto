import sys
import execnet
from remoto.log import reporting


def remote_run(channel, cmd):
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


def run(conn, command):
    result = conn.execute(remote_run, cmd=command)
    reporting(conn, result)
    conn.exit()
