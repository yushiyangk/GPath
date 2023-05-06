from ._common import _GenericValidator

from .._compat import Final


_POSIX_PORTABLE_CHARS: Final = set([
	"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z",
	"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
	"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "_", "-"
])


class _PosixValidator(_GenericValidator):
	def __init__(self):
		super().__init__(
			roots=["/"],
			separators=["/"],
			allow_root=True,
			allow_anchor=True,
			forbidden_chars=["/", "\0"],
			anchor_patterns=[r'^~[^/]*'],
		)


class _PosixPortableValidator(_GenericValidator):
	def __init__(self):
		super().__init__(
			roots=["/"],
			separators=["/"],
			allow_root=True,
			permitted_chars=_POSIX_PORTABLE_CHARS,
		)
