import logging
# compatibility for older clients that rely on the previous ``Connection`` class
from remoto.backends import BaseConnection as Connection # noqa
from remoto.backends import ssh, openshift, kubernetes, local, podman, docker, needs_ssh


logger = logging.getLogger('remoto')


def get(name, fallback='ssh'):
    """
    Retrieve the matching backend class from a string. If no backend can be
    matched, it raises an error.

    >>> get('ssh')
    <class 'remoto.backends.BaseConnection'>
    >>> get()
    <class 'remoto.backends.BaseConnection'>
    >>> get('non-existent')
    <class 'remoto.backends.BaseConnection'>
    >>> get('non-existent', 'openshift')
    <class 'remoto.backends.openshift.OpenshiftConnection'>
    """
    mapping = {
        'ssh': ssh.SshConnection,
        'oc': openshift.OpenshiftConnection,
        'openshift': openshift.OpenshiftConnection,
        'kubernetes': kubernetes.KubernetesConnection,
        'k8s': kubernetes.KubernetesConnection,
        'local': local.LocalConnection,
        'popen': local.LocalConnection,
        'localhost': local.LocalConnection,
        'docker': docker.DockerConnection,
        'podman': podman.PodmanConnection,
    }
    if not name:
        # fallsback to just plain local/ssh
        name = 'ssh'

    name = name.strip().lower()
    connection_class = mapping.get(name)
    if not connection_class:
        logger.warning('no connection backend found for: "%s"' % name)
        if fallback:
            logger.info('falling back to "%s"' % fallback)
            # this assumes that ``fallback`` is a valid mapping name
            return mapping.get(fallback)
    return connection_class
