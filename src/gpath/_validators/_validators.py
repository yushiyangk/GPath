from ._common import _GenericValidator, _PathValidator
from ._posix import _PosixPortableValidator, _PosixValidator
from ._windows import _UNCValidator, _WindowsNTValidator
from ..pathtype import PathType

from .._compat import Final


_generic_validator = _GenericValidator()
_posix_validator = _PosixValidator()
_posix_portable_validator = _PosixPortableValidator()
_windows_nt_validator = _WindowsNTValidator()
_unc_validator = _UNCValidator()


_type_validators: Final = {
	PathType.GENERIC: _generic_validator,
	PathType.POSIX: _posix_validator,
	PathType.POSIX_PORTABLE: _posix_portable_validator,
	PathType.WINDOWS_NT: _windows_nt_validator,
	PathType.UNC: _unc_validator,
}


def _from_type(type: PathType) -> _PathValidator:
	return _type_validators[type]
