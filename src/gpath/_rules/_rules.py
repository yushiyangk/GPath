from typing import Type

from ._common import COMMON_DRIVE_POSTFIX, COMMON_CURRENT_INDICATOR, COMMON_PARENT_INDICATOR
from ..pathtype import PathType

from .._compat import Final


class UnvalidatedRules:
	pass

class generic_rules(UnvalidatedRules):
	drive_postfixes: Final = [COMMON_DRIVE_POSTFIX]
	current_indicators: Final = [COMMON_CURRENT_INDICATOR]
	parent_indicators: Final = [COMMON_PARENT_INDICATOR]
	roots: Final = ["/", "\\"]
	separators: Final = ["/", "\\"]
	drive_postfixes: Final = [":"]


def from_type(type: PathType) -> Type[UnvalidatedRules]:
	return generic_rules
