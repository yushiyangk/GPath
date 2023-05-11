from __future__ import annotations

import re
from enum import IntFlag, auto
from typing import Callable, Iterable, Sequence

from .._compat import Final, Optional, Union


_COMMON_DRIVE_POSTFIX: Final = ":"
_COMMON_CURRENT_INDICATOR: Final = "."
_COMMON_PARENT_INDICATOR: Final = ".."



class _PathValidity(IntFlag):
	NONE = 0
	POSIX = auto()
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


class _PathValidator:
	def __init__(self,
		roots: Iterable[str]=[],
		separators: Iterable[str]=[],
		namespace_separators: Iterable[str]=[],
		drive_postfixes: Iterable[str]=[],
		current_indicators: Iterable[str]=[],
		parent_indicators: Iterable[str]=[],
		allow_root: bool=False,
		force_root: bool=False,
		allow_namespace: bool=False,
		force_namespace: bool=False,
		allow_drive: bool=False,
		force_drive: bool=False,
		allow_anchor: bool=False,
		force_anchor: bool=False,
		permitted_chars: Optional[Iterable[str]]=None,
		forbidden_chars: Iterable[str]=[],
		forbidden_parts: Iterable[str]=[],
		forbidden_part_patterns: Iterable[Union[str, re.Pattern]]=[],
		forbidden_checkers: Iterable[Callable[[Sequence[str]], Sequence[bool]]]=[],
		permitted_namespace_chars: Optional[Iterable[str]]=None,
		forbidden_namespace_chars: Iterable[str]=[],
		forbidden_namespace_parts: Iterable[str]=[],
		forbidden_namespace_part_patterns: Iterable[Union[str, re.Pattern]]=[],
		forbidden_namespace_checkers: Iterable[Callable[[Sequence[str]], Sequence[bool]]]=[],
		anchors: Iterable[str]=[],
		anchor_patterns: Iterable[Union[str, re.Pattern]]=[],
	):
		self.roots: list[str] = list(roots)
		self.separators: list[str] = list(separators)
		self.namespace_separators: list[str] = list(namespace_separators)
		self.drive_postfixes: list[str] = list(drive_postfixes)
		self.current_indicators: list[str] = list(current_indicators)
		self.parent_indicators: list[str] = list(parent_indicators)
		self.allow_root: bool = allow_root
		self.force_root: bool = force_root
		self.allow_namespace: bool = allow_namespace
		self.force_namespace: bool = force_namespace
		self.allow_drive: bool = allow_drive
		self.force_drive: bool = force_drive
		self.allow_anchor: bool = allow_anchor
		self.force_anchor: bool = force_anchor
		self.permitted_chars: Optional[set[str]] = set(permitted_chars) if permitted_chars is not None else None
		self.forbidden_chars: set[str] = set(forbidden_chars)
		self.forbidden_parts: set[str] = set(forbidden_parts)
		self.forbidden_part_patterns: list[re.Pattern] = [re.compile(p) for p in forbidden_part_patterns]
		self.forbidden_checkers: list[Callable[[Sequence[str]], Sequence[bool]]] = list(forbidden_checkers)
		self.permitted_namespace_chars: Optional[set[str]] = set(permitted_namespace_chars) if permitted_namespace_chars is not None else None
		self.forbidden_namespace_chars: set[str] = set(forbidden_namespace_chars)
		self.forbidden_namespace_parts: set[str] = set(forbidden_namespace_parts)
		self.forbidden_namespace_part_patterns: list[re.Pattern] = [re.compile(p) for p in forbidden_namespace_part_patterns]
		self.forbidden_namespace_checkers: list[Callable[[Sequence[str]], Sequence[bool]]] = list(forbidden_namespace_checkers)
		self.anchors: set[str] = set(anchors)
		self.anchor_patterns: list[re.Pattern] = [re.compile(p) for p in anchor_patterns]


class _GenericValidator(_PathValidator):
	def __init__(self, *super_args, **super_kwargs):
		super().__init__(*super_args, **super_kwargs)
		self.drive_postfixes = [_COMMON_DRIVE_POSTFIX]
		self.current_indicators = [_COMMON_CURRENT_INDICATOR]
		self.parent_indicators = [_COMMON_PARENT_INDICATOR]




#def _check_part_validity(part: str, validator: _PathValidator) -> bool:
#	if part in validator.forbidden_parts:
#		return False
#	for pattern in validator.forbidden_part_patterns:
#		if pattern.match(part):
#			return False

#	return True

#def _check_namespace_part_validity(namespace_part: str, validator: _PathValidator) -> bool:


#def _check_validities(parts: Sequence[str], validator: _PathValidator) -> list[bool]:

#	...
