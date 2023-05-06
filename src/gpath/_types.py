from __future__ import annotations

from enum import IntEnum, auto, unique


@unique
class PathType(IntEnum):
	GENERIC = 0
	POSIX = auto()
	POSIX_HOME = auto()
	POSIX_PORTABLE = auto()
	WINDOWS_NT = auto()
	UNC = auto()

	@staticmethod
	def from_str(name: str) -> PathType:
		return path_types[name]


canonical_path_types: dict[str, PathType] = {
	'generic': PathType.GENERIC,
	'posix': PathType.POSIX,
	'posix-portable': PathType.POSIX_PORTABLE,
	'windows-nt': PathType.WINDOWS_NT,
	'unc': PathType.UNC,
}

path_types: dict[str, PathType] = {
	**canonical_path_types,
	'': PathType.GENERIC,
	'posix': PathType.POSIX,
	'linux': PathType.POSIX,
	'macos': PathType.POSIX,
	'osx': PathType.POSIX,
	'portable': PathType.POSIX_PORTABLE,
	'win': PathType.WINDOWS_NT,
	'windows': PathType.WINDOWS_NT,
	'nt': PathType.WINDOWS_NT,
}
