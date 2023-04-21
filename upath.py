from __future__ import annotations

import functools
import os
from collections.abc import Collection, Sequence
from typing import Any, Final, ClassVar

PATH_SEPARATOR: Final = "/" if os.sep == '/' or os.altsep == '/' else os.sep
PATH_PARENT: Final = os.pardir

PathLike = str | os.PathLike

@functools.total_ordering
class UPath():
	"""
		A normalised abstract file path with no dependency on the layout of the local filesystem or, if different, the source filesystem that generated the path representation.

		The path can be manipulated before being rendered in a format that is meaningful to the local operating system.

		Class attributes
		----------------
		- `separator: str`
		   path separator that is meaningful to the local operating system
		- `parent: str`
		   path component indicating a parent directory that is meaningful to the local operating system; usually ".."
	"""

	__slots__ = ('_parts', '_device', '_root', '_dotdot')

	separator: ClassVar = PATH_SEPARATOR
	parent: ClassVar = PATH_PARENT

	def __init__(self, path: PathLike | UPath | None='') -> None:
		"""
			Initialise a normalised abstract file path, possibly by copying an existing UPath object.

			Evoked by `UPath(path)` and mutates `self`

			Parameters
			----------
			- `path: PathLike | UPath | None`
			   path-like object representing a (unnormalised) file path, or a UPath object to be copied

			Raises
			------
				`ValueError`
				if `other` is an invalid UPath
		"""
		self._parts: tuple[str, ...] = ()  # root- or dotdot- relative path
		self._device: str | None = None
		self._root: bool = False
		self._dotdot: int = 0
		if path is not None and path != '':
			if isinstance(path, UPath):
				path._validate()
				self._parts = path._parts
				self._device = path._device
				self._root = path._root
				self._dotdot = path._dotdot
			else:
				# Remove redundant '.'s and '..'s and use OS-default path separators
				path = os.path.normpath(path)  # sets empty path to '.' and removes trailing slash

				if path == '.':
					path = ''
				(self._device, path) = os.path.splitdrive(path)
				self._root = os.path.isabs(path)

				parts = path.split(os.sep)  # os.path.normpath previously rewrote the path to use os.sep
				if parts[0] == '':  # First element is '' if root
					parts = parts[1:]
				if parts[-1] == '':  # Last element is '' if there is a trailing slash, which should only happen when the path is exactly root ('/')
					parts = parts[:-1]

				dotdot = 0
				while parts[dotdot] == UPath.parent:  # UPath.parent == '..' usually
					dotdot += 1
				self._parts = tuple(parts[dotdot:])
				self._dotdot = dotdot

	@staticmethod
	def find_common(path1: UPathLike, path2: UPathLike) -> UPath | None:
		"""
			Static method. Find the longest common base path shared by two abstract file paths.

			Parameters
			----------
			  `path1: UPath | str | os.PathLike`, `path2: UPath | str | os.PathLike`
			   the abstract file paths to compare

			Returns
			-------
			- `UPath`
			   longest common base path, which may be empty if `path1` and `path2` are relative to the same filesystem root or to the same level of parent directories
			- `None`
			   otherwise

			Raises
			------
				`ValueError`
				if either UPath is invalid
		"""
		if isinstance(path1, UPath):
			path1._validate()
		else:
			path1 = UPath(path1)
		if isinstance(path2, UPath):
			path2._validate()
		else:
			path2 = UPath(path2)

		if path1._device != path2._device:
			return None
		if path1._root != path2._root:
			return None

		parts = []
		if path1._root:
			common_path = UPath()
			for part1, part2 in zip(path1._parts, path2._parts):
				if part1 == part2:
					parts.append(part1)
			common_path._root = True
			common_path._device = path1._device
			# dotdot must be 0
		else:
			if path1._dotdot != path2._dotdot:
				return None
			common_path = UPath()
			for part1, part2 in zip(path1._parts, path2._parts):
				if part1 == part2:
					parts.append(part1)
			common_path._dotdot = path1._dotdot
		common_path._parts = tuple(parts)

		return common_path

	@staticmethod
	def partition(paths: Collection[UPathLike]) -> dict[UPath, set[UPath]]:
		"""
			Static method. Partition a collection of abstract file paths based on the common base paths shared between members of the collection, such that each abstract file path can only belong to one partition.

			The partitioning logic is identical to that of `UPath.common(...)`. Paths that are relative to ancestor directories of different levels will be placed in distinct partitions.

			Parameters
			----------
			  `paths: Collection[UPath | str | os.PathLike]`
			   the list of abstract file paths to partition

			Returns
			-------
			  `dict[UPath, set[UPath]]`
			   dictionary that maps the common base path of each partition to a set of paths that belong to that partition

			Raises
			------
				`ValueError`
				if any of the UPath is invalid
		"""
		paths = [path if isinstance(path, UPath) else UPath(path) for path in paths]

		partition_map = {}
		if len(paths) > 0:
			partition_map[paths[0]] = set([paths[0]])

		for path in paths[1:]:
			partition_found = False
			for partition in partition_map:
				candidate_common = UPath.find_common(partition, path)
				if candidate_common is not None and bool(candidate_common):
					partition_found = True
					if candidate_common != partition:
						partition_map[candidate_common] = partition_map[partition]
						del partition_map[partition]
					partition_map[candidate_common].insert(path)
					break
			if not partition_found:
				partition_map[path] = set([path])

		return partition_map

	@staticmethod
	def join_str(paths: Sequence[UPathLike], delim: str="") -> str:
		"""
			Static method. Convenience method for joining a list of abstract file paths using the delimeter, if given, and return it as a string.
		"""
		return delim.join(str(path) for path in paths)

	def get_parts(self) -> list[str]:
		"""
			Get a list of strings representing each component of the abstract file path.

			If the path is relative to a filesystem root, the first item in the returned list will contain the device name if it exists, or an empty string otherwise. This allows the full path to be reconstructed as a string using `UPath.separator.join(myupath.get_parts())`.

			To get a list without information about any filesystem root, use `get_relative_parts()` instead.

			If the path is relative to an ancestor directory (e.g. '../..'), each parent level will be given as a separate item in the returned list.

			To get a list without information about any ancestor directory or filesystem root, use `get_name_parts()` instead.
		"""
		base_parts = []
		if self._root:
			base_parts = ['' if self._device is None else self._device]
		elif self._dotdot > 0:
			base_parts = [UPath.parent for i in range(self._dotdot)]
		return base_parts + list(self._parts)

	def get_relative_parts(self) -> list[str]:
		"""
			Get a list of strings representing each relative component of the abstract file path.

			The returned list will always represent a relative path, with no information about whether the path was relative to any filesystem root.

			To get a list including the filesystem root, use `get_parts()` instead.

			If the path is relative to an ancestor directory (e.g. '../..'), each parent level will be given as a separate item in the returned list.

			To get a list without information about any ancestor directory as well, use `get_name_parts()` instead.
		"""
		base_parts = []
		if self._dotdot > 0:
			base_parts = [UPath.parent for i in range(self._dotdot)]
		return base_parts + list(self._parts)

	def get_named_parts(self) -> list[str]:
		"""
			Get a list of strings representing each named component of the abstract file path.

			The returned list will always represent a descendent relative path, with no information about whether the path was relative to any filesystem root or to any ancestor directories.

			To get a list of parts with more information, use `get_parts()` or `get_relative_parts()` instead.
		"""
		return list(self._parts)

	def get_parent_parts(self) -> list[str]:
		"""
			Get a list of strings representing the ancestor directory that the path is relative to.

			The returned list will one copy of `UPath.parent` for each parent level. If the path is not relative to an ancestor directory, the returned list will be empty.
		"""
		return [UPath.parent for i in range(self._dotdot)]

	def get_device(self) -> str | None:
		"""
			Get the device name of the path.
		"""
		return self._device

	def is_root(self) -> bool:
		"""
			Check if the path is relative to filesystem root
		"""
		return self._root

	def subpath(self, base: UPathLike) -> UPath | None:
		"""
			Find the relative subpath path from `base` to `self` if `base` is an ancestor of `self.

			Parameters
			----------
			- `base: UPathLike`
			   the base path against which `self` is compared

			Returns
			-------
			- `UPath`
			   relative path from `base` to `self`, which may be empty, if `self` is a descendent
			- `None`
			   otherwise

			Raises
			------
				`ValueError`
				if either `self` or `other` is an invalid UPath
		"""
		if not isinstance(base, UPath):
			base = UPath(base)

		common_path = UPath.find_common(self, base)
		if common_path is not None and common_path == base:
			base_length = len(base._parts)
			new_path = UPath()
			new_path._parts = self._parts[base_length:]  # [] when self == base
			return new_path
		else:
			return None

	def __hash__(self) -> int:
		"""
			Calculate hash of the path.

			Evoke as `hash(myupath)`
		"""
		return hash((tuple(self._parts), self._device, self._root, self._dotdot))

	def __eq__(self, other: Any) -> bool:
		"""
			Check if two abstract file paths are completely identical. Always return False if `other` is not a UPath object.

			Evoke as `upath1 == upath2`
		"""
		if type(other) is UPath:
			return ((self._root, self._device, self._dotdot) + self._parts) == ((other._root, other._device, other._dotdot) + other._parts)
		else:
			return False

	def __gt__(self, other: UPathLike) -> bool:
		"""
			Check if `self` should be collated after `other` by comparing their component-wise lexicographical order. Root-relative paths are greater than ancestor-relative paths, which are greater than all other paths. Between two ancestor-relative paths, the path with more ancestor components is considered greater.

			Evoke as `upath1 < upath2`
		"""
		if not isinstance(other, UPath):
			other = UPath(other)
		return ((self._root, self._device, self._dotdot) + self._parts) > ((other._root, other._device, other._dotdot) + other._parts)

	def __bool__(self) -> bool:
		"""
			Return True if `self` is relative to root or an ancestor directory, or if `self` has at least one named component; return False otherwise.

			Evoke as `bool(myupath)`
		"""
		return self._root or self._dotdot != 0 or len(self._parts) > 0

	def __str__(self) -> str:
		"""
			Return a string representation of the abstract file path that is meaningful to the local operating system.

			Evoke as `str(myupath)`
		"""
		return UPath.separator.join(self.get_parts())

	def __repr__(self) -> str:
		"""
			Return a string that can be printed as a source code representation of the abstract file path.

			Evoke as `repr(myupath)`
		"""
		return f"UPath({repr(str(self))})"

	def __getitem__(self, n: int) -> str:
		"""
			Get the 0-indexed path component, excluding any device name or any parent directories.

			Evoke as `myupath[n]`
		"""
		return self._parts[n]

	def __add__(self, other: UPathLike) -> UPath | None:
		"""
			Add a relative UPath to `self` and return the new UPath. Return an unchagned copy of `self` if `other` is not a relative path, or if `other` and `self` have different `device`.

			Evoked by `upath1 + upath2`

			Raises `ValueError` if either UPath is invalid
		"""
		self._validate()
		if isinstance(other, UPath):
			other._validate
		else:
			other = UPath(other)

		if other._root:
			return UPath(self)
		elif other._device != None and self._device != other._device:
			return UPath(self)
		else:
			new_path = UPath(self)
			new_parts = [part for part in self._parts]
			for i in range(other._dotdot):
				if len(new_parts) > 0:
					new_parts.pop()
				elif not new_path._root:
					new_path._dotdot += 1
				else:
					pass  # parent of directory of root is still root

			new_parts.extend(other._parts)
			new_path._parts = tuple(new_parts)
			return new_path

	def _validate(self) -> bool:
		# Check if self is in a valid state
		if self._dotdot < 0:
			raise ValueError(f"invalid UPath, dotdot cannot be negative: {repr(self)}")
		if self._root:
			if self._dotdot != 0:
				raise ValueError(f"invalid UPath, dotdot must be 0 when root is True: {repr(self)}")
		return True

UPathLike = UPath | PathLike
