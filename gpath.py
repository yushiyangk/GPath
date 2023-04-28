"""
	GPath is a robust, generalised abstract file path that provides functions for common path manipulations independent from the local operating system.
"""

from __future__ import annotations

import functools
import os
import sys
from collections.abc import Collection, Iterator, Sequence
#from typing import Any, ClassVar, Final


# Type hinting prior to 3.10
# Using generics in built-in collections, e.g. list[int], is supported from 3.7 by __future__.annotations
from typing import Any, ClassVar, Optional, Union
if sys.version_info >= (3, 8):
	from typing import Final
else:
	Final = Any
def is_gpathlike(obj: Any) -> bool:
	if sys.version_info >= (3, 10):
		return isinstance(obj, GPathLike)
	else:
		return isinstance(obj, GPath) or isinstance(obj, str) or isinstance(obj, os.PathLike)


__version__ = '0.2'


PATH_SEPARATOR: Final = "/" if os.sep == '/' or os.altsep == '/' else os.sep
PATH_CURRENT: Final = os.curdir
PATH_PARENT: Final = os.pardir

PathLike = Union[str, os.PathLike]


@functools.total_ordering
class GPath():
	"""
		A normalised and generalised abstract file path that has no dependency on the layout of any real filesystem. This allows us to manipulate file paths that were generated on a different system, particularly one with a different operating environment as compared to the local system.

		The path can be manipulated before being rendered in a format that is meaningful to the local operating system.

		Class attributes
		----------------
		- `separator: str`
		   path separator recognised by the local operating system
		- `parent: str`
		   path component that indicates a parent directory recognised by the local operating system; usually ".."
	"""

	__slots__ = ('_parts', '_device', '_root', '_dotdot')

	separator: ClassVar = PATH_SEPARATOR
	current: ClassVar = PATH_CURRENT
	parent: ClassVar = PATH_PARENT


	def __init__(self, path: Union[PathLike, GPath, None]="") -> None:
		"""
			Initialise a normalised and generalised abstract file path, possibly by copying an existing GPath object.

			Evoked by `GPath(path)`

			Parameters
			----------
			- `path: PathLike | GPath | None`
			   path-like object representing a (unnormalised) file path, or a GPath object to be copied

			Raises
			------
				`ValueError`
				if `other` is an invalid GPath
		"""
		self._parts: tuple[str, ...] = tuple()  # root- or dotdot- relative path
		self._device: str = ""
		self._root: bool = False
		self._dotdot: int = 0
		if path is not None and path != "":
			if isinstance(path, GPath):
				path._validate()
				self._parts = path._parts
				self._device = path._device
				self._root = path._root
				self._dotdot = path._dotdot
			else:
				# Remove redundant '.'s and '..'s and use OS-default path separators
				path = os.path.normpath(path)  # sets empty path to '.' and removes trailing slash

				if path == os.curdir:
					path = ""
				(self._device, path) = os.path.splitdrive(path)
				self._root = os.path.isabs(path)

				parts = path.split(os.sep)  # os.path.normpath previously rewrote the path to use os.sep
				if len(parts) > 0 and parts[0] == "":  # First element is '' if root
					parts = parts[1:]
				if len(parts) > 0 and parts[-1] == "":  # Last element is '' if there is a trailing slash, which should only happen when the path is exactly root ('/')
					parts = parts[:-1]

				dotdot = 0
				while dotdot < len(parts) and parts[dotdot] == GPath.parent:  # GPath.parent == '..' usually
					dotdot += 1
				self._parts = tuple(parts[dotdot:])
				self._dotdot = dotdot


	@staticmethod
	def from_parts(parts: Sequence[str]) -> GPath:
		"""
			Static method. Create a GPath object from a sequence of path components, such as that generated by `get_parts()`.

			Note that unlike `GPath.join()`, this method expects each item in the sequence to be a single string without any file separators. Absolute paths are represented in the same manner as returned by `get_parts()`.
		"""
		return GPath(GPath.separator.join(parts))


	@staticmethod
	def find_common(path1: GPathLike, path2: GPathLike, common_current: bool=True, common_parent: bool=False) -> Optional[GPath]:
		"""
			Static method. Find the longest common base path shared by the two paths. Return None if the two paths do not share any base components, such as if they are not both relative paths or both absolute paths, or if they are rooted on different device names.

			By default, two non-parent relative paths that do not share any named components are still considered to share a common base path, namely the imaginary current working directory (e.g. `GPath("some/rel/path")` and `GPath("another/rel/path")` will give `GPath("")` by default). To prevent this, set `common_current` to False, and None will be returned instead.

			By default, two relative paths that are relative to different levels of parent directories are considered to not have a common base path, and will return None. To prevent this, set `common_parent` to True in order to return the highest level parent directory between the two paths (e.g. `("../relative/to/parent")` and `GPath("../../relative/to/grandparent")` will give `GPath("../..")` if `common_parent` is True). Note that `common_parent` implies `common_current`.

			Parameters
			----------
			  `path1: GPath | str | os.PathLike`, `path2: GPath | str | os.PathLike`
			   the paths to compare
			  `common_current: bool=True`
			   whether non-parent relative paths with no shared components should be considered to have a common base path; True by default
			  `common_parent: bool=False`
			   whether paths that are relative to different levels of parent directories should be considered to have a common base path; False by default

			Returns
			-------
			- `GPath`
			   longest common base path, which may be empty, if it exists based on the `common_current` and `common_parent` options
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

		if common_parent:
			common_current = True

		parts = []
		if path1._root:
			common_path = GPath()
			for part1, part2 in zip(path1._parts, path2._parts):
				if part1 == part2:
					parts.append(part1)
			common_path._root = True
			# dotdot must be 0
		else:
			if path1._dotdot != path2._dotdot:
				if not common_parent:
					return None

				common_path = GPath()
				common_path._dotdot = max(path1._dotdot, path2._dotdot)
			else:
				common_path = GPath()
				common_path._dotdot = path1._dotdot
				for part1, part2 in zip(path1._parts, path2._parts):
					if part1 == part2:
						parts.append(part1)

		common_path._device = path1._device
		common_path._parts = tuple(parts)

		if not common_current and not bool(common_path):
			if common_path != path1 or common_path != path2:
				return None
		return common_path


	@staticmethod
	def partition(*paths: Union[Collection[GPathLike], GPathLike], **find_common_kwargs: bool) -> dict[GPath, list[GPath]]:
		"""
			Static method. Partition a collection of paths based on the common base paths shared between members of the collection, such that each path can only belong to one partition. Return a list of relative paths from the common base path in each partition.

			The partitioning logic is similar to that of `GPath.common()`; by default, non-parent relative paths are always placed in the same partition, while paths that are relative to different levels of parent directories will be placed in separate partitions.

			Note that `common_parent` should only be set to True if the members of each partition are not of interest. When `common_parent` is True, the output lists will all be explicitly empty, because it is not possible to obtain a relative path from a parent directory of a higher level to one of a lower level. In most cases, this option should not be used.

			Evoked by either `GPath.partition([gpath1, gpath2, ...])` or `GPath.partition(gpath1, gpath2, ...)`

			Parameters
			----------
			   `paths: Collection[GPath | str | os.PathLike]` or `*paths: GPath | str | os.PathLike`
			   the paths to be partitioned, which can be given as either a list-like object or as variadic arguments
			   `common_current: bool=True` (in `**find_common_kwargs`)
			   whether non-parent  relative paths with no shared components should be considered to have a common base path (see `GPath.common()`); True by default
			   `common_parent: bool=False` (in `**find_common_kwargs`)
			   whether paths that are relative to different levels of parent directories should be considered to have a common base path (see `GPath.common()`); False by default

			Returns
			-------
			  `dict[GPath, set[GPath]]`
			   dictionary that maps the common base path of each partition to a set of paths that belong to that partition

			Raises
			------
			  `ValueError`
			  if any of the GPaths are invalid
		"""
		flattened_paths: list[GPathLike] = []
		for path_or_list in paths:
			if is_gpathlike(path_or_list):
				flattened_paths.append(path_or_list)
			else:
				flattened_paths.extend(path_or_list)
		gpaths = [path if isinstance(path, GPath) else GPath(path) for path in flattened_paths]

		partition_map = {}
		if len(gpaths) > 0:
			if 'common_parent' in find_common_kwargs and find_common_kwargs['common_parent'] == True:
				partition_map[gpaths[0]] = []
			else:
				partition_map[gpaths[0]] = [gpaths[0]]

		for path in gpaths[1:]:
			partition_found = False
			for partition in partition_map:
				candidate_common = GPath.find_common(partition, path, **find_common_kwargs)
				if candidate_common is not None:
					partition_found = True
					if candidate_common != partition:
						partition_map[candidate_common] = partition_map[partition]
						del partition_map[partition]
					if 'common_parent' not in find_common_kwargs or find_common_kwargs['common_parent'] == False:
						partition_map[candidate_common].append(path)
					break
			if not partition_found:
				if 'common_parent' in find_common_kwargs and find_common_kwargs['common_parent'] == True:
					partition_map[path] = []
				else:
					partition_map[path] = [path]

		for partition, path_list in partition_map.items():
			partition_map[partition] = [path.subpath_from(partition) for path in path_list]

		return partition_map


	@staticmethod
	def join(*paths: Union[Collection[GPathLike], GPathLike]) -> GPath:
		"""
			Join a sequence of paths into a single path. Apart from the first item in the sequence, all subsequent paths should be relative paths and any absolute paths will be ignored.

			Evoked by either `GPath.join([gpath1, gpath2, ...])` or `GPath.join(gpath1, gpath2, ...)`

			Parameters
			----------
			   `paths: Collection[GPath | str | os.PathLike]` or `*paths: GPath | str | os.PathLike`
			   the paths to be combined, which can be given as either a list-like object or as variadic arguments

			Returns
			-------
			  `GPath`
			   the combined path

			Raises
			------
			  `ValueError`
			  if any of the GPaths are invalid
		"""
		flattened_paths: list[GPathLike] = []
		for path_or_list in paths:
			if is_gpathlike(path_or_list):
				flattened_paths.append(path_or_list)
			else:
				flattened_paths.extend(path_or_list)

		if len(flattened_paths) == 0:
			return GPath()

		combined_path = flattened_paths[0]
		if not isinstance(combined_path, GPath):
			combined_path = GPath(combined_path)
		for path in flattened_paths[1:]:
			combined_path = combined_path + path

		return combined_path


	def get_parts(self, root: bool=True, parent: bool=True) -> list[str]:
		"""
			Get a list of strings representing each component of the path.

			By default, components representing the full path is returned in such a way that it can be reconstructed as a string using `GPath.separator.join(mygpath.get_parts())`. If it is an absolute path, the first item of the returned list will contain the device name if it exists, or be an empty string otherwise. If the path is exactly the filesystem root, the returned list will contain exactly two items, with the second being an empty string.

			If the path is relative to an parent directory (e.g. '../..'), each parent level will be given as a separate item in the returned list.

			To get a relative path without any components that indicate the filesystem root or device name, set `root` to False.

			To get a non-parent relative path without any components that indicate parent directories, set `parent` to False.

			Parameters
			----------
			   `root: bool=True`
			   whether to return components that indicate the filesystem root or device name; True by default
			   `parent: bool=True`
			   whether to return components that indicate parent directories; True by default

			Returns
			-------
			  `list[str]`
			   list of path components
		"""
		if root and self._root:
			if len(self._parts) == 0:
				return [self._device, ""]

			base_parts = [self._device]

		elif parent and self._dotdot > 0:
			base_parts = self.get_parent_parts()

		else:
			if len(self._parts) == 0:
				# bool(self) == False
				return [GPath.current]

			base_parts = []

		return base_parts + list(self._parts)


	def get_parent_parts(self) -> list[str]:
		"""
			Get a list of strings representing the parent directory that the path is relative to, if any.

			The returned list will contain a copy of `GPath.parent` for each parent level. If the path is not relative to a parent directory, the returned list will be empty.
		"""
		return [GPath.parent for i in range(self._dotdot)]

	def get_parent_level(self) -> int:
		"""
			Get the number of levels of parent directories that the path is relative to, if any.
		"""
		return self._dotdot

	def get_device(self) -> Optional[str]:
		"""
			Get the device name of the path.
		"""
		return self._device

	def is_root(self) -> bool:
		"""
			Check if the path is relative to filesystem root
		"""
		return self._root


	def subpath_from(self, base: GPathLike) -> Optional[GPath]:
		"""
			Find the relative subpath from `base` to `self` if possible and if `base` contains `self`, or return None otherwise.

			None will be returned if there are components with names that cannot be known in the subpath, for instance when `self` and `base` base are relative paths with `base` being relative to a parent directory of a higher level than `self`.

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
				if either `self` or `base` is an invalid GPath
		"""
		if not isinstance(base, GPath):
			base = GPath(base)

		if GPath.find_common(self, base, common_current=True, common_parent=False) is not None and self in base:
			# If self._dotdot > base._dotdot, self is not in base, whereas if self._dotdot < base._dotdot, path from base to self's parent cannot be known
			base_length = len(base._parts)
			new_path = GPath()
			new_path._parts = self._parts[base_length:]  # () when self == base
			return new_path
		else:
			return None


	def relpath_from(self, origin: GPathLike) -> Optional[GPath]:
		"""
			Find the relative path from `origin` to `self` if possible, or return None otherwise.

			None will be returned if there are components with names that cannot be known in the relative path, for instance when `self` is a relative path while `origin` is an absolute path or a path that is relative to a parent directory of a higher level than `self`.

			Parameters
			----------
			- `origin: GPath | str | os.PathLike`
			   the origin path against which `self` is compared

			Returns
			-------
			- `GPath`
			   relative path from `origin` to `self`, which may be empty, if possible
			- `None`
			   otherwise

			Raises
			------
				`ValueError`
				if either `self` or `origin` is an invalid GPath
		"""
		self._validate()
		if not isinstance(origin, GPath):
			origin = GPath(origin)

		if origin._root:
			common = GPath.find_common(self, origin)
			if common is None:
				return None

			new_path = GPath()
			new_path._dotdot = len(origin) - len(common)
			new_path._parts = self._parts[len(common):]
			return new_path

		else:
			common = GPath.find_common(self, origin, common_current=True, common_parent=True)
			if common is None:
				return None
			if common._dotdot > self._dotdot:
				return None  # Path from common to self's parent cannot be known

			# common._dotdot == self._dotdot
			# origin._dotdot <= self._dotdot

			new_path = GPath()
			if len(common) == 0:
				if origin._dotdot == self._dotdot:
					new_path._dotdot = len(origin)
				else:
					new_path._dotdot = (common._dotdot - origin._dotdot) + len(origin)
				new_path._parts = self._parts
			else:
				new_path._dotdot = len(origin) - len(common)
				new_path._parts = self._parts[len(common):]

			return new_path


	def __hash__(self) -> int:
		"""
			Calculate hash of the GPath object.

			Evoked by `hash(mygpath)`
		"""
		return hash((tuple(self._parts), self._device, self._root, self._dotdot))


	def __eq__(self, other: Any) -> bool:
		"""
			Check if two GPaths are completely identical. Always return False if `other` is not a GPath object, even if it is a GPath-like object.

			Evoked by `gpath1 == gpath2`
		"""
		if isinstance(other, GPath):
			return ((self._root, self._device, self._dotdot) + self._parts) == ((other._root, other._device, other._dotdot) + other._parts)
		else:
			return False


	def __gt__(self, other: GPathLike) -> bool:
		"""
			Check if `self` should be collated after `other` by comparing their component-wise lexicographical order. Absolute paths come before (is less than) parent relative paths, which come before (is less than) non-parent relative paths. Between two parent relative paths, the path with the higher parent level is considered greater (comes later).

			Evoked by `gpath1 < gpath2`
		"""
		if not isinstance(other, GPath):
			other = GPath(other)
		return ((not self._root, self._device, -1 * self._dotdot) + self._parts) > ((not other._root, other._device, -1 * other._dotdot) + other._parts)


	def __bool__(self) -> bool:
		"""
			Return True if `self` is an absolute path, if `self` is relative to a parent directory, or if `self` has at least one named component; return False otherwise.

			Evoked by `bool(mygpath)`
		"""
		return self._root or self._dotdot != 0 or len(self._parts) > 0


	def __str__(self) -> str:
		"""
			Return a string representation of the path that is meaningful to the local operating system.

			Evoked by `str(mygpath)`
		"""
		return GPath.separator.join(self.get_parts())


	def __repr__(self) -> str:
		"""
			Return a string that can be printed as a source code representation of the GPath object.

			Evoked by `repr(mygpath)`
		"""
		if bool(self):
			return f"GPath({repr(str(self))})"
		else:
			return f"GPath({repr('')})"


	def __len__(self) -> int:
		"""
			Get the number of relative path components, excluding any device name or parent directories.

			Evoked by `len(mygpath)`
		"""
		return len(self._parts)


	def __getitem__(self, index: Union[int, slice]) -> Union[str, list[str]]:
		"""
			Get a 0-indexed relative path component, or a slice of path components, excluding any device name or parent directories.

			Evoked by `mygpath[n]`, `mygpath[start:end]`, `mygpath[start:end:step]`, etc.
		"""
		if isinstance(index, int):
			return self._parts[index]
		elif isinstance(index, slice):
			return list(self._parts[index])


	def __iter__(self) -> Iterator[str]:
		"""
			Get an iterator through the relative path components, excluding any device name or parent directories.

			Evoked by `iter(mygpath)`
		"""
		return iter(self._parts)


	def __contains__(self, other: GPathLike) -> bool:
		"""
			Check if the path represented by `self` contains the path represented by `other`; i.e. check if `self` is a parent directory of `other`.

			Evoked by `other in mygpath`

			Raises `ValueError` if either GPath is invalid
		"""
		if not isinstance(other, GPath):
			other = GPath(other)

		common_path = GPath.find_common(self, other, common_current=True, common_parent=True)
		return common_path is not None and common_path == self


	def __add__(self, other: GPathLike) -> GPath:
		"""
			Add (append) `other` to the end of `self` if `other` is a relative path, and return a new copy. If `other` is an absolute path, or if `other` has a different device name, add nothing and return a copy of `self`.

			Evoked by `gpath1 + gpath2`

			Raises `ValueError` if either GPath is invalid
		"""
		if isinstance(other, GPath):
			other._validate
		else:
			other = GPath(other)

		if other._root:
			return GPath(self)
		elif other._device != None and other._device != "" and self._device != other._device:
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

			Raises `ValueError` if `self` is an invalid GPath or if `n` is negative
		"""
		if n < 0:
			raise ValueError("cannot subtract a negative number of components from the path; use __add__() instead")

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
			Duplicate the relative components of `self` `n` times and return a new path with the duplicated components instead. Named components will be duplicated separately from the components representing a parent directory. If it is an absolute path, only the relative components will be duplicated.

			If `n` is 0, the result should be an empty path (relative or absolute).

			Evoked by `mygpath * n`

			Raises `ValueError` if `self` is an invalid GPath or if `n` is negative.
		"""
		if n < 0:
			raise ValueError("cannot multiply path by a negative integer")
		new_path = GPath(self)
		new_path._dotdot = self._dotdot * n
		new_path._parts = self._parts * n
		return new_path


	def __lshift__(self, n: int) -> GPath:
		"""
			Move the imaginary current working directory `n` steps up the filesystem tree. If it is a relative path, remove up to `n` levels of parent directories from the start of the path and return a copy. If it is an absolute path, return a copy of `self` unchanged.

			If `n` is negative, the behaviour of `__rshift__(-n)` will be used instead.

			Evoked by `mygpath << n`

			Raises `ValueError` if `self` is an invalid GPath.
		"""
		if n < 0:
			return self.__rshift__(-1 * n)
		new_path = GPath(self)
		if not new_path._root:
			new_path._dotdot = max(new_path._dotdot - n, 0)
		return new_path


	def __rshift__(self, n: int) -> GPath:
		"""
			Move the imaginary current working directory `n` steps down the filesystem tree. If it is a relative path, add `n` levels of parent directories to the start of the path and return a copy. If it is an absolute path, return a copy of `self` unchanged.

			If `n` is negative, the behaviour of `__lshift__(-n)` will be used instead.

			Evoked by `mygpath >> n`

			Raises `ValueError` if `self` is an invalid GPath
		"""
		if n < 0:
			return self.__lshift__(-1 * n)
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


GPathLike = Union[GPath, PathLike]
