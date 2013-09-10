

def reporting(conn, result):
    log_map = {'debug': conn.logger.debug, 'error': conn.logger.error}
    while True:
        try:
            received = result.receive()
            level_received, message = list(received.items())[0]
            log_map[level_received](message.strip('\n'))
        except EOFError:
            break
