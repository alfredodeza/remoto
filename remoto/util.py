

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
