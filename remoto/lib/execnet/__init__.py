"""
execnet: pure python lib for connecting to local and remote Python Interpreters.

(c) 2012, Holger Krekel and others
"""
__version__ = '1.1.1-ad4'

from . import apipkg

apipkg.initpkg(__name__, {
    'PopenGateway':     '.deprecated:PopenGateway',
    'SocketGateway':    '.deprecated:SocketGateway',
    'SshGateway':       '.deprecated:SshGateway',
    'makegateway':      '.multi:makegateway',
    'HostNotFound':     '.gateway_bootstrap:HostNotFound',
    'RemoteError':      '.gateway_base:RemoteError',
    'TimeoutError':     '.gateway_base:TimeoutError',
    'XSpec':            '.xspec:XSpec',
    'Group':            '.multi:Group',
    'MultiChannel':     '.multi:MultiChannel',
    'RSync':            '.rsync:RSync',
    'default_group':    '.multi:default_group',
    'dumps':            '.gateway_base:dumps',
    'loads':            '.gateway_base:loads',
    'load':             '.gateway_base:load',
    'dump':             '.gateway_base:dump',
    'DataFormatError':  '.gateway_base:DataFormatError',
})

# CHANGELOG
#
# 1.1.1-ad4: Use the newest execnet, includes SSH options
#
# 1.1-ad3: Catch more `TypeError` if the connection is closing but the channel attempts
# to write. We now check is `struct.pack` is not None to proceed.
# Issue: https://bitbucket.org/hpk42/execnet/issue/22/structpack-can-be-none-sometimes-spits
#
# 1.1-ad2: Allow for `sudo python` on local popen gateways
# Issue: https://bitbucket.org/hpk42/execnet/issue/21/support-sudo-on-local-popen
#
# 1.1-ad1: `if case` to check if `Message` is None and avoid AttributeErrors
# Issue: https://bitbucket.org/hpk42/execnet/issue/20/attributeerror-nonetype-object-has-no
