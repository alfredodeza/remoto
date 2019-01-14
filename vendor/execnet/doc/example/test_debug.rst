
Debugging execnet / Wire messages
===============================================================

By setting the environment variable ``EXECNET_DEBUG`` you can
configure the execnet tracing mechanism:

:EXECNET_DEBUG=1:  write per-process trace-files to ``${TEMPROOT}/execnet-debug-PID``
:EXECNET_DEBUG=2:  perform tracing to stderr (popen-gateway slaves will send this to their instantiator)

Here is a simple example to see what goes on with a simple execution::

    EXECNET_DEBUG=2  # or "set EXECNET_DEBUG=2" on windows

    python -c 'import execnet ; execnet.makegateway().remote_exec("42")'

which will show PID-prefixed trace entries::

    [2326] gw0 starting to receive
    [2326] gw0 sent <Message.CHANNEL_EXEC channelid=1 '42'>
    [2327] creating slavegateway on <execnet.gateway_base.Popen2IO instance at 0x9f1c20c>
    [2327] gw0-slave starting to receive
    [2327] gw0-slave received <Message.CHANNEL_EXEC channelid=1 '42'>
    [2327] gw0-slave execution starts[1]: '42'
    [2327] gw0-slave execution finished
    [2327] gw0-slave sent <Message.CHANNEL_CLOSE channelid=1 ''>
    [2327] gw0-slave 1 sent channel close message
    [2326] gw0 received <Message.CHANNEL_CLOSE channelid=1 ''>
    [2326] gw0 1 channel.__del__
    [2326] === atexit cleanup <Group ['gw0']> ===
    [2326] gw0 gateway.exit() called
    [2326] gw0 --> sending GATEWAY_TERMINATE
    [2326] gw0 sent <Message.GATEWAY_TERMINATE channelid=0 ''>
    [2326] gw0 joining receiver thread
    [2327] gw0-slave received <Message.GATEWAY_TERMINATE channelid=0 ''>
    [2327] gw0-slave putting None to execqueue
    [2327] gw0-slave io.close_read()
    [2327] gw0-slave leaving <Thread(receiver, started daemon -1220277392)>
    [2327] gw0-slave 1 channel.__del__
    [2327] gw0-slave io.close_write()
    [2327] gw0-slave slavegateway.serve finished
    [2327] gw0-slave gateway.join() called while receiverthread already finished
    [2326] gw0 leaving <Thread(receiver, started daemon -1221223568)>
