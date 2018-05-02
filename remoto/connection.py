import socket
import sys
import execnet


#
# Connection Object
#

class Connection(object):

    def __init__(self, hostname, logger=None, sudo=False, threads=1, eager=True,
                 detect_sudo=False, interpreter=None, continuous=False):
        self.sudo = sudo
        self.hostname = hostname
        self.logger = logger or FakeRemoteLogger()
        self.remote_module = None
        self.channel = None
        self.global_timeout = None  # wait for ever

        self.interpreter = interpreter or 'python%s' % sys.version_info[0]
        self.continuous = continuous

        if eager:
            try:
                if detect_sudo:
                    self.sudo = self._detect_sudo()
                self.gateway = self._make_gateway(hostname)
            except OSError:
                self.logger.error(
                    "Can't communicate with remote host, possibly because "
                    "%s is not installed there" % self.interpreter
                )
                raise

    def _make_gateway(self, hostname):
        gateway = execnet.makegateway(
            self._make_connection_string(hostname)
        )
        gateway.reconfigure(py2str_as_py3str=False, py3str_as_py2str=False)
        return gateway

    def _detect_sudo(self, _execnet=None):
        """
        ``sudo`` detection has to create a different connection to the remote
        host so that we can reliably ensure that ``getuser()`` will return the
        right information.

        After getting the user info it closes the connection and returns
        a boolean
        """
        exc = _execnet or execnet
        gw = exc.makegateway(
            self._make_connection_string(self.hostname, use_sudo=False)
        )

        channel = gw.remote_exec(
            'import getpass; channel.send(getpass.getuser())'
        )

        result = channel.receive()
        gw.exit()

        if result == 'root':
            return False
        self.logger.debug('connection detected need for sudo')
        return True

    def _make_connection_string(self, hostname, _needs_ssh=None, use_sudo=None):
        _needs_ssh = _needs_ssh or needs_ssh
        interpreter = self.interpreter
        if use_sudo is not None:
            if use_sudo:
                interpreter = 'sudo ' + interpreter
        elif self.sudo:
            interpreter = 'sudo ' + interpreter
        if _needs_ssh(hostname):
            return 'ssh=%s//python=%s' % (hostname, interpreter)
        return 'popen//python=%s' % interpreter

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit()
        return False

    def execute(self, function, **kw):
        return self.gateway.remote_exec(function, **kw)

    def exit(self):
        self.gateway.exit()

    def import_module(self, module):
        self.remote_module = ModuleExecute(self.gateway, module, self.logger, self.continuous)
        return self.remote_module


class ModuleExecute(object):

    def __init__(self, gateway, module, logger=None, continuous=False):
        self.channel = gateway.remote_exec(module)
        self.module = module
        self.logger = logger
        self.continuous = continuous

    def __getattr__(self, name):
        if not hasattr(self.module, name):
            msg = "module %s does not have attribute %s" % (str(self.module), name)
            raise AttributeError(msg)
        docstring = self._get_func_doc(getattr(self.module, name))

        def wrapper(*args):
            arguments = self._convert_args(args)
            if docstring:
                self.logger.debug(docstring)
            self.channel.send("%s(%s)" % (name, arguments))
            try:
                return self.channel.receive()
            except Exception as error:
                # Error will come as a string of a traceback, remove everything
                # up to the actual exception since we do get garbage otherwise
                # that points to non-existent lines in the compiled code
                exc_line = str(error)
                for tb_line in reversed(str(error).split('\n')):
                    if tb_line:
                        exc_line = tb_line
                        break
                raise RuntimeError(exc_line)

        def wrapper_continuous(*args):
            arguments = self._convert_args(args)
            if docstring:
                self.logger.debug(docstring)
            self.channel.send("%s(%s)" % (name, arguments))
            try:
                for item in self.channel:
                    if item is None:
                        yield item
                    else:
                        self.channel.close()
            except Exception as error:
                # Error will come as a string of a traceback, remove everything
                # up to the actual exception since we do get garbage otherwise
                # that points to non-existent lines in the compiled code
                exc_line = str(error)
                for tb_line in reversed(str(error).split('\n')):
                    if tb_line:
                        exc_line = tb_line
                        break
                raise RuntimeError(exc_line)

        return wrapper_continuous if self.continuous else wrapper

    def _get_func_doc(self, func):
        try:
            return getattr(func, 'func_doc').strip()
        except AttributeError:
            return ''

    def _convert_args(self, args):
        if args:
            if len(args) > 1:
                arguments = str(args).rstrip(')').lstrip('(')
            else:
                arguments = str(args).rstrip(',)').lstrip('(')
        else:
            arguments = ''
        return arguments


#
# FIXME this is getting ridiculous
#

class FakeRemoteLogger:

    def error(self, *a, **kw):
        pass

    def debug(self, *a, **kw):
        pass

    def info(self, *a, **kw):
        pass

    def warning(self, *a, **kw):
        pass


def needs_ssh(hostname, _socket=None):
    """
    Obtains remote hostname of the socket and cuts off the domain part
    of its FQDN.
    """
    _socket = _socket or socket
    fqdn = _socket.getfqdn()
    if hostname == fqdn:
        return False
    local_hostname = _socket.gethostname()
    local_short_hostname = local_hostname.split('.')[0]
    if local_hostname == hostname or local_short_hostname == hostname:
        return False
    return True
