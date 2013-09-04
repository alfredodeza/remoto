remoto
======
A very simplistic remote-command-executor using ``ssh`` and Python in the
remote end.

All the heavy lifting is done by execnet, while this minimal API provides the
bare minimum to handle easy logging and connections from the remote end.

``remoto`` is a bit opinionated as it was conceived to replace helpers and
remote utilities for ``ceph-deploy`` a tool to run remote commands to configure
and setup the distributed file system Ceph.
