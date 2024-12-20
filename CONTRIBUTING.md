## Contributing

- [Report an issue](https://github.com/yushiyangk/GPath/issues)
- [Submit a pull request](https://github.com/yushiyangk/GPath/pulls)

## Dev environment

Clone the repository with `git clone https://github.com/yushiyangk/GPath.git`.

The source for the package is `src/`, with tests in `tests/`.

### Virtual environment

Create the venv using `python -m venv .venv`.

To activate the venv, on Linux run `source .venv/bin/activate`, and on Windows run `.venv/Scripts/Activate.ps1` or `.venv/Scripts/activate.bat`.

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

The documentation is generated in `docs/html/`, using template files in `docs/template/`.

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
