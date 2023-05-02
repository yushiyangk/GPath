## Changelog

### 0.3

- Renamed <code><var>g</var>.current</code> to <code><var>g</var>.current_dir</code> and <code><var>g</var>.parent</code> to <code><var>g</var>.parent_dir</code>
- Renamed <code><var>g</var>.is_root()</code> to <code><var>g</var>.is_absolute()</code>
- Renamed the optional arguments in <code><var>g</var>.find_common()</code> and <code><var>g</var>.partition()</code>, from `common_current` and `common_parent` to `allow_current` and `allow_parent`
- Added a new <code><var>g</var>.is_root()</code> that checks whether the path is exactly root
- Added <code><var>g</var>.\_\_div\_\_()</code> as an alias of <code><var>g</var>.\_\_add\_\_()</code>
- Added HTML documentation

### 0.2.1

- Fixed basic example in README

### 0.2

- Added support for Python versions 3.7 through 3.9; previously only 3.10 and 3.11 were supported

### 0.1

- Initial version
