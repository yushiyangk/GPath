from ._common import _GenericValidator, _PathValidator
from ._posix import _PosixPortableValidator, _PosixValidator
from ._windows import _UNCValidator, _WindowsNTValidator
from ..pathtype import PathType

from .._compat import Final


_generic_rules = _GenericValidator()
_posix_rules = _PosixValidator()
_posix_portable_rules = _PosixPortableValidator()
_windows_nt_rules = _WindowsNTValidator()
_unc_rules = _UNCValidator()


_type_rules: Final = {
	PathType.GENERIC: _generic_rules,
	PathType.POSIX: _posix_rules,
	PathType.POSIX_PORTABLE: _posix_portable_rules,
	PathType.WINDOWS_NT: _windows_nt_rules,
	PathType.UNC: _unc_rules,
}


def _from_type(type: PathType) -> _PathValidator:
	return _type_rules[type]
