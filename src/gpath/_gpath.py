"""
	GPath is a robust, generalised abstract file path that provides path manipulations independent from the local environment, maximising cross-platform compatibility.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Collection, Hashable, Iterator, Iterable, Sequence, Sized
from typing import Any, overload

from . import _rules


from ._compat import Final, Optional, Union


__all__ = ('GPath', 'GPathLike')


if sys.version_info >= (3, 10):
	def _is_gpathlike(obj: Any) -> bool:
		return isinstance(obj, GPathLike)
else:
	def _is_gpathlike(obj: Any) -> bool:
		return isinstance(obj, GPath) or isinstance(obj, str) or isinstance(obj, bytes) or isinstance(obj, os.PathLike)


DEFAULT_ENCODING: Final = 'utf_8'


def _split_relative(
	path: str,
	delimiters: Union[str, Collection[str]],
	collapse: bool=True
) -> list[str]:
	if path == "":
		return [path]

	if delimiters == "" or len(delimiters) == 0:
		return [path]

	if isinstance(delimiters, Iterable):
		delimiter_iter = iter(delimiters)
		delimiter = next(delimiter_iter)
		for d in delimiter_iter:
			path = path.replace(d, delimiter)

	if collapse:
		# Assumes len(delimiter) == 1
		new_path = delimiter
		for c in path:
			if c == delimiter and new_path[-1] == delimiter:
				pass
			else:
				new_path += c
		path = new_path[1:]

	return path.split(delimiter)


def _normalise_relative(
	parts: Sequence[str],
	current_dirs: Collection[str]=_rules.COMMON_CURRENT_INDICATOR,
	parent_dirs: Collection[str]=_rules.COMMON_PARENT_INDICATOR,
):
	output = []
	for part in parts:
		if part == "":
			pass
		elif part == current_dirs:
			pass
		elif part == parent_dirs:
			if len(output) > 0 and output[-1] != parent_dirs:
				output.pop()
			else:
				output.append(part)
		else:
			output.append(part)
	return output


class GPath(Hashable, Sized, Iterable):
	"""
		An immutable generalised abstract file path that has no dependency on any real filesystem.

		The path can be manipulated on a system that is different from where it originated, notably including systems with a different operating system, and it can represent file paths on a system other than local. Examples where this is useful include remote management of servers and when cross-compiling source code for a different platform.

		Since GPath objects are immutable, all operations return a new instance. The path is always stored in a normalised state, and is always treated as case sensitive.

		The path can be rendered as a string using <code>str(<var>g</var>)</code>, which will use `/` as the path separator if possible to maximise cross-platform compatibility.
	"""

	__slots__ = (
		'_parts',
		'_root',
		'_drive',
		'_parent_level',
		'_encoding',
	)


	def __init__(self, path: Union[str, bytes, os.PathLike, GPath, None]="", encoding: Optional[str]=None):
		"""
			Initialise a normalised and generalised abstract file path, possibly by copying an existing GPath object.

			Parameters
			----------
			`path`
			: path-like object representing a (possibly unnormalised) file path, or a GPath object to be copied

			`​encoding`
			: the text encoding that should be used to decode paths given as bytes-like objects; if not specified, `'utf_8'` will be used by default. The name should be one of the standard Python text encodings, as listed in the `codecs` module of the standard library. The specified encoding will propagate to new GPaths that result from operations on this GPath. If a binary operation involves two GPaths, the encoding specified by the left operand will be propagated to the result.

			Raises
			------
			`ValueError` if `other` is an invalid GPath

			Examples
			--------
			```python
			GPath("/")
			GPath("/usr/bin")
			GPath("C:/Program Files")
			```
		"""

		self._parts: tuple[str, ...] = tuple()  # root- or parent- relative path
		self._root: bool = False
		self._drive: str = ""
		self._parent_level: int = 0

		self._encoding: Optional[str] = encoding

		if path is None or path == "":
			return

		if isinstance(path, GPath):
			path._validate()
			self._parts = path._parts
			self._root = path._root
			self._drive = path._drive
			self._parent_level = path._parent_level

			self._encoding = path._encoding if encoding is None else encoding
			return

		path = os.fspath(path)

		if isinstance(path, bytes):
			if self._encoding is None:
				path = path.decode(DEFAULT_ENCODING)
			else:
				path = path.decode(self._encoding)

		# path is a str

		if len(path) >= 2 and path[1] in _rules.generic_rules.drive_postfixes:
			self._drive = path[0]
			driveless_path = path[2:]
		else:
			driveless_path = path

		for root in _rules.generic_rules.roots:
			if driveless_path.startswith(root):
				self._root = True
				break

		if self._root:
			rootless_path = driveless_path[1:]
		else:
			rootless_path = driveless_path


		parts = _split_relative(rootless_path, delimiters=(set(_rules.generic_rules.separators) | set(_rules.generic_rules.separators)))
		parts = _normalise_relative(parts)
		parent_level = 0
		while parent_level < len(parts) and parts[parent_level] in _rules.generic_rules.parent_indicators:
			parent_level += 1
		self._parts = tuple(parts[parent_level:])
		if self._root == False:
			self._parent_level = parent_level


	@property
	def named_parts(self) -> list[str]:
		"""
			Read-only named components of the path, not including the filesystem root, drive name, or any parent directories

			Examples
			--------
			```python
			GPath("usr/local/bin").named_parts     # ["usr", "local", "bin"]
			GPath("../../Documents").named_parts   # ["Documents"]
			GPath("/usr/bin").named_parts          # ["usr", "bin"]
			GPath("C:/Program Files").named_parts  # ["Program Files"]
			```
		"""
		return list(self._parts)

	@property
	def parent_level(self) -> int:
		"""
			Read-only number of levels of parent directories that the path is relative to, which may be 0

			Examples
			--------
			```python
			GPath("../../Documents").parent_level  # 2
			GPath("usr/local/bin").parent_level    # 0
			```
		"""
		return self._parent_level

	@property
	def parent_parts(self) -> list[str]:
		"""
			Read-only path components representing a parent directory that it is relative to, if any, with one item for each level of parent directory

			Examples
			--------
			```python
			GPath("../../Documents").parent_parts  # ["..", ".."]
			GPath("usr/local/bin").parent_parts    # []
			```
		"""
		return [_rules.generic_rules.parent_indicators[0] for i in range(self._parent_level)]

	@property
	def relative_parts(self) -> list[str]:
		"""
			Read-only relative components of the path, not including the filesystem root or drive name, including one item for each level of parent directory

			Examples
			--------
			```python
			GPath("usr/local/bin").relative_parts     # ["usr", "local", "bin"]
			GPath("../../Documents").relative_parts   # ["..", "..", "Documents"]
			GPath("/usr/bin").relative_parts          # ["usr", "bin"]
			GPath("C:/Program Files").relative_parts  # ["Program Files"]
			```
		"""
		return self.parent_parts + list(self._parts)

	@property
	def drive(self) -> str:
		"""
			Read-only drive name

			Examples
			--------
			```python
			GPath("C:/Windows").drive       # "C:"
			GPath("/usr/bin").drive         # ""
			GPath("../../Documents").drive  # ""
			```
		"""
		return self._drive

	@property
	def absolute(self) -> bool:
		"""
			Read-only flag for whether the path is an absolute path

			Examples
			--------
			```python
			GPath("/").absolute                # True
			GPath("C:/Windows").absolute       # True
			GPath("local/bin").absolute        # False
			GPath("../../Documents").absolute  # False
			```
		"""
		return self._root

	@property
	def root(self) -> bool:
		"""
			Read-only flag for whether the path is exactly the root of the filesystem

			Examples
			--------
			```python
			GPath("/").root                # True
			GPath("C:/").root              # True
			GPath("/usr/bin").root         # False
			GPath("C:/Windows").root       # False
			GPath("../../Documents").root  # False
			```
		"""
		return self._root and len(self._parts) == 0

	@property
	def encoding(self) -> Union[str, None]:
		"""
			Read-only encoding used to decode other paths that are given as bytes-like objects, or None if the default should be used
		"""
		return self._encoding


	#@overload
	#@staticmethod
	#def partition(paths: Iterable[GPathLike], /, *, allow_current, allow_parents, encoding) -> dict[GPath, list[GPath]]:
	#	...
	#@overload
	#@staticmethod
	#def partition(*paths: GPathLike, allow_current, allow_parents, encoding) -> dict[GPath, list[GPath]]:
	#	...
	@staticmethod
	def partition(*paths, allow_current: bool=True, allow_parents: bool=True, encoding: Optional[str]=None) -> dict[GPath, list[GPath]]:
		"""
			Partition a collection of paths based on shared common base paths such that each path belongs to one partition.

			For each partition, return a list of relative paths from the base path of that partition to each corresponding input path within that partition, unless `allow_parents` is True (see below). If the input collection is ordered, the output order is preserved within each partition. If the input collection contains duplicates, the corresponding output lists will as well.

			The number of partitions is minimised by merging partitions as much as possible, so that each partition represents the highest possible level base path. Two partitions can no longer be merged when there is no common base path between them, as determined by `common_with()`. This method takes the same optional arguments as `common_with()`, with the same default values.

			Parameters
			----------
			`paths: Iterable[GPath | str | bytes | os.PathLike]` or `*paths: GPath | str | bytes | os.PathLike`
			: the paths to be partitioned, which can be given as either a list-like object or as variadic arguments

			`allow_current`
			: whether non-parent relative paths with no shared components should be considered to have a common base path (see `common_with()`)

			`allow_parents`
			: whether paths that are relative to different levels of parent directories should be considered to have a common base path (see `common_with()`). **Warning**: when set to True, the output lists for each partition are invalidated, and explicitly set to empty. This is because it is not possible in general to obtain a relative path from the base path to its members if the base path is a parent directory of a higher level than the member (see `relpath_from()`). This  option should be True if and only if the list of members in each partition are not of interest; in most cases False is more appropriate.

			`​encoding`
			: the text encoding that should be used to decode bytes-like objects in `paths`, if any (see `__init__()`).

			Returns
			-------
			a dictionary that maps the common base path of each partition to a list of relative paths

			Raises
			------
			  `ValueError`
			  if any of the GPaths are invalid

			Examples
			--------
			```python
			GPath.partition("/usr/bin", "/usr/local/bin", "../../doc", "C:/Windows", "C:/Program Files")

			assert partitions == {
				GPath("/usr")      : [GPath("bin"), GPath("local")],
				GPath("../../doc") : [GPath("")],
				GPath("C:/")       : [GPath("Windows"), GPath("Program Files")],
			}
			```
		"""
		flattened_paths: list[GPathLike] = []
		for path_or_list in paths:
			if _is_gpathlike(path_or_list):
				flattened_paths.append(path_or_list)
			else:
				flattened_paths.extend(path_or_list)
		gpaths = [path if isinstance(path, GPath) else GPath(path, encoding=encoding) for path in flattened_paths]

		partition_map = {}
		if len(gpaths) > 0:
			if allow_parents == True:
				partition_map[gpaths[0]] = []
			else:
				partition_map[gpaths[0]] = [gpaths[0]]

		for path in gpaths[1:]:
			partition_found = False
			for partition in partition_map:
				candidate_common = partition.common_with(path, allow_current=allow_current, allow_parents=allow_parents)
				if candidate_common is not None:
					partition_found = True
					if candidate_common != partition:
						partition_map[candidate_common] = partition_map[partition]
						del partition_map[partition]
					if allow_parents == False:
						partition_map[candidate_common].append(path)
					break
			if not partition_found:
				if allow_parents == True:
					partition_map[path] = []
				else:
					partition_map[path] = [path]

		for partition, path_list in partition_map.items():
			partition_map[partition] = [path.subpath_from(partition) for path in path_list]

		return partition_map


	#@overload
	#@staticmethod
	#def join(paths: Iterable[GPathLike], /, *, encoding) -> GPath:
	#	...
	#@overload
	#@staticmethod
	#def join(*paths: GPathLike, encoding) -> GPath:
	#	...
	@staticmethod
	def join(*paths, encoding: Optional[str]=None) -> GPath:
		"""
			Join a sequence of paths into a single path. Apart from the first item in the sequence, all subsequent paths should be relative paths and any absolute paths will be ignored.

			Parameters
			----------
			`paths`: `Sequence[GPath | str | bytes | os.PathLike]` or `*paths: GPath | str | bytes | os.PathLike`
			: the paths to be combined, which can be given as either a list-like object or as variadic arguments

			`​encoding`
			: the text encoding that should be used to decode bytes-like objects in `paths`, if any (see `__init__()`).

			Returns
			-------
			the combined path

			Raises
			------
			`ValueError` if any of the GPaths are invalid

			Examples
			--------
			```python
			GPath.join("usr", "local", "bin")          # GPath("usr/local/bin")
			GPath.join("/usr/local/bin", "../../bin")  # GPath("/usr/bin")
			GPath.join("C:/", "Windows")               # GPath("C:/Windows")
			```
		"""
		flattened_paths: list[GPathLike] = []
		for path_or_list in paths:
			if _is_gpathlike(path_or_list):
				flattened_paths.append(path_or_list)
			else:
				flattened_paths.extend(path_or_list)

		if len(flattened_paths) == 0:
			return GPath(encoding=encoding)

		combined_path = flattened_paths[0]
		if not isinstance(combined_path, GPath):
			combined_path = GPath(combined_path, encoding=encoding)
		for path in flattened_paths[1:]:
			combined_path = combined_path + path

		return combined_path


	def as_relative(self, parent_level: Optional[int]=None) -> GPath:
		"""
			Convert the path to a relative path and return a new copy.

			Parameters
			----------
			`​parent_level`
			: the number of levels of parent directories that the returned path should be relative to, which may be 0. If set to None, the returned path will have the same parent level as the current path if it is currently a relative path, or have no parent level (i.e. 0) otherwise.

			Raises
			------
			`TypeError` if `​parent_level` is not a valid type

			Examples
			--------
			```python
			GPath("/usr/bin").as_relative()      # GPath("usr/bin")
			GPath("C:/Windows").as_relative()    # GPath("C:Windows")
			GPath("../Documents").as_relative()  # GPath("../Documents")
			```
		"""

		new_path = GPath(self)
		new_path._root = False
		if parent_level is None:
			pass
		elif isinstance(parent_level, int):
			new_path._parent_level = parent_level
		else:
			raise TypeError(f"parent_level must be an int: {parent_level} ({type(parent_level)})")

		return new_path


	def as_absolute(self) -> GPath:
		"""
			Convert the path to an absolute path and return a new copy.

			Any parent directory that the path is relative to will be removed. If the path is already absolute, an identical copy is returned.

			Examples
			--------
			```python
			GPath("usr/bin").as_absolute()       # GPath("/usr/bin")
			GPath("../Documents").as_absolute()  # GPath("/Documents")
			GPath("C:Windows").as_absolute()     # GPath("C:/Windows")
			```
		"""
		new_path = GPath(self)
		new_path._root = True
		new_path._parent_level = 0
		return new_path


	def with_drive(self, drive: Union[str, bytes, None]=None) -> GPath:
		"""
			Return a new copy of the path with the drive set to `​drive`.

			If `​drive` is `""` or None, this would be equivalent to `without_drive()`.

			Parameters
			----------
			`​drive`
			: the drive for the returned path, or either `""` or None if the returned path should have no drive

			Returns
			-------
			`GPath`
			: a new path with the given drive

			Raises
			------
			- `TypeError` if `​drive` is not a valid type
			- `ValueError` if `​drive` has more than one character

			Examples
			--------
			```python
			GPath("C:/Windows").with_drive()      # GPath("/Windows")
			GPath("C:/Windows").with_drive("D")   # GPath("D:/Windows")
			GPath("/Windows").with_drive("C")     # GPath("C:/Windows")
			```
		"""
		if drive is None:
			drive = ""
		elif isinstance(drive, bytes):
			if self._encoding is None:
				drive = drive.decode(DEFAULT_ENCODING)
			else:
				drive = drive.decode(self._encoding)
		elif isinstance(drive, str):
			pass
		else:
			raise TypeError(f"drive must be a str or bytes object: {drive} ({type(drive)})")

		if len(drive) > 1:
			raise ValueError(f"drive can only be a single character, an empty string or None: {drive}")

		new_path = GPath(self)
		new_path._drive = drive
		return new_path


	def without_drive(self) -> GPath:
		"""
			Return a new copy of the path without a drive.

			Equivalent to `with_drive("")` or `with_drive(None)`.

			Returns
			-------
			`GPath`
			: a new path without a drive

			Examples
			--------
			```python
			GPath("C:/Windows").without_drive()      # GPath("/Windows")
			```
		"""
		return self.with_drive(None)


	def common_with(self, other: GPathLike, allow_current: bool=True, allow_parents: bool=False) -> Optional[GPath]:
		"""
			Find the longest common base path shared between `self` and `other`, or return None if no such path exists.

			A common base path might not exist if one path is an absolute path while the other is a relative path, or if the two paths are in different filesystems (with different drive names), or in other cases as controlled by the `allow_current` and `allow_parents` options.

			If using the default options of `allow_current=True` and `allow_parent=False`, the binary operator for bitwise-and can be used: `__and__()` (usage: <code><var>g1</var> & <var>g2</var></code>).

			Parameters
			----------
			`other`
			: the path to compare with

			`allow_current`
			: whether two non-parent relative paths that do not share any components should be considered to have a common base path, namely the imaginary current working directory. For instance, `GPath("some/rel/path").find_common("another/rel/path")` will return `GPath("")` if set to True, or return None if set to False.

			`allow_parents`
			: whether two relative paths that are relative to different levels of parent directories should be considered to have a common base path, which is the highest level of parent directory between the two paths. For instance, `GPath("../rel/to/parent").find_common("../../rel/to/grandparent")` will return `GPath("../..")` if set to True, or return None if set to False. **Warning**: when set to True, given a higher level of parent directory as output, it may not be possible to find the relative path to one of the inputs (see `relpath_from()`); in most cases False is more appropriate.

			Returns
			-------
			`GPath`
			: the longest common base path, which may be empty, if it exists

			`None`
			: otherwise

			Raises
			------
			`ValueError` if either `self` or `other` is an invalid GPath

			Examples
			--------
			```python
			GPath("/usr/bin").find_common("/usr/local/bin")               # GPath("/usr")
			GPath("C:/Windows/System32").find_common("C:/Program Files")  # GPath("C:/")
			GPath("../Documents").find_common("../Pictures")              # GPath("..")
			```
		"""
		self._validate()
		if isinstance(other, GPath):
			other._validate()
		else:
			other = GPath(other, encoding=self._encoding)

		if self._drive != other._drive:
			return None
		if self._root != other._root:
			return None

		if allow_parents:
			allow_current = True

		parts = []
		if self._root:
			common_path = GPath(self)
			for part1, part2 in zip(self._parts, other._parts):
				if part1 == part2:
					parts.append(part1)
		else:
			if self._parent_level != other._parent_level:
				if not allow_parents:
					return None

				common_path = GPath(self)
				common_path._parent_level = max(self._parent_level, other._parent_level)
			else:
				common_path = GPath(self)
				for part1, part2 in zip(self._parts, other._parts):
					if part1 == part2:
						parts.append(part1)

		common_path._parts = tuple(parts)

		if not allow_current and not bool(common_path):
			if common_path != self or common_path != other:
				return None
		return common_path


	def subpath_from(self, base: GPathLike) -> Optional[GPath]:
		"""
			Find the relative subpath from `base` to `self` if possible and if `base` contains `self`, or return None otherwise.

			None will also be returned if there are unknown components in the subpath from `base` to `self`. For instance, if `self` is relative to the parent directory while `base` is relative to the grandparent directory, the path from the grandparent directory `../..` to the parent directory `..` cannot be known.

			Similar to `relpath_from()`, but `self` must be a descendent of `base`.

			Parameters
			----------
			`base`
			: the base path that the relative subpath should start from

			Returns
			-------
			`GPath`
			: relative subpath from `base` to `self`, which may be empty, if it exists

			`None`
			: otherwise

			Raises
			------
			`ValueError` if either `self` or `base` is an invalid GPath

			Examples
			--------
			```python
			GPath("/usr/local/bin").subpath_from("/usr")      # GPath("local/bin")
			GPath("/usr/bin").subpath_from("/usr/local/bin")  # None
			GPath("/usr/bin").subpath_from("../Documents")    # None
			```
		"""
		if not isinstance(base, GPath):
			base = GPath(base, encoding=self._encoding)

		if self.common_with(base, allow_current=True, allow_parents=False) is not None and self in base:
			# If self._parent_level > base._parent_level, self is not in base, whereas if self._parent_level < base._parent_level, path from base to self's parent cannot be known
			base_length = len(base._parts)
			new_path = GPath(self)
			new_path._parts = self._parts[base_length:]  # () when self == base
			new_path._drive = ""
			new_path._root = False
			new_path._parent_level = 0
			return new_path
		else:
			return None


	def relpath_from(self, origin: GPathLike) -> Optional[GPath]:
		"""
			Find the relative path from `origin` to `self` if possible, or return None otherwise.

			None will also be returned if there are unknown components in the relative path from `origin` to `self`. For instance, if `self` is relative to the parent directory while `base` base is relative to the grandparent directory, the path from the grandparent directory `../..` to the parent directory `..` cannot be known.

			Similar to `subpath_from()`, but `self` does not need to be a descendent of `origin`.

			Parameters
			----------
			`origin`
			: the origin that the relative path should start from

			Returns
			-------
			`GPath`
			: relative path from `origin` to `self`, which may be empty, if it exists

			`None`
			: otherwise

			Raises
			------
			`ValueError` if either `self` or `origin` is an invalid GPath

			Examples
			--------
			```python
			GPath("/usr/local/bin").subpath_from("/usr")      # GPath("local/bin")
			GPath("/usr/bin").subpath_from("/usr/local/bin")  # GPath("../../bin")
			GPath("/usr/bin").subpath_from("../Documents")    # None
			```
		"""
		self._validate()
		if not isinstance(origin, GPath):
			origin = GPath(origin, encoding=self._encoding)

		if origin._root:
			common = self.common_with(origin)
			if common is None:
				return None

			new_path = GPath(self)
			new_path._parent_level = len(origin) - len(common)
			new_path._parts = self._parts[len(common):]
			new_path._drive = ""
			new_path._root = False
			return new_path

		else:
			common = self.common_with(origin, allow_current=True, allow_parents=True)
			if common is None:
				return None
			if common._parent_level > self._parent_level:
				return None  # Path from common to self's parent cannot be known

			# common._dotdot == self._dotdot
			# origin._dotdot <= self._dotdot

			new_path = GPath(self)
			new_path._drive = ""
			new_path._root = False
			if len(common) == 0:
				if origin._parent_level == self._parent_level:
					new_path._parent_level = len(origin)
				else:
					new_path._parent_level = (common._parent_level - origin._parent_level) + len(origin)
				new_path._parts = self._parts
			else:
				new_path._parent_level = len(origin) - len(common)
				new_path._parts = self._parts[len(common):]

			return new_path


	def __hash__(self) -> int:
		"""
			Calculate hash of the GPath object.

			Usage: <code>hash(<var>g</var>)</code>
		"""
		return hash(self._tuple)


	def __eq__(self, other: GPathLike) -> bool:
		"""
			Check if two GPaths are completely identical.

			Always return False if `other` is not a GPath object, even if it is a GPath-like object.

			Usage: <code><var>g1</var> == <var>g2</var></code>

			Examples
			--------
			```python
			GPath("/usr/bin") == GPath("/usr/bin")  # True
			GPath("/usr/bin") == GPath("usr/bin")   # False
			GPath("C:/") == GPath("D:/")            # False
			```
		"""
		if not isinstance(other, GPath):
			other = GPath(other, encoding=self._encoding)
		return self._tuple == other._tuple


	def __bool__(self) -> bool:
		"""
			Truthy if `self` is an absolute path, if `self` is relative to a parent directory, or if `self` has at least one named component.

			Usage: <code>bool(<var>g</var>)</code>, <code>not <var>g</var></code>, or <code>if <var>g</var>:</code>

			Examples
			--------
			```python
			bool(GPath("/"))    # True
			bool(GPath(".."))   # True
			bool(GPath("doc"))  # True
			bool(GPath(""))     # False
			```
		"""
		return self._root or self._drive != "" or self._parent_level != 0 or len(self._parts) > 0


	def __str__(self) -> str:
		"""
			Return a string representation of the path.

			Usage: <code>str(<var>g</var>)</code>
		"""
		if bool(self):
			if self.root and self._drive == "":
				return _rules.generic_rules.roots[0]
			else:
				return (self._drive + _rules.generic_rules.drive_postfixes[0] if self._drive != "" else "") + (_rules.generic_rules.roots[0] if self._root else "") + _rules.generic_rules.separators[0].join(self.relative_parts)
		else:
			return _rules.generic_rules.current_indicators[0]


	def __repr__(self) -> str:
		"""
			Return a string that, when printed, gives the Python code associated with instantiating the GPath object.

			Usage: <code>repr(<var>g</var>)</code>
		"""
		if self._encoding is None:
			encoding_repr = ""
		else:
			encoding_repr = f", encoding={repr(self._encoding)}"

		if bool(self):
			return f"GPath({repr(str(self))}{encoding_repr})"
		else:
			return f"GPath({repr('')}{encoding_repr})"


	def __len__(self) -> int:
		"""
			Get the number of named path components, excluding any drive name or parent directories.

			Usage: <code>len(<var>g</var>)</code>

			Examples
			--------
			```python
			len(GPath("/usr/bin"))    # 2
			len(GPath("/"))           # 0
			len(GPath("C:/Windows"))  # 0
			len(GPath("C:/"))         # 0
			```
		"""
		return len(self._parts)


	def __getitem__(self, index: Union[int, slice]) -> Union[str, list[str]]:
		"""
			Get a 0-indexed named path component, or a slice of path components, excluding any drive name or parent directories.

			Usage: <code><var>g</var>[<var>n</var>]</code>, <code><var>g</var>[<var>start</var>:<var>end</var>]</code>, <code><var>g</var>[<var>start</var>:<var>end</var>:<var>step</var>]</code>, etc.

			Examples
			--------
			```python
			GPath("/usr/local/bin")[1]    # "local"
			GPath("/usr/local/bin")[-1]   # "bin"
			GPath("/usr/local/bin")[1:]   # ["local", "bin"]
			GPath("/usr/local/bin")[::2]  # ["usr", "bin"]
			```
		"""
		if isinstance(index, int):
			return self._parts[index]
		elif isinstance(index, slice):
			return list(self._parts[index])


	def __iter__(self) -> Iterator[str]:
		"""
			Get an iterator through the named path components, excluding any drive name or parent directories.

			Usage: <code>iter(<var>g</var>)</code> or <code>for <var>p</var> in <var>g</var>:</code>
		"""
		return iter(self._parts)


	def __contains__(self, other: GPathLike) -> bool:
		"""
			Check if the path represented by `self` contains the path represented by `other`; i.e. check if `self` is a parent directory of `other`.

			Usage: <code><var>other</var> in <var>self</var></code>

			Raises `ValueError` if either GPath is invalid

			Examples
			--------
			```python
			GPath("/usr/local/bin") in GPath("/usr")  # True
			GPath("/usr/local/bin") in GPath("/bin")  # False
			GPath("..") in GPath("../..")             # True
			GPath("..") in GPath("C:/")               # False
			```
		"""
		if not isinstance(other, GPath):
			other = GPath(other, encoding=self._encoding)

		common_path = self.common_with(other, allow_current=True, allow_parents=True)
		return common_path is not None and common_path == self


	def __add__(self, other: GPathLike) -> GPath:
		"""
			Add (concatenate) `other` to the end of `self`, and return a new copy.

			If `other` is an absolute path, the returned path will be an absolute path that matches `other`, apart from the drive name.

			If `other` has a drive, the returned path will have the same drive as `other`. Otherwise, the returned path will have the same drive as `self`. If neither has a drive, the returned path will not have a drive as well.

			Alias: `__truediv__()`

			Usage: <code><var>self</var> + <var>other</var></code> or <code><var>self</var> / <var>other</var></code>

			Raises `ValueError` if either GPath is invalid

			Examples
			--------
			```python
			GPath("/usr") + GPath("local/bin")                   # GPath("/usr/local/bin")
			GPath("C:/Windows/System32") + GPath("../SysWOW64")  # GPath("C:/Windows/SysWOW64")
			GPath("C:/Windows/System32") + GPath("/usr/bin")     # GPath("C:/usr/bin")
			GPath("..") + GPath("../..")                         # GPath("../../..")
			GPath("..") / GPath("../..")                         # GPath("../../..")
			```
		"""
		if isinstance(other, GPath):
			other._validate
		else:
			other = GPath(other, encoding=self._encoding)

		new_path = GPath(self)
		if other._root:
			new_path._parts = other._parts
			new_path._root = other._root
			new_path._parent_level = other._parent_level
		else:
			new_parts = [part for part in self._parts]
			for i in range(other._parent_level):
				if len(new_parts) > 0:
					new_parts.pop()
				elif not new_path._root:
					new_path._parent_level += 1
				else:
					pass  # parent of directory of root is still root

			new_parts.extend(other._parts)
			new_path._parts = tuple(new_parts)

		if other._drive != "":
			new_path._drive = other._drive

		return new_path


	def __sub__(self, n: int) -> GPath:
		"""
			Remove `n` components from the end of the path and return a new copy.

			Usage: <code><var>self</var> - <var>n</var></code>

			Raises `ValueError` if `self` is an invalid GPath or if `n` is negative

			Examples
			--------
			```python
			GPath("C:/Windows/System32") - 1  # GPath("C:/Windows")
			GPath("/usr/bin") - 2             # GPath("/")
			GPath("Documents") - 3            # GPath("..")
			GPath("/") - 1                    # GPath("/")
			```
		"""
		if n < 0:
			raise ValueError("cannot subtract a negative number of components from the path: {n}; use __add__() instead")

		new_path = GPath(self)
		new_parts = [part for part in self._parts]
		for i in range(n):
			if len(new_parts) > 0:
				new_parts.pop()
			elif not new_path._root:
				new_path._parent_level += 1
			else:
				pass  # removing components from root should still give root
		new_path._parts = tuple(new_parts)
		return new_path


	def __mul__(self, n: int) -> GPath:
		"""
			Duplicate the named components of `self` `n` times and return a new path with the duplicated components.

			Named components will be duplicated separately from the components representing a parent directory. If `self` is an absolute path, only the relative components will be duplicated.

			If `n` is 0, the result is an empty path (either relative or absolute).

			Usage: <code><var>self</var> * <var>n</var></code>

			Raises `ValueError` if `self` is an invalid GPath or if `n` is negative.

			Examples
			--------
			```python
			GPath("/usr/bin") * 2    # GPath("/usr/bin/usr/bin")
			GPath("../docs") * 2     # GPath("../../docs/docs")
			GPath("C:/Windows") * 0  # GPath("C:/")
			```
		"""
		if n < 0:
			raise ValueError("cannot multiply path by a negative integer: {n}")
		new_path = GPath(self)
		new_path._parent_level = self._parent_level * n
		new_path._parts = self._parts * n
		return new_path


	def __truediv__(self, other: GPathLike) -> GPath:
		"""
			Alias of `__add__()`.

			Usage: <code><var>self</var> + <var>other</var></code> or <code><var>self</var> / <var>other</var></code>
		"""
		return self.__add__(other)


	def __and__(self, other: GPathLike) -> Union[GPath, None]:
		"""
			Equivalent to `self.common_with(other)`, using the default options of `common_with()`.

			Usage: <code><var>g1</var> & <var>g2</var></code>
		"""
		return self.common_with(other)


	def __lshift__(self, n: int) -> GPath:
		"""
			Move the imaginary current working directory `n` steps up the filesystem tree.

			If `self` is a relative path, remove up to `n` levels of parent directories from the start of the path and return a copy. If it is an absolute path, return a copy of `self` unchanged.

			If `n` is negative, this is equivalent to `__rshift__(-n)`.

			Usage: <code><var>self</var> << <var>n</var></code>

			Raises `ValueError` if `self` is an invalid GPath.

			Examples
			--------
			```python
			GPath("../SysWOW64/drivers") << 1  # GPath("SysWOW64/drivers")
			GPath("../doc") << 2               # GPath("doc")
			GPath("/usr/bin") << 2             # GPath("/usr/bin")
			```
		"""
		if n < 0:
			return self.__rshift__(-1 * n)
		new_path = GPath(self)
		if not new_path._root:
			new_path._parent_level = max(new_path._parent_level - n, 0)
		return new_path


	def __rshift__(self, n: int) -> GPath:
		"""
			Move the imaginary current working directory `n` steps down the filesystem tree.

			If `self` is a relative path, add `n` levels of parent directories to the start of the path and return a copy. If it is an absolute path, return a copy of `self` unchanged.

			If `n` is negative, this is equivalent to `__lshift__(-n)`.

			Usage: <code><var>self</var> >> <var>n</var></code>

			Raises `ValueError` if `self` is an invalid GPath

			Examples
			--------
			```python
			GPath("../SysWOW64/drivers") >> 1  # GPath("../../SysWOW64/drivers")
			GPath("/usr/bin") >> 2             # GPath("/usr/bin")
			```
		"""
		if n < 0:
			return self.__lshift__(-1 * n)
		new_path = GPath(self)
		if not new_path._root:
			new_path._parent_level += n
		return new_path


	@property
	def _tuple(self) -> tuple:
		# Get a tuple of all fields
		return (
			self._root,
			self._drive,
			self._parent_level,
			self._parts,
			self._encoding,
		)


	def _validate(self) -> bool:
		# Check if self is in a valid state
		if self._parent_level < 0:
			raise ValueError(f"invalid GPath, _parent cannot be negative: {repr(self)}")
		if self._root:
			if self._parent_level != 0:
				raise ValueError(f"invalid GPath, _parent must be 0 when root is True: {repr(self)}")
		return True


GPathLike = Union[GPath, str, bytes, os.PathLike]
"""Union type of GPath-like objects that can be used as the argument for most `GPath` methods."""
