from __future__ import annotations

from enum import IntEnum, auto, unique


__all__ = ('Platform', 'canonical_platform_names', 'platform_names')


@unique
class Platform(IntEnum):
	"""
		An Enum representing the different types of operating systems recognised by GPath.

		This is used either when rendering output to a specific target platform, or to enforce maximum correctness when instantiating a new GPath from a specific origin platform. The latter use-case is not required for most normal file paths.

		A Platform object can be obtained using `Platform.from_str()`.
	"""

	GENERIC = 0
	POSIX = auto()
	WINDOWS = auto()

	@staticmethod
	def from_str(name: str) -> Platform:
		"""
			Get the Platform object associated with a given platform name.

			Valid platform names are listed in `platform_names`.
		"""
		return platform_names[name]

	def __str__(self) -> str:
		"""
			Return the name of the platform as a string.
		"""
		return _name_of_platforms[self]


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


_name_of_platforms: dict[Platform, str] = {v: k for k, v in canonical_platform_names.items()}
