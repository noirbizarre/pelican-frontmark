from pelican import signals

from .reader import add_reader


def register():  # pragma: no cover
    signals.readers_init.connect(add_reader)
