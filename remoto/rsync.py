from .lib import execnet
from .connection import Connection, FakeRemoteLogger


class _RSync(execnet.RSync):
    """
    Inherits from ``execnet.RSync`` so that we can log nicely with the user
    logger instance (if any) back with the ``_report_send_file`` method
    """

    def __init__(self, sourcedir, callback=None, verbose=True, logger=None):
        self.logger = logger
        super(_RSync, self).__init__(sourcedir, callback, verbose)

    def _report_send_file(self, gateway, modified_rel_path):
        if self._verbose:
            self.logger.info("syncing file: %s" % modified_rel_path)


def rsync(hosts, source, destination, logger=None, sudo=False):
    """
    Grabs the hosts (or single host), creates the connection object for each
    and set the rsync execnet engine to push the files.

    It assumes that all of the destinations for the different hosts is the
    same. This deviates from what execnet does because it has the flexibility
    to push to different locations.
    """
    logger = logger or FakeRemoteLogger()
    sync = _RSync(source, logger=logger)

    # setup_targets
    if not isinstance(hosts, list):
        hosts = [hosts]

    for host in hosts:
        conn = Connection(
            host,
            logger,
            sudo,
        )
        sync.add_target(conn.gateway, destination)

    return sync.send()
