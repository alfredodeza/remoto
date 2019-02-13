"""
this is just a stub module to use to test the `import_module` functionality in
remoto
"""
import sys


def function(conn):
    return True


def fails():
    raise Exception('failure from fails() function')


def unexpected_fail():
    sys.exit(1)


def noop():
    sys.exit(0)


def passes():
    pass
