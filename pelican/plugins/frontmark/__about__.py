from __future__ import annotations

from pathlib import Path

version_file = Path(__file__).parent / "VERSION"

__version__ = version_file.read_text() if version_file.is_file() else "0.0.0.dev"
__description__ = "CommonMark/Frontmatter reader for Pelican"
