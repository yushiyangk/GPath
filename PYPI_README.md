## PyPI

Make sure that you have an account on both PyPI (https://pypi.org/) and TestPyPI (https://test.pypi.org/). Obtain API keys for both (from https://pypi.org/manage/account/ and https://test.pypi.org/manage/account/).

Create `.pypirc` in the user directory, `~` on Linux and `%USERDIR%` on Windows, with the following format
<pre><code>[pypi]
username = __token__
password = <var>pypi_api_token</var>

[testpypi]
username = __token__
password = <var>testpypi_api_token</var></code></pre>

### Dependencies

Run `pip install -r requirements.publish.txt`.

### Testing

Check that the long description will render correctly on PyPI by running `twine check dist/*`.

Publish to TestPyPI by running `twine upload -r testpypi dist/*`. **Remember** to include `-r testpypi` to avoid uploading to the production PyPI.

Note that once a package of a specific version has been uploaded, no revisions can be made to that version, even on TestPyPI. To get around this, before uploading to TestPyPI, edit the version number with some dummy text, such as by appending <code>.dev<var>n</var></code> for some integer <var>n</var>, and regenerate the packages.

### Publish

If the version number was edited above, revert it to the actual version number, then regenerate the packages.

Run `twine upload dist/*`.

**Warning**: Once a package of a specific version has been uploaded, no revisions can be made to that version. Any further changes can only be made by increasing the version number.
