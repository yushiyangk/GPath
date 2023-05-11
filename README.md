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

Found a bug? Please [file an issue](https://github.com/yushiyangk/GPath/issues), or, better yet, [submit a pull request](https://github.com/yushiyangk/GPath/pulls).

## Compatibility

The default `GPath()` interface supports the vast majority of valid file paths on Windows, Linux and macOS (and other POSIX-like operating systems), with some limited caveats.

### Linux, macOS and POSIX

- any backslashes `\` in the path will be treated as path separators
- if the second character of the path is a colon <code><var>x</var>:</code>, the first character <var>`x`</var> will be treated as a drive letter

### Windows and MS-DOS

- any trailing dots `.` and spaces ` ` will not be stripped
- reserved MS-DOS device names (such as AUX, CLOCK$, COM0 through COM9, CON, LPT0 through LPT9, NUL, PRN) will be treated as normal file names

## Development

Clone the repository with `git clone https://github.com/yushiyangk/GPath.git`.

The source for the package is entirely contained in `gpath.py`, with tests in `tests/`.

### Virtual environment

Create the venv using `python -m venv .`.

To activate the venv, on Linux run `source Scripts/activate`, and on Windows run `Scripts/Activate.ps1` or `Scripts/activate.bat`.

Later, to deactivate the venv, run `deactivate`.

### Dependencies

Run `pip install -r requirements.dev.txt`.

### Install

To install the package locally (in the venv) for development, run `pip install -e .`.

### Tasks

For unit tests, run `pytest`.

To run unit tests across all supported Python versions, run `tox p -m testall`. This is slower than just `pytest`. Note that only Python versions that are installed locally will be run.

To run the full set of tasks before package publication, run `tox p -m prepare`. Alternatively, see below for manually running individual steps in this process.

#### Unit tests

Run `pytest` or `coverage run -m pytest`.

For coverage report, first run `coverage run -m pytest`, then either `coverage report -m` to print to stdout or `coverage html` to generate an HTML report in `htmlcov/`. Alternatively, run `tox r -m test` to do both steps automatically (slower).

#### Documentation

Run `tox r -m docs`.

The documentation is generated in `docs/html/`, using template files in `docs/template/`. However, note that the favicon file must be placed at `docs/html/favicon.png` manually as pdoc is unable to do so.

#### Packaging

Before packaging, check the package metadata by running `pyroma .` or `tox r -m metadata`.

To generate sdist and wheel packages, delete `dist/` and `generic_path.egg-info/` if they exist, then run `python -m build`. Run `twine check dist/*` to check that the packages were generated properly. Alternatively, run `tox r -m package` to do these steps automatically.

### Config files

- `MANIFEST.in` Additional files to include in published sdist package
- `pyproject.toml` Package metadata, as well as configs for test and build tools
- `requirements.dev.txt` Package dependencies for development, in pip format
- `requirements.publish.txt` Package dependencies for publishing, in pip format
- `tox.ini` Config file for tox

### Troubleshooting

#### Unable to uninstall the local package

Sometimes, if gpath was installed using `pip install .`, pip might have difficulty uninstalling the package, giving the contradictory message
<pre><code>Found existing installation: gpath <var>version</var>
Can't uninstall 'gpath'. No files were found to uninstall.</code></pre>

In this case, manually delete `build/` and `generic_path.egg-info/` if they exist, then run `pip uninstall generic-path` again. This should allow pip to successfully uninstall the package.

#### Tox always fails with exit 1

Delete the contents of `.tox/` and try again.
