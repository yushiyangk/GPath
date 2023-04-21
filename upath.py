from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Final, ClassVar

PATH_SEPARATOR: Final = "/" if os.sep == '/' or os.altsep == '/' else os.sep

PathLike = str | os.PathLike

class UPath():
	"""
		A normalised abstract file path with no dependency on the layout of the local filesystem or, if different, the source filesystem that generated the path representation.

		Paths are represented in a format that is meaningful to the local operating system.

		Instance attributes
		-------------------
		- `path: str`
		   path relative to either an anonymous parent directory (e.g. '../..', represented by `dotdot`) or to a filesystem root (represented by `root`), without any trailing separator for folders
		- `device: str`
		   device name of the path (e.g. drive letter on Windows), or an empty string if no device is associated with the path (e.g. Linux file paths); usually empty when `root` is False
		- `root: bool`
		   whether the path is relative to the filesystem root; should only be True when `dotdot` is 0
		- `dotdot: int`
		   number of levels of parent directories that the path is relative to (i.e. number of '..'s in the path); should only be non-zero when `root` is False; may be 0 even if `root` is False, indicating a path relative to an abstract current directory

		Class attributes
		----------------
		- `separator: str`
		   path separator string used in the `path` attribute of UPath instances, meaningful to the local operating system
	"""

	__slots__ = ('path', 'device', 'root', 'dotdot')

	separator: ClassVar = PATH_SEPARATOR

	def __init__(self, path: PathLike | UPath | None='') -> None:
		"""
			Initialise a normalised abstract file path, possibly by copying an existing UPath object.

			Evoked by `UPath(path)` and mutates `self`

			Parameters:
			- `path: PathLike | UPath | None`
			   path-like object representing a (unnormalised) file path, or a UPath object to be copied
		"""
		self.path: str = ''  # root- or dotdot- relative path
		self.device: str = ''
		self.root: bool = False
		self.dotdot: int = 0
		if path is not None and path != '':
			if isinstance(path, UPath):
				self.path = path.path
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
				parts = path.split(os.sep)
				if parts[0] == '':  # First element is '' if root
					parts = parts[1:]
				dotdot = 0
				while parts[dotdot] == os.pardir:  # os.pardir == '..' usually
					dotdot += 1
				parts = parts[dotdot:]
				self.path = (UPath.separator).join(parts)
				self.dotdot = dotdot

	def __add__(self, other: UPathLike) -> UPath | None:
		"""
			Add a relative UPath to `self` and return the new UPath. Return `None` if `other` is not a relative path, or if `other` and `self` have different `device`.

			Evoked by `upath1 + upath2`
		"""
		other = UPath(other)  # Create a new instance to mutate even if already a UPath

		if other.root:
			return None
		elif other.device != '' and self.device != other.device:
			return None
		else:
			newpath = UPath(self)
			parts = (self.path).split(UPath.separator) if len(self.path) > 0 else []
			while other.dotdot > 0:
				if len(parts) > 0:
					parts.pop()
				elif not newpath.root:
					newpath.dotdot += 1
				other.dotdot -= 1

			assert other.dotdot == 0 and not other.root
			parts.append(other.path)
			newpath.path = (UPath.separator).join(parts)
			return newpath

	def split(self) -> list[str]:
		"""
			Split the UPath into a list of strings representing each part of the abstract file path.

			If the path is relative to a filesystem root, the first item in the returned list will contain the device name if it exists, or an empty string otherwise. This allows the full absolute path to be reconstructed using `UPath.separator.join(myupath.split())`.

			If the path is relative to an anonymous ancestor directory (e.g. '../..'), the first item in the returned list will consist of the entire relative parent path (i.e. may consist of more than one '..' part) pointing to the highest-known-level ancestor directory.

			Returns
			-------
			  `List[str]`
			   list of parts of the abstract file path; empty list if it refers to an abstract current directory

			Raises
			------
			  `ValueError`
			   if `self.dotdot` < 0
		"""
		baseparts = []
		if self.root:
			baseparts = [self.device]
		elif self.dotdot != 0:
			if self.dotdot < 0:
				raise ValueError
			baseparts = [os.path.join(*([os.pardir] * self.dotdot)).replace(os.sep, UPath.separator)]
		return baseparts + ((self.path).split(UPath.separator) if len(self.path) > 0 else [])

	def subpath(self, base: UPathLike):
		"""
			Check if `self` is a descendent path from `base`, and return the relative path of `self` from `base` if it is.

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
		"""
		if not isinstance(base, UPath):
			base = UPath(base)
		cpath = UPath.common(self, base)
		if cpath is not None and cpath == base:
			baselen = len((base.path).split(os.sep))
			parts = (self.path).split(os.sep)
			spath = UPath()
			spath.path = (UPath.separator).join(parts[baselen:])  # '' when self == base
			return spath
		else:
			return None

	@staticmethod
	def common(path1: UPathLike, path2: UPathLike) -> UPath | None:
		"""
			Static method. Find the longest common base path shared by two abstract file paths.

			Parameters
			----------
			  `path1: UPathLike`, `path2: UPathLike`
			   the abstract file paths to compare

			Returns
			-------
			- `UPath`
			   longest common base path, which may be empty if `path1` and `path2` are relative to the same filesystem root or to the same level of parent directories
			- `None`
			   otherwise
		"""
		if not isinstance(path1, UPath):
			path1 = UPath(path1)
		if not isinstance(path2, UPath):
			path2 = UPath(path2)

		if path1.device == path2.device:
			if path1.root and path2.root:
				cpath = UPath()
				cpath.path = os.path.commonpath([path1.path, path2.path])
				cpath.root = True
				cpath.device = path1.device
				return cpath
			elif not path1.root and not path2.root and path1.dotdot == path2.dotdot:
				cpath = UPath()
				cpath.path = os.path.commonpath([path1.path, path2.path])
				cpath.dotdot = path1.dotdot
				return cpath
			else:
				return None
		else:
			return None

	@staticmethod
	def partitions(paths: Sequence[UPathLike]) -> list[UPath]:
		"""
			Static method. Partition a list of abstract file paths based on the common base paths between members of the list, such that each abstract file path can only belong to one partition. Return a list of common base paths corresponding to these partitions.

			The method by which partitions are determined is identical to the method used in `UPath.common(...)`. Paths that are relative to ancestor directories of different levels will be placed in distinct partitions.

			Parameters
			----------
			  `paths: Sequence[UPathLike]`
			   the list of abstract file paths to partition

			Returns
			-------
			  `List[UPath]`
			   list of common base paths by which the members of `paths` can be partitioned; empty list if `paths` is empty
		"""
		paths = [path if isinstance(path, UPath) else UPath(path) for path in paths]

		partitionlist = []
		if len(paths) > 0:
			partitionlist.append(paths[0])
		for path in paths[1:]:
			existing = False
			for (i, partition) in enumerate(partitionlist):
				newbase = UPath.common(partition, path)
				if newbase is not None and bool(newbase):
					existing = True
					if partitionlist[i] != newbase:
						partitionlist[i] = newbase
					break
			if not existing:
				partitionlist.append(path)
		return partitionlist

	@staticmethod
	def joinstr(paths: Sequence[UPathLike], delim: str="") -> str:
		"""
			Static method. Join a list of abstract file paths using the delimeter if any and return it as a string.
		"""
		return delim.join(str(path) for path in paths)

	def __bool__(self) -> bool:
		"""
			Return True if `self.path` not is empty, return False otherwise.

			Evoke as `bool(myupath)`
		"""
		return self.root or self.dotdot != 0 or self.path != ''

	def __str__(self) -> str:
		"""
			Return a string representation of the abstract file path.

			Evoke as `str(myrange)`
		"""
		if self.root:
			return os.path.join(self.device, os.sep, self.path).replace(os.sep, UPath.separator)
		else:
			return os.path.join(self.device, *([os.pardir] * self.dotdot), self.path).replace(os.sep, UPath.separator)

	def __repr__(self) -> str:
		"""
			Return a source code representation of the abstract file path.

			Evoke as `repr(myrange)`
		"""
		return f"UPath({str(self)})"

	def __eq__(self, other: Any) -> bool:
		"""
			Check if two abstract file paths are completely identical. Always return False if `other` is not a UPath object.

			Evoke as `myrange == other`
		"""
		if type(other) is UPath:
			return self.__dict__ == other.__dict__
		else:
			return False

UPathLike = UPath | PathLike
