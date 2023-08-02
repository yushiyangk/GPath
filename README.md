# GPath

**GPath** is a Python package that provides a robust, generalised abstract file path that allows path manipulations independent from the local environment, maximising cross-platform compatibility.

[![](https://img.shields.io/badge/PyPI--inactive?style=social&logo=pypi)](https://pypi.org/project/generic-path/) [![](https://img.shields.io/badge/GitHub--inactive?style=social&logo=github)](https://github.com/yushiyangk/GPath) [![](https://img.shields.io/badge/Documentation--inactive?style=social&logo=readthedocs)](https://gpath.gnayihs.uy/)

## Install

```
pip install generic-path
```

## Basic examples

Import GPath:
```python
from gpath import GPath
```

Create a GPath object and manipulate it:
```python
g = GPath("/usr/bin")

common = GPath.find_common(g, "/usr/local/bin")  # GPath("/usr")
relpath = g.relpath_from("/usr/local/bin")       # GPath("../../bin")
joined = GPath.join("/usr/local/bin", relpath)   # GPath("/usr/bin")
assert g == joined
```

For function arguments, strings or `os.PathLike` objects can be used interchangeably with GPaths.

Binary operations are also supported:
```python
g1 = GPath("C:/Windows/System32")
g2 = GPath("../SysWOW64/drivers")

added = g1 + g2      # GPath("C:/Windows/SysWOW64/drivers")
subtracted = g1 - 1  # GPath("C:/Windows")

# Shift the imaginary current working directory in relative paths
shifted_right = g2 >> 1  # GPath("../../SysWOW64/drivers")
shifted_left = g2 << 1   # GPath("SysWOW64/drivers")
```

The `GPath.partition()` method is useful when dealing with paths from various different sources:
```python
partitions = GPath.partition("/usr/bin", "/usr/local/bin", "../../doc", "C:/Windows", "C:/Program Files")

assert partitions == {
	GPath("/usr")      : [GPath("bin"), GPath("local/bin")],
	GPath("../../doc") : [GPath("")],
	GPath("C:/")       : [GPath("Windows"), GPath("Program Files")],
}
```

## Issues

Found a bug? Please [report an issue](https://github.com/yushiyangk/GPath/issues), or, better yet, [contribute a bugfix](https://github.com/yushiyangk/GPath/pulls).

## Compatibility

The default `GPath()` interface supports the vast majority of valid file paths on Windows, Linux and macOS (and other POSIX-like operating systems), with some limited caveats.

### Linux, macOS and POSIX

If using `GPath()`,
- any backslashes `\` (after parsing escape sequences) in the path will be treated as path separators
- if the second character of the path is a colon <code><var>x</var>:</code>, the first character <var>`x`</var> will be treated as a drive letter

These issues can be avoided by using `GPath.from_posix()` instead. This will cause all `\` and `:` to be treated as normal characters in file names.

### Windows

- trailing dots `.` and spaces ` ` will not be stripped
- reserved MS-DOS device names (such as AUX, CLOCK$, COM0 through COM9, CON, LPT0 through LPT9, NUL, PRN) will be treated as normal file names
