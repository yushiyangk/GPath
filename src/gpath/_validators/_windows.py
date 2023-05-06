from __future__ import annotations

from collections.abc import Sequence

from ._common import _GenericValidator

from .._compat import Final


_WINDOWS_NT_FORBIDDEN_CHARS: Final = set([
	"\x00", "\x01", "\x02", "\x03", "\x04", "\x05", "\x06", "\x07", "\x08", "\x09", "\x0a", "\x0b", "\x0c", "\x0d", "\x0e", "\x0f",
	"\x10", "\x11", "\x12", "\x13", "\x14", "\x15", "\x16", "\x17", "\x18", "\x19", "\x1a", "\x1b", "\x1c", "\x1d", "\x1e", "\x1f",
	"0x7f", '"', "*", "/", ":", "<", ">", "?", "\\", "|"
])

_WINDOWS_NT_FORBIDDEN_FILENAMES: Final = set([
	"COM0", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
	"LPT0", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
	"CON", "PRN", "AUX", "NUL"
])

#MSDOS_FORBIDDEN_CHARS: Final = WINDOWS_NT_FORBIDDEN_CHARS | set(["+", ",", ".", ";", "=", "[", "]"])
#MSDOS_FORBIDDEN_COMPONENTS: Final = set([
#	"$IDLE$", "AUX", "COM1", "COM2", "COM3", "COM4", "CON", "CONFIG$", "CLOCK$", "KEYBD$", "LPT1", "LPT2", "LPT3", "LPT4", "LST", "NUL", "PRN", "SCREEN$"
#])

# https://web.archive.org/web/20230319003310/https://learn.microsoft.com/en-gb/windows/win32/fileio/naming-a-file
# https://web.archive.org/web/20230411102940/https://learn.microsoft.com/en-us/dotnet/standard/io/file-path-formats
# https://web.archive.org/web/20230422040824/https://googleprojectzero.blogspot.com/2016/02/the-definitive-guide-on-win32-to-nt.html
# https://web.archive.org/web/20230504144810/https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-even/c1550f98-a1ce-426a-9991-7509e7c3787c
#NT_OBJECT_PREFIX: Final = "\\??\\"
#NT_API_SEPARATOR: Final = "\\"
#WIN32_FILE_PREFIX: Final = "\\\\?\\"
#WIN32_DEVICE_PREFIX: Final = "\\\\.\\"


class _WindowsNTValidator(_GenericValidator):
	def __init__(self):
		super().__init__(
			roots=["\\", "/"],
			separators=["\\", "/"],
			drive_postfixes=[":"],
			allow_root=True,
			allow_drive=True,
			forbidden_chars=_WINDOWS_NT_FORBIDDEN_CHARS,
			forbidden_checkers=[_WindowsNTValidator._check_parts],
		)

	@staticmethod
	def _check_parts(parts: Sequence[str]) -> list[bool]:
		out = []

		for part in parts:
			i = len(part) - 1
			while part[i] in [" ", "."]:
				i -= 1
			part = part[:(i + 1)]
			tokens = part.split(".")
			if tokens[0] in _WINDOWS_NT_FORBIDDEN_FILENAMES:
				out.append(True)
			out.append(False)

		return out


class _UNCValidator(_WindowsNTValidator):
	def __init__(self):
		super().__init__()
		self.roots = ["\\\\", "//"]
		self.namespace_separators = self.separators
		self.force_root = True
		self.allow_namespace = True
		self.force_namespace = True
