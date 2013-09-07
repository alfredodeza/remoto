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


