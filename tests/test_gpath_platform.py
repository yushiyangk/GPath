from __future__ import annotations

import pytest

from gpath import GPath
from gpath.platform import Platform
from util import TestGPath, RenderableData

class TestGPathEncoding(TestGPath):
	@staticmethod
	@pytest.mark.parametrize(
		('path', 'generic_expected', 'posix_expected', 'windows_expected'),
		[
			("",
    			RenderableData([], False, "", 0),
				RenderableData([], False, "", 0),
				RenderableData([], False, "", 0)
			),
			("a/b",
    			RenderableData(["a", "b"], False, "", 0),
				RenderableData(["a", "b"], False, "", 0),
				RenderableData(["a", "b"], False, "", 0)
			),
			("a\\b",
    			RenderableData(["a", "b"], False, "", 0),
				RenderableData(["a\\b"], False, "", 0),
				RenderableData(["a", "b"], False, "", 0)
			),
			("/",
    			RenderableData([], True, "", 0),
				RenderableData([], True, "", 0),
				RenderableData([], True, "", 0)
			),
			("\\",
    			RenderableData([], True, "", 0),
				RenderableData(["\\"], False, "", 0),
				RenderableData([], True, "", 0)
			),
			("/a/b",
    			RenderableData(["a", "b"], True, "", 0),
				RenderableData(["a", "b"], True, "", 0),
				RenderableData(["a", "b"], True, "", 0)
			),
			("\\a\\b",
    			RenderableData(["a", "b"], True, "", 0),
				RenderableData(["\\a\\b"], False, "", 0),
				RenderableData(["a", "b"], True, "", 0)
			),
			("..",
    			RenderableData([], False, "", 1),
				RenderableData([], False, "", 1),
				RenderableData([], False, "", 1)
			),
			("../..",
    			RenderableData([], False, "", 2),
				RenderableData([], False, "", 2),
				RenderableData([], False, "", 2)
			),
			("..\\..",
    			RenderableData([], False, "", 2),
				RenderableData(["..\\.."], False, "", 0),
				RenderableData([], False, "", 2)
			),
			("C:",
    			RenderableData([], False, "C", 0),
				RenderableData(["C:"], False, "", 0),
				RenderableData([], False, "C", 0)
			),
			("C:/",
    			RenderableData([], True, "C", 0),
				RenderableData(["C:"], False, "", 0),
				RenderableData([], True, "C", 0)
			),
			("C:\\",
    			RenderableData([], True, "C", 0),
				RenderableData(["C:\\"], False, "", 0),
				RenderableData([], True, "C", 0)
			),
		]
	)
	def test_platform(
		path: str,
		generic_expected: RenderableData,
		posix_expected: RenderableData,
		windows_expected: RenderableData,
	):
		"""
			Test constructor with different platforms and test their propagation
		"""
		for platform, expected in [
			(Platform.GENERIC, generic_expected),
			(Platform.POSIX, posix_expected),
			(Platform.WINDOWS, windows_expected),
		]:
			gpath = GPath(path, platform=platform)
			assert gpath.absolute == expected.absolute
			assert gpath.drive == expected.drive
			assert gpath.named_parts == expected.named_parts
			assert gpath.parent_level == expected.parent_level
			assert gpath.platform == str(platform)

			# Test copy propagation
			gpath_copy = GPath(gpath)
			assert gpath_copy.platform == str(platform)

			# Test copy with override
			gpath_copy = GPath(gpath, platform=Platform.GENERIC)
			assert gpath_copy.platform == str(Platform.GENERIC)

			# Test left-operand propagation
			gpath_result = gpath + "a"
			assert gpath_result.platform == str(platform)
			gpath_result = gpath + GPath("a", platform=Platform.GENERIC)
			assert gpath_result.platform == str(platform)

			# Test right-operand propagation
			default_encoding_gpath = GPath(path)
			assert default_encoding_gpath.platform == None
			gpath_result = default_encoding_gpath + "a"
			assert default_encoding_gpath.platform == None
			gpath_result = gpath + GPath("a", platform=platform)
			assert gpath_result.platform == str(platform)
