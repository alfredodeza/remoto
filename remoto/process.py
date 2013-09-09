import sys
import execnet


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
    while True:
        try:
            log_map = {'debug': conn.logger.debug, 'error': conn.logger.error}
            received = result.receive()
            level_received, message = received.items()[0]
            log_map[level_received](message.strip('\n'))
        except EOFError:
            break
    conn.exit()
