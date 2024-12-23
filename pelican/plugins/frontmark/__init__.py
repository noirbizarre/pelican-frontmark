from __future__ import annotations

from pelican.plugins.signals import readers_init

from .__about__ import __description__, __version__  # noqa
from .reader import add_reader


def register():
    readers_init.connect(add_reader)
