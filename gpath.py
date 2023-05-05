"""
	GPath is a robust, generalised abstract file path that provides path manipulations independent from the local environment, maximising cross-platform compatibility.
"""

from __future__ import annotations

import enum
import functools
import os
import re
import sys
from collections.abc import Hashable, Iterable, Iterator, Sequence
from enum import auto, IntEnum, IntFlag
#from typing import Any, ClassVar, Final


# Type hinting prior to 3.10
# Using generics in built-in collections, e.g. list[int], is supported from 3.7 by __future__.annotations
from typing import Any, Callable, ClassVar, Collection, Generator, Optional, Union
if sys.version_info >= (3, 8):
	from typing import Final
else:
	Final = Any
if sys.version_info >= (3, 10):
	def _is_gpathlike(obj: Any) -> bool:
		return isinstance(obj, GPathLike)
else:
	def _is_gpathlike(obj: Any) -> bool:
		return isinstance(obj, GPath) or isinstance(obj, str) or isinstance(obj, os.PathLike)


__version__ = '0.3'


__all__ = ['GPath', 'GPathLike']


@enum.unique
class PathType(IntEnum):
	GENERIC = 0
	POSIX = auto()
	POSIX_HOME = auto()
	POSIX_PORTABLE = auto()
	WINDOWS_NT = auto()
	UNC = auto()

	@staticmethod
	def from_str(name: str) -> PathType:
		return _path_type_of_str[name]

_path_type_of_canonical_str: Final = {
	'generic': PathType.GENERIC,
	'posix': PathType.POSIX,
	'posix-home': PathType.POSIX_HOME,
	'posix-portable': PathType.POSIX_PORTABLE,
	'windows-nt': PathType.WINDOWS_NT,
	'unc': PathType.UNC,
}
path_types: Final = list(_path_type_of_canonical_str.keys())
_path_type_of_str: Final = _path_type_of_canonical_str.update({
	'': PathType.GENERIC,
	'posix': PathType.POSIX,
	'linux': PathType.POSIX,
	'macos': PathType.POSIX,
	'osx': PathType.POSIX,
	'linux-home': PathType.POSIX_HOME,
	'macos-home': PathType.POSIX_HOME,
	'osx-home': PathType.POSIX_HOME,
	'home': PathType.POSIX_HOME,
	'portable': PathType.POSIX_PORTABLE,
	'win': PathType.WINDOWS_NT,
	'windows': PathType.WINDOWS_NT,
	'nt': PathType.WINDOWS_NT,
})

class _PathValidity(IntFlag):
	NONE = 0
	POSIX = auto()
	POSIX_HOME = auto()
	POSIX_PORTABLE = auto()
	WINDOWS_NT = auto()
	UNC = auto()
	#MSDOS = auto()
	#NT_API = auto()
	#NT_OBJECT = auto()
	#WIN32_FILE = auto()
	#WIN32_DEVICE = auto()
	#REGISTRY = auto()

	ALL = ~NONE

	LINUX = POSIX
	MACOS = POSIX
	OSX = MACOS
	UNIX = POSIX
	OS2 = WINDOWS_NT


_LOCAL_SEPARATOR: Final = "/" if os.sep == '/' or os.altsep == '/' else os.sep
_LOCAL_ROOT_INDICATOR: Final = _LOCAL_SEPARATOR
_LOCAL_PLAIN_ROOT_INDICATOR: Final = os.sep  # Windows does not accept a single '/' as device root
_LOCAL_CURRENT_INDICATOR: Final = os.curdir
_LOCAL_PARENT_INDICATOR: Final = os.pardir


_COMMON_CURRENT_INDICATOR: Final = "."
_COMMON_PARENT_INDICATOR: Final = ".."

_POSIX_SEPARATOR: Final = "/"

