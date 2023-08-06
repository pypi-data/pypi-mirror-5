from zope.interface import implements
from zope.interface.verify import verifyClass

from spinoff.remoting.hub import IHub


class HubWithNoRemoting(object):
    """A dummy hub used during networkless testing and in production when no remoting should be available.

    All it does is imitate the interface of the real `Hub`, and report attempts to send remote messages as
    `RuntimeError`s.

    """
    implements(IHub)

    # to be compatible with Hub:
    guardian = None
    nodeid = None

    def __init__(self, *args, **kwargs):
        pass

    def send_message(self, *args, **kwargs):  # pragma: no cover
        raise RuntimeError("Attempt to send a message to a remote ref but remoting is not available")

    def stop(self):  # pragma: no cover
        pass

    def watch_node(self, *args, **kwargs):
        raise RuntimeError("Attempt to watch a remote node but remoting is not available")

    def unwatch_node(self, *args, **kwargs):
        raise RuntimeError("Attempt to unwatch a remote node but remoting is not available")
verifyClass(IHub, HubWithNoRemoting)
