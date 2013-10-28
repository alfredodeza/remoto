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
