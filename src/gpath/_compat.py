import sys
import typing


# Required for versions < 3.10
Optional = typing.Optional
Union = typing.Union


if sys.version_info >= (3, 8):
	Final = typing.Final[typing.Any]
else:
	Final = typing.Any
