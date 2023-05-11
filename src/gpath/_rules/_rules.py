from ._common import COMMON_DRIVE_POSTFIX, COMMON_CURRENT_INDICATOR, COMMON_PARENT_INDICATOR

from .._compat import Final


class generic_rules:
	drive_postfixes: Final = [COMMON_DRIVE_POSTFIX]
	current_indicators: Final = [COMMON_CURRENT_INDICATOR]
	parent_indicators: Final = [COMMON_PARENT_INDICATOR]
	roots: Final = ["/", "\\"]
	separators: Final = ["/", "\\"]
	drive_postfixes: Final = [":"]
