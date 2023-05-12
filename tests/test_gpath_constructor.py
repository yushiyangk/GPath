from __future__ import annotations

from typing import Optional

import pytest

from gpath import GPath
from util import TestGPath


class TestGPathConstructor(TestGPath):
	@staticmethod
	@pytest.mark.parametrize(
		('path', 'expected_parts', 'expected_drive', 'expected_root', 'expected_parent_level'),
		[
			(None, tuple(), "", False, 0),
			("", tuple(), "", False, 0),
			(".", tuple(), "", False, 0),
			("./", tuple(), "", False, 0),
			("./.", tuple(), "", False, 0),
			(".//", tuple(), "", False, 0),
			("/", tuple(), "", True, 0),
			("/.", tuple(), "", True, 0),
			("/..", tuple(), "", True, 0),
			("/./", tuple(), "", True, 0),
			("/./.", tuple(), "", True, 0),
			("/.//", tuple(), "", True, 0),
			("/./..", tuple(), "", True, 0),
			("C:/", tuple(), "C", True, 0),
			("C:/.", tuple(), "C", True, 0),
			("C:/./.", tuple(), "C", True, 0),
			("C:/.//", tuple(), "C", True, 0),
			("C:", tuple(), "C", False, 0),
			("C:.", tuple(), "C", False, 0),
			("C:./.", tuple(), "C", False, 0),
			("C:.//", tuple(), "C", False, 0),
			("c:/", tuple(), "c", True, 0),
			("c:", tuple(), "c", False, 0),
		]
	)
	def test_constructor_root(
		path: Optional[str],
		expected_parts: tuple[str, ...],
		expected_drive: str,
		expected_root: bool,
		expected_parent_level: int,
	):
		"""
			Test constructor `__init__()` as well as property getters for `absolute`, `drive`, `named_parts`, `parent_level` and `encoding`, for paths requiring special treatment.
		"""
		if path is None:
			gpath = GPath()
		else:
			gpath = GPath(path)

		assert gpath._parts == expected_parts
		assert gpath._drive == expected_drive
		assert gpath._root == expected_root
		assert gpath._parent_level == expected_parent_level
		assert gpath._encoding == None

		assert gpath.absolute == expected_root
		assert gpath.drive == expected_drive
		assert gpath.named_parts == list(expected_parts)
		assert gpath.parent_level == expected_parent_level
		assert gpath.encoding == None

		gpath_copy = GPath(gpath)
		assert gpath_copy._parts == expected_parts
		assert gpath_copy._drive == expected_drive
		assert gpath_copy._root == expected_root
		assert gpath_copy._parent_level == expected_parent_level
		assert gpath_copy._encoding == None

		assert gpath_copy.absolute == expected_root
		assert gpath_copy.drive == expected_drive
		assert gpath_copy.named_parts == list(expected_parts)
		assert gpath_copy.parent_level == expected_parent_level
		assert gpath_copy.encoding == None


	@staticmethod
	@pytest.mark.parametrize(
		('path', 'expected_parts', 'expected_parent_level'),
		[
			("..", tuple(), 1),
			("../..", tuple(), 2),
			("bin", ("bin", ), 0),
			("usr/bin", ("usr", "bin"), 0),
			("../usr/bin", ("usr", "bin"), 1),
			("../../usr/bin", ("usr", "bin"), 2),
			("./usr/bin", ("usr", "bin"), 0),
			("././usr/bin", ("usr", "bin"), 0),
			("usr/./bin", ("usr", "bin"), 0),
			("usr/././bin", ("usr", "bin"), 0),
			("././usr/././bin", ("usr", "bin"), 0),
			("usr/../bin", ("bin", ), 0),
			("usr/../../bin", ("bin", ), 1),
			("usr/././../bin", ("bin", ), 0),
			("usr/././../../bin", ("bin", ), 1),
			("usr/../././../bin", ("bin", ), 1),
			("initrd.img", ("initrd.img", ), 0),
			("home/username/Documents/Secret Documents/Secret Document.txt", ("home", "username", "Documents", "Secret Documents", "Secret Document.txt"), 0),
			("Windows/System32", ("Windows", "System32"), 0),
			("directory/français", ("directory", "français"), 0),
			("directory/ελληνικά", ("directory", "ελληνικά"), 0),
			("directory/русский язык", ("directory", "русский язык"), 0),
			("directory/中文", ("directory", "中文"), 0),
			("directory/اَلْعَرَبِيَّةُ", ("directory", "اَلْعَرَبِيَّةُ"), 0),
		]
	)
	@pytest.mark.parametrize('path_suffix', ["", "/", "//", "/.", "/./", "/././/"])
	@pytest.mark.parametrize(
		('path_prefix', 'expected_drive', 'expected_root'),
		[
			("", "", False),
			("/", "", True),
			#("//", "", True),
			("C:/", "C", True),
			("c:/", "c", True),
			("C:", "C", False),
			("1:", "1", False),
			("::", ":", False),
		]
	)
	def test_constructor(
		path: str,
		path_prefix: str,
		path_suffix: str,
		expected_parts: tuple[str, ...],
		expected_drive: str,
		expected_root: bool,
		expected_parent_level: int,
	):
		"""
			Test constructor `__init__()` as well as property getters for `absolute`, `device`, `named_parts`, `parent_level` and `encoding`.
		"""
		gpath = GPath(path_prefix + path + path_suffix)
		if expected_root and expected_parent_level > 0:
			expected_parent_level = 0

		assert gpath._parts == expected_parts
		assert gpath._drive == expected_drive
		assert gpath._root == expected_root
		assert gpath._parent_level == expected_parent_level

		assert gpath.absolute == expected_root
		assert gpath.drive == expected_drive
		assert gpath.named_parts == list(expected_parts)
		assert gpath.parent_level == expected_parent_level

		gpath_copy = GPath(gpath)

		assert gpath_copy._parts == expected_parts
		assert gpath_copy._drive == expected_drive
		assert gpath_copy._root == expected_root
		assert gpath_copy._parent_level == expected_parent_level

		assert gpath_copy.absolute == expected_root
		assert gpath_copy.drive == expected_drive
		assert gpath_copy.named_parts == list(expected_parts)
		assert gpath_copy.parent_level == expected_parent_level
