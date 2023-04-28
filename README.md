# GPath

**GPath** is a Python package that provides a robust, generalised abstract file path that provides functions for common path manipulations independent from the local operating system.

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
partitions = GPath.partition("/usr/bin", "/usr/local/", "../../doc", "C:/Windows", "C:/Program Files")

assert partitions == {
	GPath("/usr")      : [GPath("/usr/bin"), GPath("/usr/local")],
	GPath("../../doc") : [GPath("")],
	GPath("C:/")       : [GPath("Windows"), GPath("Program Files")]
}
```

## Issues

Found a bug? Please [file an issue](https://github.com/yushiyangk/GPath/issues), or, better yet, [submit a pull request](https://github.com/yushiyangk/GPath/pulls)

## Development

Clone the repository with `git clone https://github.com/yushiyangk/GPath.git`.

The source for the package is entirely contained in `gpath.py`, with tests in `tests/`.

### Virtual environment

The virtual environment was created with `python -m venv .`.

To activate the virtual environment, on Linux run `source Scripts/activate`, and on Windows run `Scripts/Activate.ps1` or `Scripts/activate.bat`.

Later, to deactivate the virtual environment, run `deactivate`.

### Dependencies

Run `pip install -r requirements.dev.txt`.

### Install

To install the package locally (in the venv), run `pip install .`. To keep the installed package always in sync with the source code, instead run `pip install -e .`.

### Testing

For unit tests, run `pytest` or `coverage run -m pytest`.

For coverage report, first run `coverage run -m pytest`, then either `coverage report -m` to print to stdout or `coverage html` to generate an HTML report in `htmlcov/`.

### Packaging

Before packaging, check the package configuration by running `pyroma .`

To generate sdist and wheel packages, delete `dist/` and `generic_path.egg-info/` if they exist, then run `python -m build`.

### Config files

- `pyproject.toml` Package metadata, as well as configs for pytest and setuptools
- `requirements.dev.txt` Package dependencies for development, in pip format
- `requirements.publish.txt` Package dependencies for publishing, in pip format

### Troubleshooting

#### Unable to uninstall the local package

Sometimes, if gpath was installed using `pip install .`, pip might have difficulty uninstalling the package, giving the contradictory message
<pre><code>Found existing installation: gpath <var>version</var>
Can't uninstall 'gpath'. No files were found to uninstall.</code></pre>

In this case, manually delete `build/` and `generic_path.egg-info/` if they exist, as well as `Lib/site-packages/gpath.py` and <code>Lib/site-packages/generic_path-<var>version</var>.dist-info/</code>, then verify that pip no longer sees the package by running `pip list`. If the package was installed outside of a local venv, the latter two items would instead be found at the same location where the other pip packages are installed.
