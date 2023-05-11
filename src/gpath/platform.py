from __future__ import annotations

from enum import IntEnum, auto, unique


__all__ = ('Platform', 'canonical_platform_names', 'platform_names')


@unique
class Platform(IntEnum):
	GENERIC = 0
	POSIX = auto()
	WINDOWS = auto()

	@staticmethod
	def from_str(name: str) -> Platform:
		return platform_names[name]


canonical_platform_names: dict[str, Platform] = {
	'generic': Platform.GENERIC,
	'posix': Platform.POSIX,
	'windows': Platform.WINDOWS,
}
"""Canonical platform names and the Platform enum that they map to"""

platform_names: dict[str, Platform] = {
	**canonical_platform_names,
	'': Platform.GENERIC,
	'posix': Platform.POSIX,
	'linux': Platform.POSIX,
	'macos': Platform.POSIX,
	'osx': Platform.POSIX,
	'win': Platform.WINDOWS,
	'nt': Platform.WINDOWS,
}
"""Valid platform names and the Platform enum that they map to"""