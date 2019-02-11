import pytest
from remoto.connection import get


base_names = [
    'ssh', 'oc', 'openshift', 'kubernetes', 'k8s', 'local', 'popen', 'localhost', 'docker', 'podman',
]

capitalized_names = [n.capitalize() for n in base_names]

spaced_names = [" %s " % n for n in base_names]

valid_names = base_names + capitalized_names + spaced_names


class TestGet(object):

    @pytest.mark.parametrize('name', valid_names)
    def test_valid_names(self, name):
        conn_class = get(name)
        assert conn_class.__name__.endswith('Connection')

    def test_fallback(self):
        conn_class = get('non-existent')
        assert conn_class.__name__ == 'BaseConnection'

    def test_custom_fallback(self):
        conn_class = get('non-existent', 'openshift')
        assert conn_class.__name__ == 'OpenshiftConnection'
