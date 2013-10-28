

def reporting(conn, result, timeout=None):
    timeout = timeout or conn.global_timeout # -1 a.k.a. wait for ever
    log_map = {
        'debug': conn.logger.debug,
        'error': conn.logger.error,
        'warning': conn.logger.warning
    }

    while True:
        try:
            received = result.receive(timeout)
            level_received, message = list(received.items())[0]
            log_map[level_received](message.strip('\n'))
        except EOFError:
            break
        except Exception as err:
            # the things we need to do here :(
            # because execnet magic, we cannot catch this as
            # `except TimeoutError`
            if err.__class__.__name__ == 'TimeoutError':
                msg = 'No data was received after %s seconds, disconnecting...' % timeout
                conn.logger.warning(msg)
                break
            raise
