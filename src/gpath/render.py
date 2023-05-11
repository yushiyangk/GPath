from __future__ import annotations

import functools
from abc import ABC, abstractmethod
from typing import Type

from . import _rules
from .platform import Platform


__all__ = (
	'RenderedPath',
	'GenericRenderedPath',
	'PosixRenderedPath',
	'LinuxRenderedPath',
	'MacOsRenderedPath',
	'WindowsRenderedPath',
)


class Renderable(ABC):
	@property
	@abstractmethod
	def named_parts(self):
		pass

	@property
	@abstractmethod
	def relative_parts(self):
		pass

	@property
	@abstractmethod
	def absolute(self):
		pass

	@property
	@abstractmethod
	def drive(self):
		pass

	@property
	@abstractmethod
	def parent_level(self):
		pass

	@abstractmethod
	def __str__(self):
		pass

	@abstractmethod
	def __repr__(self):
		pass


@functools.total_ordering
class RenderedPath:
	__slots__ = ('_path')

	def __init__(self, path: Renderable):
		self._path: Renderable = path

	def __str__(self) -> str:
		return str(self._path)

	def __repr__(self) -> str:
		return f"{type(self).__name__}({repr(self._path)})"

	def __eq__(self, other) -> bool:
		return self._tuple == other._tuple

	def __lt__(self, other) -> bool:
		return self._tuple < other._tuple

	@property
	def _tuple(self) -> tuple:
		return (
			self._path.absolute,
			self._path.drive,
			self._path.parent_level,
			self._path.named_parts,
		)


class GenericRenderedPath(RenderedPath):
	def __str__(self) -> str:
		if bool(self):
			return (self._path.drive + _rules.generic_rules.drive_postfixes[0] if self._path.drive != "" else "") + (_rules.generic_rules.roots[0] if self._path.absolute else "") + _rules.generic_rules.separators[0].join(self._path.relative_parts)
		else:
			return _rules.generic_rules.current_indicators[0]


class PosixRenderedPath(RenderedPath):
	def __str__(self) -> str:
		if bool(self):
			return (_rules.posix_rules.roots[0] if self._path.absolute else "") + _rules.posix_rules.separators[0].join(self._path.relative_parts)
		else:
			return _rules.posix_rules.current_indicators[0]

	@property
	def _tuple(self) -> tuple:
		return (
			self._path.absolute,
			self._path.parent_level,
			self._path.named_parts,
		)

LinuxRenderedPath = PosixRenderedPath
MacOsRenderedPath = PosixRenderedPath


class WindowsRenderedPath(RenderedPath):
	def __str__(self) -> str:
		if bool(self):
			return (self._path.drive + _rules.windows_rules.drive_postfixes[0] if self._path.drive != "" else "") + (_rules.windows_rules.roots[0] if self._path.absolute else "") + _rules.windows_rules.separators[0].join(self._path.relative_parts)
		else:
			return _rules.windows_rules.current_indicators[0]


_platform_render: dict[Platform, Type[RenderedPath]] = {
	Platform.GENERIC: GenericRenderedPath,
	Platform.POSIX: PosixRenderedPath,
	Platform.WINDOWS: WindowsRenderedPath,
}


def get_type(platform: Platform) -> Type[RenderedPath]:
	"""Get the type of RenderedPath that corresponds to the given Platform"""
	return _platform_render[platform]
