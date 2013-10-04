remoto
======
A very simplistic remote-command-executor using ``ssh`` and Python in the
remote end.

All the heavy lifting is done by execnet, while this minimal API provides the
bare minimum to handle easy logging and connections from the remote end.

``remoto`` is a bit opinionated as it was conceived to replace helpers and
remote utilities for ``ceph-deploy`` a tool to run remote commands to configure
and setup the distributed file system Ceph.


Example Usage
-------------
The usage aims to be extremely straightforward, with a very minimal set of
helpers and utilities for remote processes and logging output.

The most basic example will use the ``run`` helper to execute a command on the
remote end. It does require a logging object, which needs to be one that, at
the very least, has both ``error`` and ``debug``. Those are called for
``stderr`` and ``stdout`` respectively.

This is how it would look with a basic logger passed in::

    >>> logger = logging.getLogger('hostname')
    >>> conn = remoto.Connection('hostname', logger=logger)
    >>> run(conn, ['ls', '-a'])
    2013-09-07 15:32:06,662 [hostname][DEBUG] .
    2013-09-07 15:32:06,662 [hostname][DEBUG] ..
    2013-09-07 15:32:06,662 [hostname][DEBUG] .bash_history
    2013-09-07 15:32:06,662 [hostname][DEBUG] .bash_logout
    2013-09-07 15:32:06,662 [hostname][DEBUG] .bashrc
    2013-09-07 15:32:06,662 [hostname][DEBUG] .cache
    2013-09-07 15:32:06,664 [hostname][DEBUG] .profile
    2013-09-07 15:32:06,664 [hostname][DEBUG] .ssh

The ``run`` helper will display the ``stderr`` and ``stdout`` as ``ERROR`` and
``DEBUG`` respectively.

For other types of usage (like checking exit status codes, or raising upon
them) ``remoto`` does provide them too.


Remote Commands
===============

``process.run``
---------------
Calling remote commands can be done in a few different ways. The most simple
one is with ``process.run``::

    >>> from remoto.process import run
    >>> from remoto import Connection
    >>> logger = my_logging_setup('hostname')
    >>> conn = Connection('hostname')
    >>> run(conn, ['whoami'])
    2013-09-07 15:32:06,664 [hostname][DEBUG] root

Note however, that you are not capturing results or information from the remote
end. The intention here is only to be able to run a command and log its output.
It is a *fire and forget* call.


``process.check``
-----------------
This callable, allows the caller to deal with the ``stderr``, ``stdout`` and
exit code. It returns it in a 3 item tuple::

    >>> from remoto.process import check
    >>> check(conn, ['ls', '/nonexistent/path'])
    ([], ['ls: cannot access /nonexistent/path: No such file or directory'], 2)

Note that the ``stdout`` and ``stderr`` items are returned as lists with the ``\n``
characters removed.

This is useful if you need to process the information back locally, as opposed
to just firing and forgetting (while logging, like ``process.run``).


Remote Functions
================

To execute remote functions (ideally) you would need to define them in a module
and add the following to the end of that module::

    if __name__ == '__channelexec__':
        for item in channel:
            channel.send(eval(item))


If you had a function in a module named ``foo`` that looks like this::

    import os

    def listdir(path):
        return os.listdir(path)

To be able to execute that ``listdir`` function remotely you would need to pass
the module to the connection object and then call that function::

    >>> import foo
    >>> conn = Connection('hostname')
    >>> remote_foo = conn.import_module(foo)
    >>> remote_foo.listdir('.')
    ['.bash_logout',
     '.profile',
     '.veewee_version',
     '.lesshst',
     'python',
     '.vbox_version',
     'ceph',
     '.cache',
     '.ssh']

Note that functions to be executed remotely **cannot** accept objects as
arguments, just normal Python data structures, like tuples, lists and
dictionaries. Also safe to use are ints and strings.