# https://web.archive.org/web/20230319003310/https://learn.microsoft.com/en-gb/windows/win32/fileio/naming-a-file
# https://web.archive.org/web/20230411102940/https://learn.microsoft.com/en-us/dotnet/standard/io/file-path-formats
# https://web.archive.org/web/20230422040824/https://googleprojectzero.blogspot.com/2016/02/the-definitive-guide-on-win32-to-nt.html
_MSDOS_SEPARATOR: Final = "\\"
# https://web.archive.org/web/20230504144810/https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-even/c1550f98-a1ce-426a-9991-7509e7c3787c
_NT_OBJECT_PREFIX: Final = "\\??\\"
_NT_API_SEPARATOR: Final = _MSDOS_SEPARATOR
_WIN32_FILE_PREFIX: Final = "\\\\?\\"
_WIN32_DEVICE_PREFIX: Final = "\\\\.\\"
_WIN32_API_SEPARATOR = _MSDOS_SEPARATOR
_UNC_PREFIXES: Final = ("\\\\", "//")

POSIX_PORTABLE_CHARS: Final = set([
	"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
	"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
	"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "_", "-"
])
WINDOWS_NT_FORBIDDEN_CHARS: Final = set([
	"\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06", "\x07", "\x08", "\x09", "\x0a", "\x0b", "\x0c", "\x0d", "\x0e", "\x0f",
	"\x10", "\x11", "\x12", "\x13", "\x14", "\x15", "\x16", "\x17", "\x18", "\x19", "\x1a", "\x1b", "\x1c", "\x1d", "\x1e", "\x1f",
	"0x7f", '"', "*", "/", ":", "<", ">", "?", "\\", "|"
])
WINDOWS_NT_FORBIDDEN_FILENAMES: Final = set([
	"COM0", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
	"LPT0", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
	"CON", "PRN", "AUX", "NUL"
])
#MSDOS_FORBIDDEN_CHARS: Final = WINDOWS_NT_FORBIDDEN_CHARS | set(["+", ",", ".", ";", "=", "[", "]"])
#MSDOS_FORBIDDEN_COMPONENTS: Final = set([
#	"$IDLE$", "AUX", "COM1", "COM2", "COM3", "COM4", "CON", "CONFIG$", "CLOCK$", "KEYBD$", "LPT1", "LPT2", "LPT3", "LPT4", "LST", "NUL", "PRN", "SCREEN$"
#])


