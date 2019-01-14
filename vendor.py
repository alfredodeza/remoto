import subprocess
import os
from os import path
import traceback
import sys


error_msg = """
This library depends on sources fetched when packaging that failed to be
retrieved.

This means that it will *not* work as expected. Errors encountered:
"""


def run(cmd):
    sys.stdout.write('[vendoring] Running command: %s\n' % ' '.join(cmd))
    try:
        result = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE
        )
    except Exception:
        # if building with python2.5 this makes it compatible
        _, error, _ = sys.exc_info()
        print_error([], traceback.format_exc(error).split('\n'))
        raise SystemExit(1)

    err, out = result.communicate()
    if result.returncode:
        print_error(out.split('\n'), err.split('\n'))

    return result.returncode


def print_error(stdout, stderr):
    sys.stderr.write('*'*80+'\n')
    sys.stderr.write(str(error_msg)+'\n')
    for line in stdout:
        sys.stderr.write(str(line)+'\n')
    for line in stderr:
        sys.stderr.write(str(line)+'\n')
    sys.stderr.write('*'*80+'\n')


def vendor_library(source, destination):
    this_dir = path.dirname(path.abspath(__file__))
    vendor_dir = os.path.join(this_dir, 'vendor')
    vendor_source_path = os.path.join(vendor_dir, source)
    if destination is None:
        vendor_destination = path.join(this_dir, 'remoto/lib/vendor/')
    else:
        vendor_destination = path.join(this_dir, 'remoto/lib/vendor/%s' % destination)
    vendor_source = path.join(vendor_dir, source)

    #if os.path.isfile(vendor_source_path):
    #    vendor_destination = path.join(this_dir, 'remoto/lib/vendor/')
    #    vendor_destination = 'remoto/lib/vendor/'
    #if not path.exists(vendor_destination):
    run(['cp', '-r', vendor_source, vendor_destination])


def clean_vendor(name):
    """
    Ensure that vendored code/dirs are removed, possibly when packaging when
    the environment flag is set to avoid vendoring.
    """
    this_dir = path.dirname(path.abspath(__file__))
    vendor_dest = path.join(this_dir, 'remoto/lib/vendor/%s' % name)
    run(['rm', '-rf', vendor_dest])


def vendorize(vendor_requirements):
    """
    This is the main entry point for vendorizing requirements. It expects
    a list of tuples that should contain the name of the library and the
    destination.

    For example, a library ``foo.py`` would look like::

        vendor_requirements = [
            ('foo.py')
        ]

    Optionally, the destination name can be altered::

        vendor_requirements = [
            ('foo/__init__.py', 'foo.py')
        ]

    All vendored libraries go into remoto/lib/vendor/
    """

    for library in vendor_requirements:
        try:
            source, destination = library
        except ValueError:
            source = library[0]
            destination = None
        vendor_library(source, destination)
