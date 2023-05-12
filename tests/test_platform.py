from __future__ import annotations

from gpath.platform import Platform, platform_names

def test_common_platforms():
	"""
		Test the existence of common platforms.
	"""
	linux_platform = Platform.from_str('linux')
	windows_platform = Platform.from_str('windows')
	macos_platform = Platform.from_str('macos')
	assert linux_platform == macos_platform
	assert windows_platform != linux_platform

def test_platform_names():
	"""
		Test `platform_names` and `Platform.from_str()` for different platforms
	"""
	for name in platform_names:
		expected = platform_names[name]
		result = Platform.from_str(name)
		assert expected == result
