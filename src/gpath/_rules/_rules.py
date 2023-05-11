from typing import Type
from ._common import _COMMON_DRIVE_POSTFIX, _COMMON_CURRENT_INDICATOR, _COMMON_PARENT_INDICATOR
from ..pathtype import PathType

from .._compat import Final


class UnvalidatedRules:
	pass

class _generic_rules(UnvalidatedRules):
	drive_postfixes: Final = [_COMMON_DRIVE_POSTFIX]
	current_indicators: Final = [_COMMON_CURRENT_INDICATOR]
	parent_indicators: Final = [_COMMON_PARENT_INDICATOR]

class _posix_rules(_generic_rules):
	roots: Final = ["/"]
	separators: Final = ["/"]

class _posix_portable_rules(_generic_rules):
	roots: Final = ["/"]
	separators: Final = ["/"]

class _windows_nt_rules(_generic_rules):
	roots: Final = ["\\", "/"]
	separators: Final = ["\\", "/"]
	drive_postfixes: Final = [":"]


_type_rules: Final = {
	PathType.GENERIC: _generic_rules,
	PathType.POSIX: _posix_rules,
	PathType.POSIX_PORTABLE: _posix_portable_rules,
	PathType.WINDOWS_NT: _windows_nt_rules,
}


def _from_type(type: PathType) -> Type[UnvalidatedRules]:
	return _type_rules[type]
