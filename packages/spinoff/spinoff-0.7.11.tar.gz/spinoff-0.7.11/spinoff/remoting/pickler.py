# coding: utf8
from __future__ import print_function, absolute_import

from pickle import Unpickler, BUILD

from spinoff.actor.ref import Ref


class IncomingMessageUnpickler(Unpickler):
    """Unpickler for attaching a `Hub` instance to all deserialized `Ref`s."""

    def __init__(self, node, file):
        Unpickler.__init__(self, file)
        self.node = node

    # called by `Unpickler.load` before an uninitalized object is about to be filled with members;
    def _load_build(self):
        """See `pickle.py` in Python's source code."""
        # if the ctor. function (penultimate on the stack) is the `Ref` class...
        if isinstance(self.stack[-2], Ref):
            # Ref.__setstate__ will know it's a remote ref if the state is a tuple
            self.stack[-1] = (self.stack[-1], self.node)

            self.load_build()  # continue with the default implementation

            # detect our own refs sent back to us
            ref = self.stack[-1]
            if ref.uri.node == self.node.nid:
                ref.is_local = True
                ref._cell = self.node.guardian.lookup_cell(ref.uri)
                # dbg(("dead " if not ref._cell else "") + "local ref detected")
                del ref.node  # local refs never need access to the node
        else:  # pragma: no cover
            self.load_build()

    dispatch = dict(Unpickler.dispatch)  # make a copy of the original
    dispatch[BUILD] = _load_build  # override the handler of the `BUILD` instruction
