remoto
======
A very simplistic remote-command-executor using connections to hosts (``ssh``,
local, containers, and several others are supported) and Python in the remote
end.

All the heavy lifting is done by execnet, while this minimal API provides the
bare minimum to handle easy logging and connections from the remote end.

``remoto`` is a bit opinionated as it was conceived to replace helpers and
remote utilities for ``ceph-deploy``, a tool to run remote commands to configure
and setup the distributed file system Ceph. `ceph-medic
<https://pypi.org/project/ceph-medic/>`_ uses remoto as well to inspect Ceph
clusters.


Example Usage
-------------
The usage aims to be extremely straightforward, with a very minimal set of
helpers and utilities for remote processes and logging output.

The most basic example will use the ``run`` helper to execute a command on the
remote end. It does require a logging object, which needs to be one that, at
the very least, has both ``error`` and ``debug``. Those are called for
``stderr`` and ``stdout`` respectively.

This is how it would look with a basic logger passed in::

    >>> conn = remoto.Connection('hostname')
    >>> run(conn, ['ls', '-a'])
    INFO:hostname:Running command: ls -a
    DEBUG:hostname:.
    DEBUG:hostname:..
    DEBUG:hostname:.bash_history
    DEBUG:hostname:.bash_logout
    DEBUG:hostname:.bash_profile
    DEBUG:hostname:.bashrc
    DEBUG:hostname:.lesshst
    DEBUG:hostname:.pki
    DEBUG:hostname:.ssh
    DEBUG:hostname:.vim
    DEBUG:hostname:.viminfo

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
    >>> from remoto import connection
    >>> Connection = connection.get('ssh')
    >>> conn = Connection('myhost')
    >>> run(conn, ['whoami'])
    INFO:myhost:Running command: whoami
    DEBUG:myhost:root

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
There are two supported ways to execute functions on the remote side. The
library that ``remoto`` uses to connect (``execnet``) only supports a few
backends *natively*, and ``remoto`` has extended this ability for other backend
connections like kubernetes.

The remote function capabilities are provided by ``LegacyModuleExecute`` and
``JsonModuleExecute``. By default, both ``ssh`` and ``local`` connection will
use the legacy execution class, and everything else will use the ``legacy``
class. The ``ssh`` and ``local`` connections can still be forced to use the new
module execution by setting::

    conn.remote_import_system = 'json'


``json``
--------
The default module for ``docker``, ``kubernetes``, ``podman``, and
``openshift``. It does not require any magic on the module to be executed,
however it is worth noting that the library *will* add the following bit of
magic when sending the module to the remote end for execution::


    if __name__ == '__main__':
        import json, traceback
        obj = {'return': None, 'exception': None}
        try:
            obj['return'] = function_name(*a)
        except Exception:
            obj['exception'] = traceback.format_exc()
        try:
            print(json.dumps(obj).decode('utf-8'))
        except AttributeError:
            print(json.dumps(obj))

This allows the system to execute ``function_name`` (replaced by the real
function to be executed with its arguments), grab any results, serialize them
with ``json`` and send them back for local processing.


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


``legacy``
----------
When using the ``legacy`` execution model (the default for ``local`` and
``ssh`` connections), modules are required to add the following to the end of
that module::

    if __name__ == '__channelexec__':
        for item in channel:
            channel.send(eval(item))

This piece of code is fully compatible with the ``json`` execution model, and
would not cause conflicts.


Automatic detection for ssh connections
---------------------------------------
There is automatic detection for the need to connect remotely (via SSH) or not
that it is infered by the hostname of the current host (vs. the host that is
connecting to).

If the local host has the same as the remote hostname, a local connection (via
`Popen`) will be opened and that will be used instead of `ssh`, and avoiding
the issues of being able to ssh into the same host.

Automatic detection for using `sudo`
------------------------------------
This magical detection can be enabled by using the `detect_sudo` flag in the
`Connection` class. It is disabled by default.

When enabled, it will prefix any command with `sudo`. This is useful for
libraries that need super user permissions and want to avoid passing `sudo`
everywhere, which can be non-trivial if dealing with `root` users that are
connecting via SSH.
