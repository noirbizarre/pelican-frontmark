from pelican import signals as pelican_signals

from .__about__ import __version__, __description__  # noqa
from .reader import add_reader


def register():
    pelican_signals.readers_init.connect(add_reader)