def _split_relative(
	path: str,
	delimiters: Union[str, Collection[str]]=_LOCAL_SEPARATOR,
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
	current_dirs: Collection[str]=_COMMON_CURRENT_INDICATOR,
	parent_dirs: Collection[str]=_COMMON_PARENT_INDICATOR,
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


def _check_windows_nt_component(components: Sequence[str]) -> Generator[bool, None, None]:
	for component in components:
		i = len(component) - 1
		while component[i] in [" ", "."]:
			i -= 1
		component = component[:(i + 1)]
		tokens = component.split(".")
		for fn in WINDOWS_NT_FORBIDDEN_FILENAMES:
			if tokens[0] == fn:
				yield True
		yield False


class _PathValidator:
	def __init__(self,
		roots: Iterable[str]=[],
		separators: Iterable[str]=[],
		namespace_separators: Iterable[str]=[],
		current_indicators: Iterable[str]=[_COMMON_CURRENT_INDICATOR],
		parent_indicators: Iterable[str]=[_COMMON_PARENT_INDICATOR],
		allow_root: bool=True,
		force_root: bool=False,
		allow_namespace: bool=True,
		force_namespace: bool=False,
		permitted_chars: Optional[Iterable[str]]=None,
		forbidden_chars: Iterable[str]=[],
		forbidden_components: Iterable[str]=[],
		forbidden_component_checkers: Iterable[Callable[[bool, Sequence[str]], Sequence[bool]]]=[lambda r, p: [False for c in p]],
		permitted_namespaces: Optional[Iterable[str]]=None,
		forbidden_namespaces: Iterable[str]=[],
		forbidden_namespace_patterns: Iterable[Union[str, re.Pattern]]=[],
		placeholders: Iterable[str]=[],
		placeholder_patterns: Iterable[Union[str, re.Pattern]]=[],
		root_placeholders: Iterable[str]=[],
		root_placeholder_patterns: Iterable[Union[str, re.Pattern]]=[],
	):
		self.separators: list[str] = list(separators)
		self.roots: list[str] = list(roots)
		self.namespace_separators: list[str] = list(namespace_separators)
		self.current_indicators: list[str] = list(current_indicators)
		self.parent_indicators: list[str] = list(parent_indicators)
		self.allow_root: bool = allow_root
		self.force_root: bool = force_root
		self.allow_namespace: bool = allow_namespace
		self.force_namespace: bool = force_namespace
		self.permitted_chars: Optional[set[str]] = set(permitted_chars) if permitted_chars is not None else None
		self.forbidden_chars: set[str] = set(forbidden_chars)
		self.forbidden_components: set[str] = set(forbidden_components)
		self.forbidden_component_checkers: list[Callable[[bool, Sequence[str]], Sequence[bool]]] = list(forbidden_component_checkers)
		self.permitted_namespaces: Optional[set[str]] = set(permitted_namespaces) if permitted_namespaces is not None else None
		self.forbidden_namespaces: set[str] = set(forbidden_namespaces)
		self.forbidden_namespace_patterns: list[re.Pattern] = [re.compile(p) for p in forbidden_namespace_patterns]
		self.placeholders: set[str] = set(placeholders)
		self.placeholder_pattern: list[re.Pattern] = [re.compile(p) for p in placeholder_patterns]
		self.root_placeholders: set[str] = set(root_placeholders)
		self.root_placeholder_pattern: list[re.Pattern] = [re.compile(p) for p in root_placeholder_patterns]


class _Validators:
	GENERIC: Final = _PathValidator()

	POSIX: Final = _PathValidator(
		roots=["/"],
		separators=["/"],
		allow_namespace=False,
		forbidden_chars=["/", "\0"],
	)

	POSIX_HOME: Final = _PathValidator(
		roots=["~"],
		separators=["/"],
		namespace_separators=["/"],
		forbidden_chars=["/", "\0"],
	)

	POSIX_PORTABLE: Final = _PathValidator(
		roots=["/"],
		separators=["/"],
		allow_namespace=False,
		permitted_chars=POSIX_PORTABLE_CHARS,
	)

	#MSDOS: Final = _PathTypeData(
	#	roots=["\\"],
	#	forbidden_chars=MSDOS_FORBIDDEN_CHARS,
	#	forbidden_component_checkers=[
	#		lambda r, p: [False if i != 1 else (r == True and len(s) >= 2 and s[0].upper() == "DEV" and s[1] in MSDOS_FORBIDDEN_COMPONENTS) for i, c in enumerate(p)]
	#	],
	#	forbidden_namespace_patterns=[r'^..']
	#)

	WINDOWS_NT: Final = _PathValidator(
		roots=["\\", "/"],
		separators=["\\", "/"],
		namespace_separators=[":"],
		forbidden_chars=WINDOWS_NT_FORBIDDEN_CHARS,
		forbidden_component_checkers=[lambda r, p: [v for v in _check_windows_nt_component(p)]],
		forbidden_namespace_patterns=[r'^..'],
	)

	UNC: Final = _PathValidator(
		roots=["\\\\", "//"],
		separators=["\\", "/"],
		namespace_separators=["\\", "/"],
		force_namespace=True,
		forbidden_chars=WINDOWS_NT_FORBIDDEN_CHARS,
		forbidden_component_checkers=[lambda r, p: [v for v in _check_windows_nt_component(p)]],
		forbidden_namespace_patterns=[r'^..'],
	)

	@staticmethod
	def from_type(type: PathType) -> _PathValidator:
		return _validator_of_type[type]

_validator_of_type: Final = {
	PathType.GENERIC: _Validators.GENERIC,
	PathType.POSIX: _Validators.POSIX,
	PathType.POSIX_HOME: _Validators.POSIX_HOME,
	PathType.POSIX_PORTABLE: _Validators.POSIX_PORTABLE,
	PathType.WINDOWS_NT: _Validators.WINDOWS_NT,
	PathType.UNC: _Validators.UNC,
}


@functools.total_ordering
class GPath(Hashable):
	"""
		An immutable generalised abstract file path that has no dependency on any real filesystem.

		The path can be manipulated on a system that is different from where it originated, particularly with a different operating environment, and it can represent file paths on a system other than local. Examples where this is useful include remote management of servers and when cross-compiling source code for a different platform. Since GPath objects are immutable, all operations return a new instance.

		The path is always stored in a normalised state, and is always treated as case sensitive.

		The path can be rendered as a string using <code>str(<var>g</var>)</code>, which will use `/` as the path separator if possible to maximise cross-platform compatibility.

		If the GPath will be used on a specific operating system,

		If the GPath is to be used on the local system, use <code><var>g</var>.to_local()</code> instead, which will render object represents a viable real path on the local system, it will always be rendered in a format that is meaningful to the local system.
	"""

	__slots__ = (
		'_parts',
		'_namespace',
		'_root',
		'_parent_level',
		'_propagate_encoding',
		'_target_type',
		'_root_validity',
		'_part_validities',
	)

	_separator: ClassVar[str] = _LOCAL_SEPARATOR
	_root_indicator: ClassVar[str] = _LOCAL_ROOT_INDICATOR
	_plain_root_indicator: ClassVar[str] = _LOCAL_PLAIN_ROOT_INDICATOR
	_current_indicator: ClassVar[str] = _LOCAL_CURRENT_INDICATOR
	_parent_indicator: ClassVar[str] = _LOCAL_PARENT_INDICATOR


	def __init__(self, path: Union[str, bytes, os.PathLike, GPath, None]="", encoding: str='utf-8'):
		"""
			Initialise a normalised and generalised abstract file path, possibly by copying an existing GPath object.

			Parameters
			----------
			`path`
			: path-like object representing a (possibly unnormalised) file path, or a GPath object to be copied
			`encoding`
			: if `path` is a `bytes`-like object, name of a standard Python text encoding (as listed in the `codecs` module in the standard library) that should be use to decode it; otherwise, this parameter is ignored

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
		self._namespace: str = ""
		self._root: bool = False
		self._parent_level: int = 0

		self._propagate_encoding: Union[str, None] = None
		self._target_type: PathType = PathType.GENERIC
		self._root_validity: _PathValidity = _PathValidity.NONE
		self._part_validities: tuple[_PathValidity, ...] = tuple()

		if path is None or path == "":
			return

		if isinstance(path, GPath):
			path._validate()
			self._parts = path._parts
			self._namespace = path._namespace
			self._root = path._root
			self._parent_level = path._parent_level
			self._propagate_encoding = path._propagate_encoding
			self._root_validity = path._root_validity
			self._part_validities = path._part_validities
			return

		path = os.fspath(path)

		if isinstance(path, bytes):
			self._propagate_encoding = encoding
			path = path.decode(encoding)

		# path is a str

		#if path.startswith(_WIN32_FILE_PREFIX):
		#	self._validities = _PathValidity.WIN32_FILE
		#	self._parts = tuple(_split_path(path[len(_WIN32_FILE_PREFIX):], delimiter=_WIN32_API_SEPARATOR, collapse=False))
		#	self._root = _WIN32_FILE_PREFIX
		#	return

		#if path.startswith(_WIN32_DEVICE_PREFIX):
		#	self._validities = _PathValidity.WIN32_DEVICE
		#	parts = _split_path(path[len(_WIN32_DEVICE_PREFIX):], delimiter=_WIN32_API_SEPARATOR)
		#	self._parts = tuple(_normalise_relative(parts))
		#	self._root = _WIN32_DEVICE_PREFIX
		#	return

		#if path.startswith(_NT_OBJECT_PREFIX):
		#	self._validities = _PathValidity.NT_OBJECT | _PathValidity.NT_API
		#	parts = _split_path(path[len(_NT_OBJECT_PREFIX):], delimiter=_NT_API_SEPARATOR)
		#	self._parts = tuple(_normalise_relative(parts))
		#	self._root = _NT_OBJECT_PREFIX
		#	return

		# path is POSIX, POSIX_PORTABLE, MSDOS, WINDOWS_NT, UNC or NT_API
		#root_validity = _PathValidity.POSIX | _PathValidity.POSIX_HOME | _PathValidity.POSIX_PORTABLE | _PathValidity.MSDOS | _PathValidity.WINDOWS_NT | _PathValidity.UNC | _PathValidity.NT_API
		root_validity = _PathValidity.POSIX | _PathValidity.POSIX_HOME | _PathValidity.POSIX_PORTABLE | _PathValidity.WINDOWS_NT | _PathValidity.UNC

		if path.startswith(_Validators.UNC.roots[0]):
			root_validity = _PathValidity.UNC
			self._root = True
			parts = _split_relative(path[len(_Validators.UNC.roots[0]):], delimiters=_Validators.UNC.separators)
			if len(parts) < 2:
				root_validity &= ~_PathValidity.UNC
			self._namespace = _Validators.UNC.separators[0].join(parts[:2])
			self._parts = tuple(parts[2:])
			return

		if len(path) >= 2 and path[1] in _Validators.WINDOWS_NT.namespace_separators:
			#validities &= ~_PathValidity.POSIX & ~_PathValidity.POSIX_PORTABLE & ~_PathValidity.UNC & ~_PathValidity.NT_API
			root_validity &= ~_PathValidity.POSIX & ~_PathValidity.POSIX_PORTABLE & ~_PathValidity.UNC
			self._namespace = path[0]
			deviceless_path = path[2:]
		else:
			deviceless_path = path

		if deviceless_path.startswith(_MSDOS_SEPARATOR):
			root_validity &= ~_PathValidity.POSIX & ~_PathValidity.POSIX_PORTABLE
			self._root = True

		if deviceless_path.startswith(_POSIX_SEPARATOR):
			#validities &= ~_PathValidity.MSDOS & ~_PathValidity.NT_API
			self._root = True

		if self._root:
			rootless_path = deviceless_path[1:]
		else:
			rootless_path = deviceless_path

		if _MSDOS_SEPARATOR in rootless_path:
			root_validity &= ~_PathValidity.POSIX & ~_PathValidity.POSIX_PORTABLE
		#if _POSIX_SEPARATOR in rootless_path:
		#	validities &= ~_PathValidity.MSDOS & ~_PathValidity.NT_API

		parts = _split_relative(rootless_path, delimiters=[_POSIX_SEPARATOR, _MSDOS_SEPARATOR])
		parts = _normalise_relative(parts)
		parent_level = 0
		while parent_level < len(parts) and parts[parent_level] == _COMMON_PARENT_INDICATOR:
			parent_level += 1
		self._parts = tuple(parts[parent_level:])
		if self._root == False:
			self._parent_level = parent_level


	@property
	def named_parts(self) -> list[str]:
		"""
			Read-only named components of the path, not including the filesystem root, device name, or any parent directories

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
			Read-only path components representing a parent directory that it is relative to, if any, with a copy of `parent_indicator` for each level of parent directory

			Examples
			--------
			```python
			GPath("../../Documents").parent_parts  # ["..", ".."]
			GPath("usr/local/bin").parent_parts    # []
			```
		"""
		return [GPath._parent_indicator for i in range(self._parent_level)]

	@property
	def relative_parts(self) -> list[str]:
		"""
			Read-only relative components of the path, not including the filesystem root or device name, with a copy of `parent_indicator` for each level of parent directory

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
	def device(self) -> str:
		"""
			Read-only device name

			Examples
			--------
			```python
			GPath("C:/Windows").device       # "C:"
			GPath("/usr/bin").device         # ""
			GPath("../../Documents").device  # ""
			```
		"""
		return self._namespace

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


	@staticmethod
	def partition(*paths: Union[Iterable[GPathLike], GPathLike], allow_current: bool=True, allow_parents: bool=False) -> dict[GPath, list[GPath]]:
		"""
			Partition a collection of paths based on shared common base paths such that each path belongs to one partition.

			For each partition, return a list of relative paths from the base path of that partition to each corresponding input path within that partition, unless `allow_parents` is True (see below). If the input collection is ordered, the output order is preserved within each partition. If the input collection contains duplicates, the corresponding output lists will as well.

			The number of partitions is minimised by merging partitions as much as possible, so that each partition represents the highest possible level base path. Two partitions can no longer be merged when there is no common base path between them, as determined by `common_with()`. This method takes the same optional arguments as `common_with()`, with the same default values.

			Parameters
			----------
			`paths: Iterable[GPath | str | os.PathLike]` or `*paths: GPath | str | os.PathLike`
			: the paths to be partitioned, which can be given as either a list-like object or as variadic arguments

			`allow_current`
			: whether non-parent relative paths with no shared components should be considered to have a common base path (see `common_with()`)

			`allow_parents`
			: whether paths that are relative to different levels of parent directories should be considered to have a common base path (see `common_with()`). **Warning**: when set to True, the output lists for each partition are invalidated, and explicitly set to empty. This is because it is not possible in general to obtain a relative path from the base path to its members if the base path is a parent directory of a higher level than the member (see `relpath_from()`). This  option should be True if and only if the list of members in each partition are not of interest; in most cases False is more appropriate.

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
		gpaths = [path if isinstance(path, GPath) else GPath(path) for path in flattened_paths]

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


	@staticmethod
	def join(*paths: Union[Sequence[GPathLike], GPathLike]) -> GPath:
		"""
			Join a sequence of paths into a single path. Apart from the first item in the sequence, all subsequent paths should be relative paths and any absolute paths will be ignored.

			Parameters
			----------
			`paths`: `Sequence[GPath | str | os.PathLike]` or `*paths: GPath | str | os.PathLike`
			: the paths to be combined, which can be given as either a list-like object or as variadic arguments

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
			return GPath()

		combined_path = flattened_paths[0]
		if not isinstance(combined_path, GPath):
			combined_path = GPath(combined_path)
		for path in flattened_paths[1:]:
			combined_path = combined_path + path

		return combined_path


	def common_with(self, other: GPathLike, allow_current: bool=True, allow_parents: bool=False) -> Optional[GPath]:
		"""
			Find the longest common base path shared between `self` and `other`, or return None if no such path exists.

			A common base path might not exist if one path is an absolute path while the other is a relative path, or if the two paths are in different filesystems (with different device names), or in other cases as controlled by the `allow_current` and `allow_parents` options.

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
			other = GPath(other)

		if self._namespace != other._namespace:
			return None
		if self._root != other._root:
			return None

		if allow_parents:
			allow_current = True

		parts = []
		if self._root:
			common_path = GPath()
			for part1, part2 in zip(self._parts, other._parts):
				if part1 == part2:
					parts.append(part1)
			common_path._root = True
			# dotdot must be 0
		else:
			if self._parent_level != other._parent_level:
				if not allow_parents:
					return None

				common_path = GPath()
				common_path._parent_level = max(self._parent_level, other._parent_level)
			else:
				common_path = GPath()
				common_path._parent_level = self._parent_level
				for part1, part2 in zip(self._parts, other._parts):
					if part1 == part2:
						parts.append(part1)

		common_path._namespace = self._namespace
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
			base = GPath(base)

		if self.common_with(base, allow_current=True, allow_parents=False) is not None and self in base:
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
			origin = GPath(origin)

		if origin._root:
			common = self.common_with(origin)
			if common is None:
				return None

			new_path = GPath()
			new_path._parent_level = len(origin) - len(common)
			new_path._parts = self._parts[len(common):]
			return new_path

		else:
			common = self.common_with(origin, allow_current=True, allow_parents=True)
			if common is None:
				return None
			if common._parent_level > self._parent_level:
				return None  # Path from common to self's parent cannot be known

			# common._dotdot == self._dotdot
			# origin._dotdot <= self._dotdot

			new_path = GPath()
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
		return hash((tuple(self._parts), self._namespace, self._root, self._parent_level, GPath._separator, GPath._current_indicator, GPath._parent_indicator))


	def __eq__(self, other: Any) -> bool:
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
			GPath("/usr/bin") == "/usr/bin"         # False
			```
		"""
		if isinstance(other, GPath):
			return self._tuple == other._tuple
		else:
			return False


	def __lt__(self, other: GPathLike) -> bool:
		"""
			Check if `self` should be collated before `other` by comparing them in component-wise lexicographical order.

			Relative paths come before (are less than) absolute paths, and non-parent relative paths come before (are less than) parent-relative paths. Between two parent relative paths, the path with the lower parent level comes first (is lesser).

			Usage: <code><var>self</var> < <var>other</var></code>

			Examples
			--------
			```python
			GPath("") < GPath("..")       # True
			GPath("..") < GPath("../..")  # True
			GPath("../..") < GPath("/")   # True
			GPath("/") < GPath("C:/")     # True
			GPath("") < GPath("usr")      # True
			```
		"""
		if not isinstance(other, GPath):
			other = GPath(other)
		return self._order < other._order


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
		return self._root or self._namespace != "" or self._parent_level != 0 or len(self._parts) > 0


	def __str__(self) -> str:
		"""
			Return a string representation of the path.

			Usage: <code>str(<var>g</var>)</code>
		"""
		if bool(self):
			if self.root and self._namespace == "":
				return GPath._plain_root_indicator
			else:
				return (self._namespace + _Validators.WINDOWS_NT.namespace_separators[0] if self._namespace != "" else "") + (GPath._root_indicator if self._root else "") + GPath._separator.join(self.relative_parts)
		else:
			return GPath._current_indicator


	def __repr__(self) -> str:
		"""
			Return a string that, when printed, gives the Python code associated with instantiating the GPath object.

			Usage: <code>repr(<var>g</var>)</code>
		"""
		if bool(self):
			return f"GPath({repr(str(self))})"
		else:
			return f"GPath({repr('')})"


	def __len__(self) -> int:
		"""
			Get the number of named path components, excluding any device name or parent directories.

			Usage: <code>len(<var>g</var>)</code>

			Examples
			--------
			```python
			len(GPath("/usr/bin"))   # 2
			len(GPath("/"))          # 0
			len(GPath("C:/Windows))  # 0
			len(GPath("C:/))         # 0
			```
		"""
		return len(self._parts)


	def __getitem__(self, index: Union[int, slice]) -> Union[str, list[str]]:
		"""
			Get a 0-indexed named path component, or a slice of path components, excluding any device name or parent directories.

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
			Get an iterator through the named path components, excluding any device name or parent directories.

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
			other = GPath(other)

		common_path = self.common_with(other, allow_current=True, allow_parents=True)
		return common_path is not None and common_path == self


	def __add__(self, other: GPathLike) -> GPath:
		"""
			Add (concatenate) `other` to the end of `self`, and return a new copy.

			If `other` is an absolute path, the returned path will be an absolute path that matches `other`, apart from the device name.

			If `other` has a device name, the returned path will have the same device name as `other`. Otherwise, the returned path will have the same device name as `self`. If neither has a device name, the returned path will not have a device name as well.

			Alias: `__div__()`

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
			other = GPath(other)

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

		if other._namespace != "":
			new_path._namespace = other._namespace

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


	def __div__(self, other: GPathLike) -> GPath:
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
			self._namespace,
			self._parent_level,
			self._parts,
		)


	@property
	def _order(self) -> tuple:
		# Get a tuple that represents the ordering of the class
		return (
			self._root,  # relative before absolute
			self._namespace,  # no device before devices
			self._parent_level,  # no parent before low parent before high parent
			self._parts  # empty before few components before many components
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
"""Union type of GPath-like objects that can be used as the argument for most GPath methods."""
