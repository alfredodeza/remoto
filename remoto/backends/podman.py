from .docker import DockerConnection


class PodmanConnection(DockerConnection):

    executable = 'podman'
