from __future__ import annotations

import functools
import os
from collections.abc import Collection, Iterator, Sequence
from typing import Any, Final, ClassVar

PATH_SEPARATOR: Final = "/" if os.sep == '/' or os.altsep == '/' else os.sep
PATH_PARENT: Final = os.pardir

PathLike = str | os.PathLike

@functools.total_ordering
class GPath():
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

	def __init__(self, path: PathLike | GPath | None='') -> None:
		"""
			Initialise a normalised abstract file path, possibly by copying an existing GPath object.

			Evoked by `GPath(path)` and mutates `self`

			Parameters
			----------
			- `path: PathLike | GPath | None`
			   path-like object representing a (unnormalised) file path, or a GPath object to be copied

			Raises
			------
				`ValueError`
				if `other` is an invalid GPath
		"""
		self._parts: tuple[str, ...] = ()  # root- or dotdot- relative path
		self._device: str | None = None
		self._root: bool = False
		self._dotdot: int = 0
		if path is not None and path != '':
			if isinstance(path, GPath):
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
				while parts[dotdot] == GPath.parent:  # GPath.parent == '..' usually
					dotdot += 1
				self._parts = tuple(parts[dotdot:])
				self._dotdot = dotdot

	@staticmethod
	def find_common(path1: GPathLike, path2: GPathLike) -> GPath | None:
		"""
			Static method. Find the longest common base path shared by two abstract file paths.

			Parameters
			----------
			  `path1: GPath | str | os.PathLike`, `path2: GPath | str | os.PathLike`
			   the abstract file paths to compare

			Returns
			-------
			- `GPath`
			   longest common base path, which may be empty if `path1` and `path2` are relative to the same filesystem root or to the same level of parent directories
			- `None`
			   otherwise

			Raises
			------
				`ValueError`
				if either GPath is invalid
		"""
		if isinstance(path1, GPath):
			path1._validate()
		else:
			path1 = GPath(path1)
		if isinstance(path2, GPath):
			path2._validate()
		else:
			path2 = GPath(path2)

		if path1._device != path2._device:
			return None
		if path1._root != path2._root:
			return None

		parts = []
		if path1._root:
			common_path = GPath()
			for part1, part2 in zip(path1._parts, path2._parts):
				if part1 == part2:
					parts.append(part1)
			common_path._root = True
			common_path._device = path1._device
			# dotdot must be 0
		else:
			if path1._dotdot != path2._dotdot:
				return None
			common_path = GPath()
			for part1, part2 in zip(path1._parts, path2._parts):
				if part1 == part2:
					parts.append(part1)
			common_path._dotdot = path1._dotdot
		common_path._parts = tuple(parts)

		return common_path

	@staticmethod
	def partition(paths: Collection[GPathLike]) -> dict[GPath, set[GPath]]:
		"""
			Static method. Partition a collection of abstract file paths based on the common base paths shared between members of the collection, such that each abstract file path can only belong to one partition.

			The partitioning logic is identical to that of `GPath.common(...)`. Paths that are relative to ancestor directories of different levels will be placed in distinct partitions.

			Parameters
			----------
			  `paths: Collection[GPath | str | os.PathLike]`
			   the list of abstract file paths to partition

			Returns
			-------
			  `dict[GPath, set[GPath]]`
			   dictionary that maps the common base path of each partition to a set of paths that belong to that partition

			Raises
			------
				`ValueError`
				if any of the GPath is invalid
		"""
		paths = [path if isinstance(path, GPath) else GPath(path) for path in paths]

		partition_map = {}
		if len(paths) > 0:
			partition_map[paths[0]] = set([paths[0]])

		for path in paths[1:]:
			partition_found = False
			for partition in partition_map:
				candidate_common = GPath.find_common(partition, path)
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
	def join_str(paths: Sequence[GPathLike], delim: str="") -> str:
		"""
			Static method. Convenience method for joining a list of abstract file paths using the delimeter, if given, and return it as a string.
		"""
		return delim.join(str(path) for path in paths)

	def get_parts(self) -> list[str]:
		"""
			Get a list of strings representing each component of the abstract file path.

			If the path is relative to a filesystem root, the first item in the returned list will contain the device name if it exists, or an empty string otherwise. This allows the full path to be reconstructed as a string using `GPath.separator.join(mygpath.get_parts())`.

			To get a list without information about any filesystem root, use `get_relative_parts()` instead.

			If the path is relative to an ancestor directory (e.g. '../..'), each parent level will be given as a separate item in the returned list.

			To get a list without information about any ancestor directory or filesystem root, use `get_name_parts()` instead.
		"""
		base_parts = []
		if self._root:
			base_parts = ['' if self._device is None else self._device]
		elif self._dotdot > 0:
			base_parts = [GPath.parent for i in range(self._dotdot)]
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
			base_parts = [GPath.parent for i in range(self._dotdot)]
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

			The returned list will one copy of `GPath.parent` for each parent level. If the path is not relative to an ancestor directory, the returned list will be empty.
		"""
		return [GPath.parent for i in range(self._dotdot)]

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

	def subpath(self, base: GPathLike) -> GPath | None:
		"""
			Find the relative subpath from `base` to `self` if `base` contains `self`.

			Parameters
			----------
			- `base: GPath | str | os.PathLike`
			   the base path against which `self` is compared

			Returns
			-------
			- `GPath`
			   relative path from `base` to `self`, which may be empty, if `self` is a descendent
			- `None`
			   otherwise

			Raises
			------
				`ValueError`
				if either `self` or `other` is an invalid GPath
		"""
		if not isinstance(base, GPath):
			base = GPath(base)

		if self in base:
			base_length = len(base._parts)
			new_path = GPath()
			new_path._parts = self._parts[base_length:]  # () when self == base
			return new_path
		else:
			return None

	def __hash__(self) -> int:
		"""
			Calculate hash of the path.

			Evoked by `hash(mygpath)`
		"""
		return hash((tuple(self._parts), self._device, self._root, self._dotdot))

	def __eq__(self, other: Any) -> bool:
		"""
			Check if two abstract file paths are completely identical. Always return False if `other` is not a GPath object.

			Evoked by `gpath1 == gpath2`
		"""
		if type(other) is GPath:
			return ((self._root, self._device, self._dotdot) + self._parts) == ((other._root, other._device, other._dotdot) + other._parts)
		else:
			return False

	def __gt__(self, other: GPathLike) -> bool:
		"""
			Check if `self` should be collated after `other` by comparing their component-wise lexicographical order. Root-relative paths are greater than ancestor-relative paths, which are greater than all other paths. Between two ancestor-relative paths, the path with more ancestor components is considered greater.

			Evoked by `gpath1 < gpath2`
		"""
		if not isinstance(other, GPath):
			other = GPath(other)
		return ((self._root, self._device, self._dotdot) + self._parts) > ((other._root, other._device, other._dotdot) + other._parts)

	def __bool__(self) -> bool:
		"""
			Return True if `self` is relative to root or an ancestor directory, or if `self` has at least one named component; return False otherwise.

			Evoked by `bool(mygpath)`
		"""
		return self._root or self._dotdot != 0 or len(self._parts) > 0

	def __str__(self) -> str:
		"""
			Return a string representation of the abstract file path that is meaningful to the local operating system.

			Evoked by `str(mygpath)`
		"""
		return GPath.separator.join(self.get_parts())

	def __repr__(self) -> str:
		"""
			Return a string that can be printed as a source code representation of the abstract file path.

			Evoked by `repr(mygpath)`
		"""
		return f"GPath({repr(str(self))})"

	def __len__(self) -> int:
		"""
			Get the number of relative path components, excluding any device name or parent directories.

			Evoked by `len(mygpath)`
		"""
		return len(self._parts)

	def __getitem__(self, n: int) -> str:
		"""
			Get the 0-indexed relative path component, excluding any device name or parent directories.

			Evoked by `mygpath[n]`
		"""
		return self._parts[n]

	def __iter__(self) -> Iterator[str]:
		"""
			Get an iterator through the relative path components, excluding any device name or parent directories.

			Evoked by `iter(mygpath)`
		"""
		return iter(self._parts)

	def __contains__(self, other: GPathLike) -> bool:
		"""
			Check if the path represented by `self` contains that represented by `other`; i.e. check if `self` is an ancestor path of `other`.

			Evoked by `other in mygpath`

			Raises `ValueError` if either GPath is invalid
		"""
		if not isinstance(other, GPath):
			other = GPath(other)

		common_path = GPath.find_common(self, other)
		return common_path is not None and common_path == self

	def __add__(self, other: GPathLike) -> GPath:
		"""
			Add (append) `other` to the end of `self` if `other` is a relative path, and return a new copy. If `other` is relative to the filesystem root, or if `other` has a different device name, add nothing and return a copy of `self`.

			Evoked by `gpath1 + gpath2`

			Raises `ValueError` if either GPath is invalid
		"""
		if isinstance(other, GPath):
			other._validate
		else:
			other = GPath(other)

		if other._root:
			return GPath(self)
		elif other._device != None and self._device != other._device:
			return GPath(self)
		else:
			new_path = GPath(self)
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

	def __sub__(self, n: int) -> GPath:
		"""
			Remove `n` components from the end of the path and return a new copy.

			Evoked by `mygpath - n`

			Raises `ValueError` if `self` is an invalid GPath
		"""
		new_path = GPath(self)
		new_parts = [part for part in self._parts]
		for i in range(n):
			if len(new_parts) > 0:
				new_parts.pop()
			elif not new_path._root:
				new_path._dotdot += 1
			else:
				pass  # removing components from root should still give root
		new_path._parts = tuple(new_parts)
		return new_path

	def __mul__(self, n: int) -> GPath:
		"""
			Duplicate the relative path in `self` `n` times and append them to `self`. If the path is relative to filesystem root, only the relative component of the path will be duplicated.

			Evoked by `mgpath * n`

			Raises `ValueError` if `self` is an invalid GPath
		"""
		new_path = GPath(self)
		new_path._parts = self._parts * n
		return new_path

	def __lshift__(self, n: int) -> GPath:
		"""
			Imagine moving the current directory `n` steps up the filesystem tree. If the path is relative to an ancestor directory, remove up to `n` levels of parent directories from the start of the path and return a copy. If the path is not relative to an ancestor directory, return a copy of `self` unchanged.

			Evoked by `mygpath << n`

			Raises `ValueError` if `self` is an invalid GPath
		"""
		new_path = GPath(self)
		if not new_path._root:
			new_path._dotdot = max(new_path._dotdot - n, 0)
		return new_path

	def __rshift__(self, n: int) -> GPath:
		"""
			Imagine moving the current directory `n` steps down the filesystem tree. If the path is not relative to filesystem root, add `n` levels of parent directoreis to the start of the path and return a copy. If the path is relative to filesystem root, return a copy of `self` unchanged.

			Evoked by `mygpath >> n`

			Raises `ValueError` if `self` is an invalid GPath
		"""
		new_path = GPath(self)
		if not new_path._root:
			new_path._dotdot += n
		return new_path

	def _validate(self) -> bool:
		# Check if self is in a valid state
		if self._dotdot < 0:
			raise ValueError(f"invalid GPath, dotdot cannot be negative: {repr(self)}")
		if self._root:
			if self._dotdot != 0:
				raise ValueError(f"invalid GPath, dotdot must be 0 when root is True: {repr(self)}")
		return True

GPathLike = GPath | PathLike
