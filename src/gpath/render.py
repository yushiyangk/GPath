from __future__ import annotations

import functools
from abc import ABC, abstractmethod
from typing import Type

from . import _rules
from .platform import Platform


__all__ = (
	'Renderable',
	'RenderedPath',
	'GenericRenderedPath',
	'PosixRenderedPath',
	'LinuxRenderedPath',
	'MacOsRenderedPath',
	'WindowsRenderedPath',
)


class Renderable(ABC):
	"""
		Abstract interface that represents any object that can be converted to a RenderedPath.

		Abstract properties
		-------------------
		`named_parts: list[str]`
		: read-only named components of the path, not including the filesystem root, drive name, or any parent directories

		`relative_parts: list[str]`
		: read-only relative components of the path, not including the filesystem root or drive name, including one item for each level of parent directory

		`absolute: bool`
		: read-only flag for whether the path is an absolute path

		`parent_level: int`
		: read-only number of levels of parent directories that the path is relative to, which may be 0
	"""

	@property
	@abstractmethod
	def named_parts(self) -> list[str]:
		pass

	@property
	@abstractmethod
	def relative_parts(self) -> list[str]:
		pass

	@property
	@abstractmethod
	def absolute(self) -> bool:
		pass

	@property
	@abstractmethod
	def drive(self) -> str:
		pass

	@property
	@abstractmethod
	def parent_level(self) -> int:
		pass

	@abstractmethod
	def __repr__(self) -> str:
		"""
			Return a string representation of the object instance for debugging
		"""
		pass


@functools.total_ordering
class RenderedPath(ABC):
	"""
		Abstract base class for rendered path objects that target a specific operating system.

		Whereas GPath represents a generalised abstract path, RenderedPath represents a file path on a specific platform with properties defined by the specific type of filesystem. Note however that the RenderedPath still does not represent a real file in a real filesystem, and can represent file paths on a system other than local.

		The additional semantics available to RenderedPath allows it to be:
		- printed in a format preferred by the given platform
		- meaningfully compared and sorted
	"""

	__slots__ = ('_path')

	def __hash__(self) -> int:
		"""
			Calculate hash of the RenderedPath.

			Usage: <code>hash(<var>rp</var>)</code>
		"""
		return hash(self._tuple)

	def __init__(self, path: Renderable):
		"""
			Initialise a rendered path from any object that is Renderable.
		"""
		self._path: Renderable = path

	def __eq__(self, other) -> bool:
		"""
			Check if two RenderedPaths have the same target platform, and check if they have equivalent values on that platform

			Usage: <code><var>rp1</var> == <var>rp2</var></code>
		"""
		return type(self) == type(other) and self._tuple == other._tuple

	def __lt__(self, other) -> bool:
		"""
			Check if `self` should be collated before `other`

			Usage: <code><var>rp1</var> < <var>rp2</var></code>
		"""
		return self._tuple < other._tuple

	def __bool__(self) -> bool:
		"""
			False if `self` is equivalent to an empty path on the target platform, and True otherwise

			By default, False if `self` is a relative path without any relative components and without a drive, and True otherwise.

			Usage: <code>bool(<var>rp</var>)</code>, <code>not <var>rp</var></code>, or <code>if <var>rp</var>:</code>
		"""
		return self._path.absolute or self._path.drive != "" or self._path.parent_level != 0 or len(self._path.named_parts) > 0

	def __str__(self) -> str:
		"""
			Return a string representation of the path in the preferred format for the target platform

			Usage: <code>str(<var>rp</var>)</code>
		"""
		return repr(self)

	def __repr__(self) -> str:
		"""
			Return a string that, when printed, gives the Python code associated with instantiating a copy of `self`.

			Usage: <code>repr(<var>rp</var>)</code>
		"""
		return f"{type(self).__name__}({repr(self._path)})"

	@property
	def _tuple(self) -> tuple:
		return (
			self._path.absolute,
			self._path.drive,
			self._path.parent_level,
			self._path.named_parts,
		)


class GenericRenderedPath(RenderedPath):
	"""
		A rendered path that maximises interoperability between different target platforms, specifically between Windows and POSIX-like operating systems.

		This is done at the expense of producing outputs that may not conform to platform recommendations but that should still be usable across different platforms.

		Note that if the path contains a drive, it should be removed if the path is to be used on Linux or macOS. On Windows, forward slashes / will be used in favour of backslashes.
	"""
	def __str__(self) -> str:
		if bool(self):
			return (self._path.drive + _rules.generic_rules.drive_postfixes[0] if self._path.drive != "" else "") + (_rules.generic_rules.roots[0] if self._path.absolute else "") + _rules.generic_rules.separators[0].join(self._path.relative_parts)
		else:
			return _rules.generic_rules.current_indicators[0]


class PosixRenderedPath(RenderedPath):
	"""
		A rendered path meant for POSIX-like operating systems, such as Linux and macOS.

		If the original path contains a drive, it will be ignored for both printing and collation. Forward slashes are used always.
	"""
	def __str__(self) -> str:
		if bool(self):
			return (_rules.posix_rules.roots[0] if self._path.absolute else "") + _rules.posix_rules.separators[0].join(self._path.relative_parts)
		else:
			return _rules.posix_rules.current_indicators[0]

	def __bool__(self) -> bool:
		"""
			False if `self` is a relative path without any relative components, and True otherwise.

			Usage: <code>bool(<var>rp</var>)</code>, <code>not <var>rp</var></code>, or <code>if <var>rp</var>:</code>
		"""
		return self._path.absolute or self._path.parent_level != 0 or len(self._path.named_parts) > 0

	@property
	def _tuple(self) -> tuple:
		return (
			self._path.absolute,
			self._path.parent_level,
			self._path.named_parts,
		)

LinuxRenderedPath = PosixRenderedPath
"""Alias of `PosixRenderedPath`"""

MacOsRenderedPath = PosixRenderedPath
"""Alias of `PosixRenderedPath`"""


class WindowsRenderedPath(RenderedPath):
	"""
		A rendered path meant for Windows operating systems.

		The path may or may not contain a drive, which affects both its printed output and its collation order. Backslashes are used always, although forward slashes are supported on Windows NT also.
	"""
	def __str__(self) -> str:
		if bool(self):
			return (self._path.drive + _rules.windows_rules.drive_postfixes[0] if self._path.drive != "" else "") + (_rules.windows_rules.roots[0] if self._path.absolute else "") + _rules.windows_rules.separators[0].join(self._path.relative_parts)
		else:
			return _rules.windows_rules.current_indicators[0]


_render_of_platforms: dict[Platform, Type[RenderedPath]] = {
	Platform.GENERIC: GenericRenderedPath,
	Platform.POSIX: PosixRenderedPath,
	Platform.WINDOWS: WindowsRenderedPath,
}


def get_type(platform: Platform) -> Type[RenderedPath]:
	"""Get the type of RenderedPath that corresponds to the given Platform"""
	return _render_of_platforms[platform]
