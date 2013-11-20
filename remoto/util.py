

def admin_command(sudo, command):
    """
    If sudo is needed, make sure the command is prepended
    correctly, otherwise return the command as it came.

    :param sudo: A boolean representing the intention of having a sudo command
                (or not)
    :param command: A list of the actual command to execute with Popen.
    """
    if sudo:
        if not isinstance(command, list):
            command = [command]
        return ['sudo'] + [cmd for cmd in command]
    return command


class RemoteError(object):

    def __init__(self, traceback):
        self.orig_traceback = traceback
        self.exception_line = ''
        self.exception_name = self.get_exception_name()

    def get_exception_name(self):
        for tb_line in reversed(self.orig_traceback.split('\n')):
            if tb_line:
                for word in tb_line.split():
                    if word.endswith(':'):  # exception!
                        self.exception_line = tb_line
                        return word.strip().strip(':')
