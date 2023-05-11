from typing import Type

from ._common import COMMON_DRIVE_POSTFIX, COMMON_CURRENT_INDICATOR, COMMON_PARENT_INDICATOR
from ..platform import Platform

from .._compat import Final


class UnvalidatedRules:
	pass

class generic_rules(UnvalidatedRules):
	drive_postfixes: Final = [COMMON_DRIVE_POSTFIX]
	current_indicators: Final = [COMMON_CURRENT_INDICATOR]
	parent_indicators: Final = [COMMON_PARENT_INDICATOR]
	roots: Final = ["/", "\\"]
	separators: Final = ["/", "\\"]

class posix_rules(UnvalidatedRules):
	current_indicators: Final = [COMMON_CURRENT_INDICATOR]
	parent_indicators: Final = [COMMON_PARENT_INDICATOR]
	roots: Final = ["/"]
	separators: Final = ["/"]

class windows_rules(UnvalidatedRules):
	drive_postfixes: Final = [COMMON_DRIVE_POSTFIX]
	current_indicators: Final = [COMMON_CURRENT_INDICATOR]
	parent_indicators: Final = [COMMON_PARENT_INDICATOR]
	roots: Final = ["\\", "/"]
	separators: Final = ["\\", "/"]


platform_rules: dict[Platform, Type[UnvalidatedRules]] = {
	Platform.GENERIC: generic_rules,
	Platform.POSIX: posix_rules,
	Platform.WINDOWS: windows_rules,
}


def from_type(type: Platform) -> Type[UnvalidatedRules]:
	return platform_rules[type]
