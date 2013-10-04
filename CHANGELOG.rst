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
