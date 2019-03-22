1.1.3
-----
22-Mar-2019

* No code changes - adding packaging files for Debian


1.1.2
-----
13-Mar-2019

* Try a few different executables (not only ``python``) to check for a working
  one, in order of preference, starting with ``python3`` and ultimately falling
  back to the connection interpreter


1.1.1
-----
13-Mar-2019

* Fix an issue with remote Python interpreters that might not be ``python``,
  like in distros that use ``python3`` or similar.


1.1.0
-----
26-Feb-2019

* Allow to specify ``--context`` to kubernetes connections
* When a remote exception happens using the ``JsonModuleExecute``, include both
  stderr and stdout.


1.0.0
-----
13-Feb-2019

* Create other connection backends aside from ssh and local: kubernetes,
  podman, docker, and openshift.
* Adds new remote function/module execution model for non-native (for execnet) backends, so that
  modules will work in backends like kubernetes.
* Create a helper (``remoto.connection.get()``) for retrieving connection
  backends based on strings
* Increase the test coverage.
* Allow using ``localhost``, ``127.0.0.1``, and ``127.0.1.1`` to detect local
  connections (before the full hostname was required, as returned by
  ``socket.gethostname()``)
* No longer require creating ``logging`` loggers to pass in to connection
  classes, it will create a basic one when undefined.


0.0.35
------
8-Jan-2019

* Fix the botched 0.0.34 version which had stale commits from 0.0.32 - No code
  changes.


0.0.34
------
12-Dec-2018

* Allow ``ssh_options`` to extend ssh flags in the ``Connection()`` object


0.0.33
------
17-Jul-2018

* ``extend_env`` needs to be removed from ``**kw`` **only** when present.


0.0.32
------
16-Jul-2018

* ``extend_env`` needs to be removed from ``**kw`` as it is being passed onto
  subprocess, which renders it invalid


0.0.31
------
10-Jul-2018

* Extend environment variables, do not overwrite


0.0.30
------
05-Jul-2016

* Fix test issue with py3
* Remove vendored execnet
* Include tests when building
* Strip carriage-returns from messages in logs

0.0.29
------
17-May-2016
* Catch possible errors when remotes are missing the right Python interpreter

0.0.28
------
11-May-2016
* Avoid needless list comprehension that caused issues with Python 3
* Do not bare return when clients expect a three item tuple always
* Fix an issue where ``process.check`` would need to raise exit but the
  response had an error.

22-Dec-2015
0.0.27
------
22-Dec-2015
* Fix a problem where stderr/stdout variables would be undefined on certain
  conditions when running a remote command.

0.0.26
------
15-Dec-2015
* Fix (issue 19) where stdout and stderr would be prematurely ended and not
  fully logged.

0.0.25
------
21-Apr-2015
* Fix (issue 15) where a child process could finish but output would not be
  flushed to stdout/stderr.

0.0.24
------
* Ship the ``LICENSE`` file and ``tests`` directory as part of the
  distribution.

0.0.23
------
* Output the exact same order of remote ``stdout`` and ``stderr``

0.0.22
------
* Create a better detection mechanism for remote ``sudo`` needs

0.0.21
------
* Do not override remote environment variables to set the ``$PATH``

0.0.20
------
* Fix unneeded ssh connection when using FQDN hosts

0.0.19
------
* Fix ``vendor.py`` to really include the proper tag for ``execnet``

0.0.18
------
* Use execnet 1.2post2 that fixes a problem with ``None`` globals (see issue
  #1)

0.0.17
------
* add some imports to init so that they are easier to use
* make vendor libraries optional

0.0.16
------
* spit stdout before stderr as errors should be read last

0.0.15
------
* eat typeerror when closing the connection (execnet)

0.0.14
------
* Use new execnet  1.2.0
* use new connection defaults for execent

0.0.13
------
* Add a ``sync`` function to be able to synchronize directories between hosts.

0.0.12
------
* Map ``stderr`` to ``WARNING`` log level
* Do not spit out ``remoto``'s own tracebacks when raising remote errors
  because some exception occurred just do it for non-remoto exceptions
* Use version 1.1.1 of execnet with patches.

0.0.11
------
* Catch more TypeError problems when closing the connections.

0.0.10
------
* Allow configuration to raise on non-zero exit status

0.0.9
-----
* If the exit status is non-zero on the remote end, raise an exception

0.0.8
-----
* Raise RuntimeError on remote exceptions so others can actually
  catch that.

0.0.7
-----
* Patches execnet to allow local popen with sudo python

0.0.6
-----
* Add a global timeout option
* All processes use PATH variables passed to Popen
* Do not mangle commands if they need sudo
* Allow sudo python

0.0.5
-----
* Allow more than one thread to be started in the connection
* log at debug level the name of the function to be remotely
  executed

0.0.4
-----
* Create a way to execute functions remotely

0.0.3
-----
* If the hostname passed in to the connection matches the local
  hostname, then do a local connection (not an ssh one)

0.0.2
-----
* Allow a context manager for running one-off commands with the connection
  object.
* ``process.run`` can now take in a timeout value so that it does not hang in
  remote processes
