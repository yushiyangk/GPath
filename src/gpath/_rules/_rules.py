from ._common import _COMMON_DRIVE_POSTFIX, _COMMON_CURRENT_INDICATOR, _COMMON_PARENT_INDICATOR

from .._compat import Final


class UnvalidatedRules:
	pass

class _generic_rules(UnvalidatedRules):
	drive_postfixes: Final = [_COMMON_DRIVE_POSTFIX]
	current_indicators: Final = [_COMMON_CURRENT_INDICATOR]
	parent_indicators: Final = [_COMMON_PARENT_INDICATOR]
	roots: Final = ["/", "\\"]
	separators: Final = ["/", "\\"]
	drive_postfixes: Final = [":"]
