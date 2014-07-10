import subprocess
import os
from os import path
import re
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

    if result.wait():
        print_error(result.stdout.readlines(), result.stderr.readlines())


def print_error(stdout, stderr):
    sys.stderr.write('*\n'*80)
    sys.stderr.write(str(error_msg)+'\n')
    for line in stdout:
        sys.stderr.write(str(line)+'\n')
    for line in stderr:
        sys.stderr.write(str(line)+'\n')
    sys.stderr.write('*'*80+'\n')


def vendor_library(name, version, git_repo):
    this_dir = path.dirname(path.abspath(__file__))
    vendor_dest = path.join(this_dir, 'remoto/lib/vendor/%s' % name)
    vendor_init = path.join(vendor_dest, '__init__.py')
    vendor_src = path.join(this_dir, name)
    vendor_module = path.join(vendor_src, name)
    current_dir = os.getcwd()

    if path.exists(vendor_src):
        run(['rm', '-rf', vendor_src])

    if path.exists(vendor_init):
        module_file = open(vendor_init).read()
        metadata = dict(re.findall(r"__([a-z]+)__\s*=\s*['\"]([^'\"]*)['\"]", module_file))
        if metadata.get('version') != version:
            run(['rm', '-rf', vendor_dest])

    if not path.exists(vendor_dest):
        run(['git', 'clone', git_repo])
        os.chdir(vendor_src)
        run(['git', 'checkout', version])
        run(['mv', vendor_module, vendor_dest])
    os.chdir(current_dir)


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
    version.

    For example, a library ``foo`` with version ``0.0.1`` would look like::

        vendor_requirements = [
            ('foo', '0.0.1', 'https://example.com/git_repo'),
        ]
    """

    for library in vendor_requirements:
        name, version, repo = library
        vendor_library(name, version, repo)


if __name__ == '__main__':
    # XXX define this in one place, so that we avoid making updates
    # in two places
    vendor_requirements = [
        ('execnet', '1.2post2', 'https://github.com/alfredodeza/execnet'),
    ]
    vendorize(vendor_requirements)

