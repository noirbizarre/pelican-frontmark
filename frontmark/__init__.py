import pelican.signals

from .reader import add_reader


def register():
    pelican.signals.readers_init.connect(add_reader)
