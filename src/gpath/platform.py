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

	def __str__(self) -> str:
		"""Return the name of the platform as a string"""
		return _name_from_platform[self]


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
}
"""Valid platform names and the Platform enum that they map to"""


_name_from_platform: dict[Platform, str] = {v: k for k, v in canonical_platform_names.items()}
