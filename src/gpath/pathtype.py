from __future__ import annotations

from enum import IntEnum, auto, unique


@unique
class PathType(IntEnum):
	GENERIC = 0
	POSIX = auto()
	WINDOWS_NT = auto()

	@staticmethod
	def from_str(name: str) -> PathType:
		return path_types[name]


canonical_path_types: dict[str, PathType] = {
	'generic': PathType.GENERIC,
	'posix': PathType.POSIX,
	'windows-nt': PathType.WINDOWS_NT,
}

path_types: dict[str, PathType] = {
	**canonical_path_types,
	'': PathType.GENERIC,
	'posix': PathType.POSIX,
	'linux': PathType.POSIX,
	'macos': PathType.POSIX,
	'osx': PathType.POSIX,
	'win': PathType.WINDOWS_NT,
	'windows': PathType.WINDOWS_NT,
	'nt': PathType.WINDOWS_NT,
}
