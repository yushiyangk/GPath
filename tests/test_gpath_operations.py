from __future__ import annotations

import itertools
from typing import Union

import pytest

from gpath import GPath
from util import TestGPath


class TestGPathOperations(TestGPath):
	@staticmethod
	@pytest.mark.parametrize(
		('gpath1', 'gpath2', 'subpath_expected', 'relpath_expected'),
		[
			("/", "/", "", ""),
			("/", "", None, None),
			("/", "..", None, None),
			("/", "C:/", None, None),
			("/", "C:", None, None),
			("/a", "/", "a", "a"),
			("/a", "/a", "", ""),
			("/a/b", "/", "a/b", "a/b"),
			("/a/b", "/a", "b", "b"),
			("/a/b", "/b", None, "../a/b"),

			("", "/", None, None),
			("", "", "", ""),
			("", "..", None, None),
			("", "C:/", None, None),
			("", "C:", None, None),
			("", "a", None, ".."),
			("", "../a", None, None),
			("a", "", "a", "a"),
			("a", "a", "", ""),
			("a", "..", None, None),
			("a", "../a", None, None),
			("a/b", "", "a/b", "a/b"),
			("a/b", "a", "b", "b"),
			("a/b", "b", None, "../a/b"),

			("..", "/", None, None),
			("..", "", None, ".."),
			("..", "..", "", ""),
			("..", "../..", None, None),
			("..", "C:/", None, None),
			("..", "C:", None, None),
			("..", "a", None, "../.."),
			("..", "../a", None, ".."),
			("../a", "..", "a", "a"),
			("../a", "../a", "", ""),
			("../a", "", None, "../a"),
			("../a", "a", None, "../../a"),
			("../a/b", "..", "a/b", "a/b"),
			("../a/b", "../a", "b", "b"),
			("../a/b", "../b", None, "../a/b"),

			("../..", "/", None, None),
			("../..", "", None, "../.."),
			("../..", "..", None, ".."),
			("../..", "../..", "", ""),
			("../..", "C:/", None, None),
			("../..", "C:", None, None),
			("../..", "a", None, "../../.."),
			("../..", "../a", None, "../.."),
			("../..", "../../a", None, ".."),
			("../../a", "../..", "a", "a"),
			("../../a", "../../a", "", ""),
			("../../a", "..", None, "../a"),
			("../../a", "../a", None, "../../a"),
			("../../a", "", None, "../../a"),
			("../../a", "a", None, "../../../a"),
			("../../a/b", "../..", "a/b", "a/b"),
			("../../a/b", "../../a", "b", "b"),
			("../../a/b", "../../b", None, "../a/b"),

			("C:/", "/", None, None),
			("C:/", "", None, None),
			("C:/", "..", None, None),
			("C:/", "C:/", "", ""),
			("C:/", "D:/", None, None),
			("C:/", "C:", None, None),
			("C:/a", "C:/", "a", "a"),
			("C:/a", "C:/a", "", ""),
			("C:/a/b", "C:/", "a/b", "a/b"),
			("C:/a/b", "C:/a", "b", "b"),
			("C:/a/b", "D:/a", None, None),
			("C:/a/b", "C:/b", None, "../a/b"),

			("C:", "/", None, None),
			("C:", "", None, None),
			("C:", "..", None, None),
			("C:", "C:/", None, None),
			("C:", "C:", "", ""),
			("C:", "D:", None, None),
			("C:a", "C:", "a", "a"),
			("C:a", "C:a", "", ""),
			("C:a/b", "C:", "a/b", "a/b"),
			("C:a/b", "C:a", "b", "b"),
			("C:a/b", "D:a", None, None),
			("C:a/b", "C:b", None, "../a/b"),
		],
		indirect=['gpath1', 'gpath2']
	)
	def test_subpath_relpath(gpath1: GPath, gpath2: GPath, subpath_expected: str, relpath_expected: Union[str, GPath]):
		"""
			Test `subpath_from()` and `relpath_from()`.
		"""
		if subpath_expected is not None:
			subpath_expected_gpath = GPath(subpath_expected)
		else:
			subpath_expected_gpath = None

		if relpath_expected is not None:
			relpath_expected_gpath = GPath(relpath_expected)
		else:
			relpath_expected_gpath = None

		result = gpath1.subpath_from(gpath2)
		assert result == subpath_expected_gpath

		if subpath_expected_gpath is not None:
			assert relpath_expected_gpath is not None

			if gpath1 != gpath2:
				result = gpath2.subpath_from(gpath1)
				assert result == None

		result = gpath1.relpath_from(gpath2)
		assert result == relpath_expected_gpath


	@staticmethod
	@pytest.mark.parametrize(
		('gpath1', 'expected'),
		[
			("/", True),
			("", False),
			("..", False),
			("C:/", True),
			("C:", False),
			("C:..", False),
			("/a", False),
			("a", False),
			("../a", False),
			("C:/a", False),
			("C:a", False),
			("C:../a", False),
		],
		indirect=['gpath1']
	)
	def test_root(gpath1: GPath, expected: bool):
		"""
			Test property getter for `root`.
		"""
		result = gpath1.root
		assert result == expected


	@staticmethod
	@pytest.mark.parametrize(
		('gpath1', 'expected_parent_parts', 'expected_relative_parts'),
		[
			("/", [], []),
			("/a", [], ["a"]),
			("/a/b", [], ["a", "b"]),
			("", [], []),
			("a", [], ["a"]),
			("a/b", [], ["a", "b"]),
			("..", [".."], [".."]),
			("../a", [".."], ["..", "a"]),
			("../a/b", [".."], ["..", "a", "b"]),
			("../..", ["..", ".."], ["..", ".."]),
			("../../a", ["..", ".."], ["..", "..", "a"]),
			("../../a/b", ["..", ".."], ["..", "..", "a", "b"]),
			("C:/", [], []),
			("C:/a", [], ["a"]),
			("C:/a/b", [], ["a", "b"]),
			("C:", [], []),
			("C:a", [], ["a"]),
			("C:a/b", [], ["a", "b"]),
			("C:..", [".."], [".."]),
			("C:../a", [".."], ["..", "a"]),
			("C:../a/b", [".."], ["..", "a", "b"]),
			("C:../..", ["..", ".."], ["..", ".."]),
			("C:../../a", ["..", ".."], ["..", "..", "a"]),
			("C:../../a/b", ["..", ".."], ["..", "..", "a", "b"]),
		],
		indirect=['gpath1']
	)
	def test_parent_relative_parts(gpath1: GPath, expected_parent_parts: list[str], expected_relative_parts: list[str]):
		"""
			Test property getters for `parent_parts` and `relative_parts`.
		"""
		assert gpath1.parent_parts == expected_parent_parts
		assert gpath1.relative_parts == expected_relative_parts


	@staticmethod
	@pytest.mark.parametrize(
		('gpath1', 'parent_level', 'expected_gpath'),
		[
			("/", None, ""),
			("/", 0, ""),
			("/", 2, "../.."),
			("/a/b", None, "a/b"),
			("/a/b", 0, "a/b"),
			("/a/b", 2, "../../a/b"),

			("", None, ""),
			("", 0, ""),
			("", 2, "../.."),
			("a/b", None, "a/b"),
			("a/b", 0, "a/b"),
			("a/b", 2, "../../a/b"),

			("..", None, ".."),
			("..", 0, ""),
			("..", 2, "../.."),
			("../a/b", None, "../a/b"),
			("../a/b", 0, "a/b"),
			("../a/b", 2, "../../a/b"),

			("C:/", None, "C:"),
			("C:/", 0, "C:"),
			("C:/", 2, "C:../.."),
			("C:/a/b", None, "C:a/b"),
			("C:/a/b", 0, "C:a/b"),
			("C:/a/b", 2, "C:../../a/b"),

			("C:", None, "C:"),
			("C:", 0, "C:"),
			("C:", 2, "C:../.."),
			("C:a/b", None, "C:a/b"),
			("C:a/b", 0, "C:a/b"),
			("C:a/b", 2, "C:../../a/b"),
		],
		indirect=['gpath1', 'expected_gpath']
	)
	def test_as_relative(gpath1: GPath, parent_level: int, expected_gpath: GPath):
		"""
			Test `as_relative()`.
		"""
		result = gpath1.as_relative(parent_level)
		assert result == expected_gpath


	@staticmethod
	@pytest.mark.parametrize(
		('gpath1', 'expected_gpath'),
		[
			("/", "/"),
			("/a/b", "/a/b"),
			("", "/"),
			("a/b", "/a/b"),
			("..", "/"),
			("../a/b", "/a/b"),
			("C:/", "C:/"),
			("C:/a/b", "C:/a/b"),
			("C:", "C:/"),
			("C:a/b", "C:/a/b"),
		],
		indirect=['gpath1', 'expected_gpath']
	)
	def test_as_absolute(gpath1: GPath, expected_gpath: GPath):
		"""
			Test `as_absolute()`.
		"""
		result = gpath1.as_absolute()
		assert result == expected_gpath


	@staticmethod
	@pytest.mark.parametrize(
		('gpath1', 'drive', 'expected_gpath', 'unset_expected'),
		[
			("/", "K", "K:/", "/"),
			("/a/b", "K", "K:/a/b", "/a/b"),
			("", "K", "K:", ""),
			("a/b", "K", "K:a/b", "a/b"),
			("..", "K", "K:..", ".."),
			("../a/b", "K", "K:../a/b", "../a/b"),
			("C:/", "K", "K:/", "/"),
			("C:/a/b", "K", "K:/a/b", "/a/b"),
			("C:", "K", "K:", ""),
			("C:a/b", "K", "K:a/b", "a/b"),
		],
		indirect=['gpath1', 'expected_gpath']
	)
	def test_with_drive(gpath1: GPath, drive: str, expected_gpath: GPath, unset_expected: str):
		"""
			Test `with_drive()` and `without_drive`.
		"""
		result = gpath1.with_drive(drive)
		assert result == expected_gpath

		unset_expected_gpath = GPath(unset_expected)
		for unset in ["", None]:
			result = gpath1.with_drive(unset)
			assert result == unset_expected_gpath
		result = gpath1.without_drive()
		assert result == unset_expected_gpath


	@staticmethod
	@pytest.mark.parametrize(
		('gpath1'),
		[
			("/"),
			("/a/b"),
			(""),
			("a/b"),
			(".."),
			("../a/b"),
			("C:/"),
			("C:/a/b"),
			("C:"),
			("C:a/b"),
		],
		indirect=['gpath1']
	)
	@pytest.mark.parametrize(('drive'), ["CC", 1, False])
	def test_with_drive_invalid(gpath1: GPath, drive: str):
		"""
			Test `with_drive()` when `drive` is longer than one character
		"""
		if isinstance(drive, str):
			with pytest.raises(ValueError):
				gpath1.with_drive(drive)
		else:
			with pytest.raises(TypeError):
				gpath1.with_drive(drive)


	@staticmethod
	@pytest.mark.parametrize(
		#('path1', 'path2', 'allow_current', 'allow_parents', 'expected_path'),
		('path1', 'path2', 'allow_current_expected', 'allow_parents_expected', 'allow_current_parent_expected', 'no_common_expected'),
		[
			("/", "/", "/", "/", "/", "/"),
			("/", "", None, None, None, None),
			("/", "..", None, None, None, None),
			("/", "C:/", None, None, None, None),
			("/", "C:", None, None, None, None),
			("/", "/a", "/", "/", "/", "/"),
			("/", "a", None, None, None, None),
			("/", "../a", None, None, None, None),
			("/a", "/", "/", "/", "/", "/"),
			("/a", "", None, None, None, None),
			("/a", "..", None, None, None, None),
			("/a", "C:/", None, None, None, None),
			("/a", "C:", None, None, None, None),
			("/a", "/b", "/", "/", "/", "/"),
			("/a", "b", None, None, None, None),
			("/a", "../b", None, None, None, None),

			("", "", "", "", "", ""),
			("", "..", None, "..", "..", None),
			("", "C:/", None, None, None, None),
			("", "C:", None, None, None, None),
			("", "a", "", "", "", None),
			("", "../a", None, "..", "..", None),
			#("a", "", "", "", "", None),
			("a", "..", None, "..", "..", None),
			("a", "C:/", None, None, None, None),
			("a", "C:", None, None, None, None),
			("a", "b", "", "", "", None),
			("a", "../b", None, "..", "..", None),

			("..", "..", "..", "..", "..", ".."),
			("..", "../..", None, "../..", "../..", None),
			("..", "C:/", None, None, None, None),
			("..", "C:", None, None, None, None),
			("..", "../a", "..", "..", "..", ".."),
			("..", "../../a", None, "../..", "../..", None),
			("../a", "..", "..", "..", "..", ".."),
			("../a", "../..", None, "../..", "../..", None),
			("../a", "C:/", None, None, None, None),
			("../a", "C:", None, None, None, None),
			("../a", "../b", "..", "..", "..", ".."),
			("../a", "../../b", None, "../..", "../..", None),

			("C:/", "C:/", "C:/", "C:/", "C:/", "C:/"),
			("C:/", "C:", None, None, None, None),
			("C:/", "D:/", None, None, None, None),
			("C:/", "D:", None, None, None, None),
			("C:/a", "C:/", "C:/", "C:/", "C:/", "C:/"),
			("C:/a", "C:", None, None, None, None),
			("C:/a", "D:/", None, None, None, None),
			("C:/a", "D:", None, None, None, None),
			("C:/a", "C:/b", "C:/", "C:/", "C:/", "C:/"),
		]
	)
	def test_common_with(
		path1: str,
		path2: str,
		allow_current_expected: str,
		allow_parents_expected: str,
		allow_current_parent_expected: str,
		no_common_expected: str
	):
		"""
			Test `common_with()` and `__and__()`.
		"""
		assert allow_parents_expected == allow_current_parent_expected

		if allow_current_expected is not None:
			allow_current_expected_gpath = GPath(allow_current_expected)
		else:
			allow_current_expected_gpath = None

		if allow_parents_expected is not None:
			allow_parents_expected_gpath = GPath(allow_parents_expected)
		else:
			allow_parents_expected_gpath = None

		if allow_current_parent_expected is not None:
			allow_current_parent_expected_gpath = GPath(allow_current_parent_expected)
		else:
			allow_current_parent_expected_gpath = None

		if no_common_expected is not None:
			no_common_expected_gpath = GPath(no_common_expected)
		else:
			no_common_expected_gpath = None

		for lhs, rhs in itertools.chain(itertools.product([path1], [path2, GPath(path2)]), itertools.product([path2], [path1, GPath(path1)])):
			gpath = GPath(lhs)

			result = gpath.common_with(rhs)
			assert result == allow_current_expected_gpath
			result = gpath & rhs
			assert result == allow_current_expected_gpath

			result = gpath.common_with(rhs, allow_current=True, allow_parents=False)
			assert result == allow_current_expected_gpath

			result = gpath.common_with(rhs, allow_current=False, allow_parents=True)
			assert result == allow_parents_expected_gpath

			result = gpath.common_with(rhs, allow_current=True, allow_parents=True)
			assert result == allow_current_parent_expected_gpath

			result = gpath.common_with(rhs, allow_current=False, allow_parents=False)
			assert result == no_common_expected_gpath
