advanced (multi) channel communication
=====================================================

MultiChannel: container for multiple channels
------------------------------------------------------

Use ``execnet.MultiChannel`` to work with multiple channels::

    >>> import execnet
    >>> ch1 = execnet.makegateway().remote_exec("channel.send(1)")
    >>> ch2 = execnet.makegateway().remote_exec("channel.send(2)")
    >>> mch = execnet.MultiChannel([ch1, ch2])
    >>> len(mch)
    2
    >>> mch[0] is ch1 and mch[1] is ch2
    True
    >>> ch1 in mch and ch2 in mch
    True
    >>> sum(mch.receive_each())
    3

receive results from sub processes with a Queue
-----------------------------------------------------

Use ``MultiChannel.make_receive_queue()`` to get a queue
from which to obtain results::

    >>> ch1 = execnet.makegateway().remote_exec("channel.send(1)")
    >>> ch2 = execnet.makegateway().remote_exec("channel.send(2)")
    >>> mch = execnet.MultiChannel([ch1, ch2])
    >>> queue = mch.make_receive_queue()
    >>> chan1, res1 = queue.get()
    >>> chan2, res2 = queue.get(timeout=3)
    >>> res1 + res2
    3

Working asynchronously/event-based with channels
---------------------------------------------------

Use channel callbacks if you want to process incoming
data immediately and without blocking execution::

    >>> import execnet
    >>> gw = execnet.makegateway()
    >>> ch = gw.remote_exec("channel.receive() ; channel.send(42)")
    >>> l = []
    >>> ch.setcallback(l.append)
    >>> ch.send(1)
    >>> ch.waitclose()
    >>> assert l == [42]

Note that the callback function will be executed in the
receiver thread and should not block or run for too long.

robustly receive results and termination notification
-----------------------------------------------------

Use ``MultiChannel.make_receive_queue(endmarker)`` to specify
an object to be put to the queue when the remote side of a channel
is closed.  The endmarker will also be put to the Queue if the gateway
is blocked in execution and is terminated/killed::

    >>> group = execnet.Group(['popen'] * 3) # create three gateways
    >>> mch = group.remote_exec("channel.send(channel.receive()+1)")
    >>> queue = mch.make_receive_queue(endmarker=42)
    >>> mch[0].send(1)
    >>> chan1, res1 = queue.get()
    >>> res1
    2
    >>> group.terminate(timeout=1) # kill processes waiting on receive
    >>> for i in range(3):
    ...    chan1, res1 = queue.get()
    ...    assert res1 == 42
    >>> group
    <Group []>



saturate multiple Hosts and CPUs with tasks to process
--------------------------------------------------------

If you have multiple CPUs or hosts you can create as many
gateways and then have a process sit on each CPU and wait
for a task to proceed.  One complication is that we 
want to ensure clean termination of all processes 
and loose no result.  Here is an example that just uses
local subprocesses and does the task:

.. include:: taskserver.py
    :literal:

