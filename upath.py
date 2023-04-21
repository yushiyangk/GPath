from __future__ import annotations

import os
from collections.abc import Collection, Sequence
from typing import Final, ClassVar

PATH_SEPARATOR: Final = "/" if os.sep == '/' or os.altsep == '/' else os.sep
PATH_PARENT: Final = os.pardir

PathLike = str | os.PathLike

class UPath():
	"""
		A normalised abstract file path with no dependency on the layout of the local filesystem or, if different, the source filesystem that generated the path representation.

		The path can be manipulated before being rendered in a format that is meaningful to the local operating system.

		Instance attributes
		-------------------
		- `parts: list[str]`
		   decomposed parts of a path relative to either an anonymous parent directory (e.g. '../..', represented by `dotdot`) or to a filesystem root (represented by `root`), without separats in each part
		- `device: str`
		   device name of the path (e.g. drive letter on Windows), or an empty string if no device is associated with the path (e.g. Linux file paths); usually empty when `root` is False
		- `root: bool`
		   whether the path is relative to the filesystem root; should only be True when `dotdot` is 0
		- `dotdot: int`
		   number of levels of parent directories that the path is relative to (i.e. number of '..'s in the path); should only be non-zero when `root` is False; may be 0 even if `root` is False, indicating a path relative to an abstract current directory

		Class attributes
		----------------
		- `separator: str`
		   path separator that is meaningful to the local operating system
		- `parent: str`
		   path component indicating a parent directory that is meaningful to the local operating system; usually ".."
	"""

	__slots__ = ('parts', 'device', 'root', 'dotdot')

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
		self.parts: list[str] = []  # root- or dotdot- relative path
		self.device: str = ''
		self.root: bool = False
		self.dotdot: int = 0
		if path is not None and path != '':
			if isinstance(path, UPath):
				path._validate()
				self.parts = path.parts
				self.device = path.device
				self.root = path.root
				self.dotdot = path.dotdot
			else:
				# Remove redundant '.'s and '..'s and use OS-default path separators
				path = os.path.normpath(path)  # sets empty path to '.' and removes trailing slash

				if path == '.':
					path = ''
				(self.device, path) = os.path.splitdrive(path)
				self.root = os.path.isabs(path)

				parts = path.split(os.sep)  # os.path.normpath previously rewrote the path to use os.sep
				if parts[0] == '':  # First element is '' if root
					parts = parts[1:]
				if parts[-1] == '':  # Last element is '' if there is a trailing slash, which should only happen when the path is exactly root ('/')
					parts = parts[:-1]

				dotdot = 0
				while parts[dotdot] == UPath.parent:  # UPath.parent == '..' usually
					dotdot += 1
				self.parts = parts[dotdot:]
				self.dotdot = dotdot

	@staticmethod
	def common(path1: UPathLike, path2: UPathLike) -> UPath | None:
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

		if path1.device != path2.device:
			return None
		if path1.root != path2.root:
			return None

		if path1.root:
			common_path = UPath()
			for part1, part2 in zip(path1.parts, path2.parts):
				if part1 == part2:
					common_path.parts.append(part1)
			common_path.root = True
			common_path.device = path1.device
			# dotdot must be 0
		else:
			if path1.dotdot != path2.dotdot:
				return None
			common_path = UPath()
			for part1, part2 in zip(path1.parts, path2.parts):
				if part1 == part2:
					common_path.parts.append(part1)
			common_path.dotdot = path1.dotdot

		return common_path

	@staticmethod
	def partitions(paths: Collection[UPathLike]) -> dict[UPath, set[UPath]]:
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
				candidate_common = UPath.common(partition, path)
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
	def joinstr(paths: Sequence[UPathLike], delim: str="") -> str:
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

			Returns
			-------
			  `List[str]`
			   list of components of the path

			Raises
			------
				`ValueError`
				if `self` is in an invalid state
		"""
		self._validate()
		base_parts = []
		if self.root:
			base_parts = [self.device]
		elif self.dotdot > 0:
			base_parts = [UPath.parent for i in range(self.dotdot)]
		return base_parts + self.parts

	def get_relative_parts(self) -> list[str]:
		"""
			Get a list of strings representing each relative component of the abstract file path.

			The returned list will always represent a relative path, with no information about whether the path was relative to any filesystem root.

			To get a list including the filesystem root, use `get_parts()` instead.

			If the path is relative to an ancestor directory (e.g. '../..'), each parent level will be given as a separate item in the returned list.

			To get a list without information about any ancestor directory as well, use `get_name_parts()` instead.

			Returns
			-------
			  `List[str]`
			   list of relative components of the path

			Raises
			------
				`ValueError`
				if `self` is in an invalid state
		"""
		self._validate()
		base_parts = []
		if self.dotdot > 0:
			base_parts = [UPath.parent for i in range(self.dotdot)]
		return base_parts + self.parts

	def get_named_parts(self) -> list[str]:
		"""
			Get a list of strings representing each named component of the abstract file path.

			The returned list will always represent a descendent relative path, with no information about whether the path was relative to any filesystem root or to any ancestor directories.

			To get a list of parts with more information, use `get_parts()` or `get_relative_parts()` instead.

			Returns
			-------
			  `List[str]`
			   list of named components of the path
		"""
		return self.parts

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

		common_path = UPath.common(self, base)
		if common_path is not None and common_path == base:
			base_length = len(base.parts)
			new_path = UPath()
			new_path.parts = self.parts[base_length:]  # [] when self == base
			return new_path
		else:
			return None

	def __add__(self, other: UPathLike) -> UPath | None:
		"""
			Add a relative UPath to `self` and return the new UPath. Return `None` if `other` is not a relative path, or if `other` and `self` have different `device`.

			Evoked by `upath1 + upath2`

			Raises `ValueError` if `other` is an invalid UPath
		"""
		other = UPath(other)

		if other.root:
			return None
		elif other.device != '' and self.device != other.device:
			return None
		else:
			new_path = UPath(self)
			new_parts = [part for part in self.parts]
			for i in range(other.dotdot):
				if len(new_parts) > 0:
					new_parts.pop()
				elif not new_path.root:
					new_path.dotdot += 1
				else:
					pass  # parent of directory of root is still root

			new_parts.extend(other.parts)
			new_path.parts = new_parts
			return new_path

	def __bool__(self) -> bool:
		"""
			Return True if `self` is relative to root or an ancestor directory, or if `self` has at least one named component; return False otherwise.

			Evoke as `bool(myupath)`

			Raises `ValueError` if `self` is an invalid UPath
		"""
		self._validate()
		return self.root or self.dotdot != 0 or len(self.parts) > 0

	def __str__(self) -> str:
		"""
			Return a string representation of the abstract file path that is meaningful to the local operating system.

			Evoke as `str(myrange)`

			Raises `ValueError` if `self` is an invalid UPath
		"""
		return UPath.separator.join(self.get_parts())

	def __repr__(self) -> str:
		"""
			Return a string that can be printed as a source code representation of the abstract file path.

			Evoke as `repr(myrange)`

			Raises `ValueError` if `self` is an invalid UPath
		"""
		return f"UPath({repr(str(self))})"

	def __eq__(self, other: Any) -> bool:
		"""
			Check if two abstract file paths are completely identical. Always return False if `other` is not a UPath object.

			Evoke as `myrange == other`

			Raises `ValueError` if either UPath is invalid
		"""
		if type(other) is UPath:
			return self.__dict__ == other.__dict__
		else:
			return False

	def _validate(self) -> bool:
		# Check if self is in a valid state
		if self.dotdot < 0:
			raise ValueError(f"invalid UPath, dotdot cannot be negative: {repr(self)}")
		if self.root:
			if self.dotdot != 0:
				raise ValueError(f"invalid UPath, dotdot must be 0 when root is True: {repr(self)}")
		return True

UPathLike = UPath | PathLike
