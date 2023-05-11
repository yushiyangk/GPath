## Changelog

This project follows [PEP 440](https://peps.python.org/pep-0440/) and [Semantic Versioning (SemVer)](https://semver.org/spec/v2.0.0.html). In addition to the guarantees specified by SemVer, for versions before 1.0, this project guarantees backwards compatibility of the API for patch version updates (0.<var>y</var>.<b><var>z</var></b>).

The recommended version specifier is <code>generic-path ~= <var>x</var>.<var>y</var></code> for version 1.0 and later, and <code>generic-path ~= <var>0</var>.<var>y</var>.<var>z</var></code> for versions prior to 1.0.

### 0.4.1

- Fixed embedded documentation

### 0.4

#### Breaking API changes

- Replaced the following instance methods with read-only properties:
	- <code><var>g</var>.get_parent_level()</code> → <code><var>g</var>.parent_level</code>
	- <code><var>g</var>.get_parent_parts()</code> → <code><var>g</var>.parent_parts</code>
	- <code><var>g</var>.get_device()</code> → <code><var>g</var>.drive</code> (renamed `device` to `drive`)
	- <code><var>g</var>.is_absolute()</code> → <code><var>g</var>.absolute</code>
	- <code><var>g</var>.is_root()</code> → <code><var>g</var>.root</code>
- Replaced <code><var>g</var>.get_parts()</code> and <code><var>g</var>.from_parts()</code> with the read-only properties <code><var>g</var>.named_parts</code> and <code><var>g</var>.relative_parts</code>
- Replaced `GPath.find_common()` with <code><var>g</var>.common_with()</code> and added <code><var>g1</var> & <var>g2</var></code> as an alias for <code><var>g</var>.common_with()</code> with default options
- Removed the ability to sort GPaths, and removed the following comparison operators:
	- <code><var>g1</var> < <var>g2</var></code>
	- <code><var>g1</var> <= <var>g2</var></code>
	- <code><var>g1</var> > <var>g2</var></code>
	- <code><var>g1</var> >= <var>g2</var></code>
- Removed package constants `PATH_SEPARATOR`, `PATH_CURRENT`, `PATH_PARENT`, and typedef `PathLike`

#### Breaking behavioural changes

- Changed <code><var>g1</var> + <var>g2</var></code>, <code><var>g1</var> / <var>g2</var></code> and <code><var>g</var>.join()</code> so that appending an absolute path overwrites the left operand; previously the left operand would be returned unchanged
- Changed <code><var>g1</var> == <var>g2</var></code> so that it can return True even when the left operand is GPath-like but not a GPath object

#### Other changes

- Added <code><var>g</var>.as_absolute()</code>, <code><var>g</var>.as_relative()</code>, <code><var>g</var>.with_drive()</code>, <code><var>g</var>.without_drive()</code> for returning modified copies of the path
- Added support for drive names in relative paths
- Added support for instantiating a GPath with a bytes-like object, <code>GPath(<var>byteslike</var>)</code> (or, fixed the constructor that was previously broken for bytes-like objects)
- Added an argument to `GPath.__init__()` to allow specifying encoding (default `'utf-8'`), which propagates to new GPaths when performing operations with other bytes-like operands
- Added the read-only property <code><var>g</var>.encoding</code> for this propagating encoding
- Added abstract base classes for GPath, from `collections.abc`
- Fixed <code><var>g1</var> / <var>g2</var></code>
- Fixed small errors in web documentation

### 0.3

- Renamed `GPath.current` to `GPath.current_dir` and `GPath.parent` to `GPath.parent_dir`
- Renamed <code><var>g</var>.is_root()</code> to <code><var>g</var>.is_absolute()</code>
- Renamed the optional arguments in <code><var>g</var>.find_common()</code> and <code><var>g</var>.partition()</code>, from `common_current` and `common_parent` to `allow_current` and `allow_parent`
- Added a new <code><var>g</var>.is_root()</code> that checks whether the path is exactly root
- Added <code><var>g</var>.\_\_div\_\_()</code> as an alias of <code><var>g</var>.\_\_add\_\_()</code>
- Added web documentation at https://gpath.gnayihs.uy/

### 0.2.1

- Fixed basic example in README

### 0.2

- Added support for Python versions 3.7 through 3.9; previously only 3.10 and 3.11 were supported

### 0.1

- Initial version
