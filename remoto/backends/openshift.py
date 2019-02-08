from .kubernetes import KubernetesConnection


class OpenshiftConnection(KubernetesConnection):

    executable = 'oc'
