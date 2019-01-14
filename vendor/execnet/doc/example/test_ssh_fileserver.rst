
Receive file contents from remote SSH account
-----------------------------------------------------

Here is some small server code that you can use to retrieve
contents of remote files:

.. include:: servefiles.py
    :literal:

And here is some code to use it to retrieve remote contents::

    import execnet
    import servefiles
    gw = execnet.makegateway("ssh=codespeak.net")
    channel = gw.remote_exec(servefiles)

    for fn in ('/etc/passwd', '/etc/group'):
        channel.send(fn)
        content = channel.receive()
        print(fn)
        print(content)
