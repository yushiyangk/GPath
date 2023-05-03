from __future__ import annotations

import pytest

from gpath import GPath


# Type hinting prior to 3.10
# Using generics in built-in collections, e.g. list[int], is supported from 3.7 by __future__.annotations
from typing import Optional, Union


class TestGPath:

	@pytest.fixture
	def gpath1(self, request: pytest.FixtureRequest) -> GPath:
		return GPath(request.param)

	@pytest.fixture
	def gpath2(self, request: pytest.FixtureRequest) -> GPath:
		return GPath(request.param)

	@pytest.fixture
	def expected_gpath(self, request: pytest.FixtureRequest) -> Optional[GPath]:
		if request.param is None:
			return None
		else:
			return GPath(request.param)


	@pytest.mark.parametrize(
		('path', 'expected_parts', 'expected_device', 'expected_absolute', 'expected_parent'),
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
			("C:/", tuple(), "C:", True, 0),
			("C:/.", tuple(), "C:", True, 0),
			("c:/", tuple(), "c:", True, 0),
		]
	)
	def test_constructor_root(self,
		path: Optional[str],
		expected_parts: tuple[str, ...],
		expected_device: str,
		expected_absolute: bool,
		expected_parent: int,
	):
		"""
			Test constructor `__init__()` as well as property getters for `absolute`, `device`, `named_parts` and `parent_level`, for paths requiring special treatment.
		"""
		if path is None:
			gpath = GPath()
		else:
			gpath = GPath(path)

		if expected_absolute and expected_parent > 0:
			expected_parent = 0

		assert gpath._parts == expected_parts
		assert gpath._device == expected_device
		assert gpath._absolute == expected_absolute
		assert gpath._parent == expected_parent

		assert gpath.absolute == expected_absolute
		assert gpath.device == expected_device
		assert gpath.named_parts == list(expected_parts)
		assert gpath.parent_level == expected_parent

		gpath_copy = GPath(gpath)
		assert gpath_copy._parts == expected_parts
		assert gpath_copy._device == expected_device
		assert gpath_copy._absolute == expected_absolute
		assert gpath_copy._parent == expected_parent

		assert gpath_copy.absolute == expected_absolute
		assert gpath_copy.device == expected_device
		assert gpath_copy.named_parts == list(expected_parts)
		assert gpath_copy.parent_level == expected_parent


	@pytest.mark.parametrize(
		('path', 'expected_parts', 'expected_parent'),
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
		('path_prefix', 'expected_device', 'expected_absolute'),
		[
			("", "", False),
			("/", "", True),
			#("//", "", True),
			("C:/", "C:", True),
			("c:/", "c:", True),
			#("C:", "C:", False),
		]
	)
	def test_constructor(self,
		path: str,
		path_prefix: str,
		path_suffix: str,
		expected_parts: tuple[str, ...],
		expected_device: str,
		expected_absolute: bool,
		expected_parent: int,
	):
		"""
			Test constructor `__init__()` as well as property getters for `absolute`, `device`, `named_parts` and `parent_level`.
		"""
		gpath = GPath(path_prefix + path + path_suffix)
		if expected_absolute and expected_parent > 0:
			expected_parent = 0

		assert gpath._parts == expected_parts
		assert gpath._device == expected_device
		assert gpath._absolute == expected_absolute
		assert gpath._parent == expected_parent

		assert gpath.absolute == expected_absolute
		assert gpath.device == expected_device
		assert gpath.named_parts == list(expected_parts)
		assert gpath.parent_level == expected_parent

		gpath_copy = GPath(gpath)

		assert gpath_copy._parts == expected_parts
		assert gpath_copy._device == expected_device
		assert gpath_copy._absolute == expected_absolute
		assert gpath_copy._parent == expected_parent

		assert gpath_copy.absolute == expected_absolute
		assert gpath_copy.device == expected_device
		assert gpath_copy.named_parts == list(expected_parts)
		assert gpath_copy.parent_level == expected_parent


	@pytest.mark.parametrize(
		('gpath1', 'expected'),
		[
			("/", True),
			("", False),
			("..", False),
			("C:/", True),
			("/a", False),
			("a", False),
			("../a", False),
			("C:/a", False),
		],
		indirect=['gpath1']
	)
	def test_root(self, gpath1: GPath, expected: bool):
		"""
			Test property getter for `root`.
		"""
		result = gpath1.root
		assert result == expected


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
		],
		indirect=['gpath1']
	)
	def test_parent_relative_parts(self, gpath1: GPath, expected_parent_parts: list[str], expected_relative_parts: list[str]):
		"""
			Test property getters for `parent_parts` and `relative_parts`.
		"""
		assert gpath1.parent_parts == expected_parent_parts
		assert gpath1.relative_parts == expected_relative_parts


	@pytest.mark.parametrize(
		('path1', 'path2', 'expected'),
		[
			("/", "/", True),
			("", "", True),
			("..", "..", True),
			("C:/", "C:/", True),
			("/", "", False),
			("..", "", False),
			("..", "/", False),
			("..", "../..", False),
			("C:/", "c:/", False),
			("C:/", "D:/", False),
			("/usr/bin", "/usr/bin", True),
			("/usr/bin", "/usr/./bin", True),
			("usr/bin", "usr/bin", True),
			("usr/bin", "usr/./bin", True),
			("/usr/bin", "/../usr/bin", True),
			("usr/bin", "../usr/bin", False),
			("../usr/bin", "../usr/bin", True),
			("../usr/bin", "../../usr/bin", False),
			("../../usr/bin", "../../usr/bin", True),
			("bin", "/bin", False),
			("bin", "bin", True),
			("bin", "usr", False),
			("bin", "biñ", False),
			("bin", "usr/bin", False),
			("C:/Windows", "C:/Windows", True),
			("C:/Windows", "C:/./Windows", True),
			("C:/Windows", "C:/../Windows", True),
			("C:/Windows", "D:/Windows", False),
			("C:/Windows", "c:/Windows", False),
			("C:/Windows", "/Windows", False),
			("C:/Windows", "Windows", False),
			("C:/Windows", "C:/Windows/System32", False),
		]
	)
	def test_eq_hash(self, path1: str, path2: str, expected: bool):
		"""
			Test `__eq__()` and `__hash__()`.
		"""
		gpath1 = GPath(path1)
		gpath2 = GPath(path2)
		result = gpath1 == gpath2
		assert result == expected
		result = gpath2 == gpath1
		assert result == expected

		result = gpath1 == path2
		assert result == False
		result = gpath2 == path1
		assert result == False

		if expected is True:
			assert hash(gpath1) == hash(gpath2)
		else:
			assert hash(gpath1) != hash(gpath2)


	@pytest.mark.parametrize(
		('gpath1', 'gpath2', 'gt_expected', 'eq_expected'),
		[
			("/", "/", False, True),
			("/a/b", "/a/b", False, True),
			("", "", False, True),
			("a/b", "a/b", False, True),
			("..", "..", False, True),
			("../..", "../..", False, True),
			("../../a/b", "../../a/b", False, True),
			("C:/", "C:/", False, True),
			("C:/a/b", "C:/a/b", False, True),

			("", "/", True, False),
			("", "..", True, False),
			("..", "/", True, False),
			("..", "../..", True, False),
			("C:/", "/", True, False),
			("", "C:/", True, False),
			("..", "C:/", True, False),

			("b", "a", True, False),
			("aa", "a", True, False),
			("a", "", True, False),
			("a", "..", True, False),
			("a", "/", True, False),
			("a/b", "a/a", True, False),
			("b/a", "a/b", True, False),

			("/b", "/a", True, False),
			("/aa", "/a", True, False),
			("/a", "/", True, False),
			("", "/a", True, False),
			("..", "/a", True, False),
			("/a/b", "/a/a", True, False),
			("/b/a", "/a/b", True, False),

			("../b", "../a", True, False),
			("../aa", "../a", True, False),
			("../a", "..", True, False),
			("../a", "/", True, False),
			("", "../a", True, False),
			("../a/b", "../a/a", True, False),
			("../b/a", "../a/b", True, False),
			("../a", "../../b", True, False),

			("D:/", "C:/", True, False),
			("CC:/", "C:/", True, False),
			("C:/b", "C:/a", True, False),
			("C:/aa", "C:/a", True, False),
			("C:/a", "C:/", True, False),
			("D:/", "C:/a", True, False),
			("C:/a", "/", True, False),
			("", "C:/a", True, False),
			("..", "C:/a", True, False),
			("C:/a/b", "C:/a/a", True, False),
			("C:/b/a", "C:/a/b", True, False),
		],
		indirect=['gpath1', 'gpath2']
	)
	def test_gt_lt_gte_lte(self, gpath1: GPath, gpath2: GPath, gt_expected: bool, eq_expected: bool):
		"""
			Test `__gt__()`, `__lt__()`, `__gte__()` and `__lte__()`, which are automatically generated based on the definition of `__gt__()` (and `__eq__()`).
		"""
		lt_expected = ((not gt_expected) and (not eq_expected))
		gte_expected = gt_expected or eq_expected
		lte_expected = lt_expected or eq_expected

		result = gpath1 == gpath2
		assert result == eq_expected

		result = gpath1 > gpath2
		assert result == gt_expected
		result = gpath2 < gpath1
		assert result == gt_expected

		result = gpath2 > gpath1
		assert result == lt_expected
		result = gpath1 < gpath2
		assert result == lt_expected

		result = gpath1 >= gpath2
		assert result == gte_expected
		result = gpath2 <= gpath1
		assert result == gte_expected

		result = gpath2 >= gpath1
		assert result == lte_expected
		result = gpath1 <= gpath2
		assert result == lte_expected


	@pytest.mark.parametrize(
		('gpath1', 'expected'),
		[
			("/", True),
			("", False),
			("..", True),
			("../..", True),
			("C:/", True),

			("/a", True),
			("a", True),
			("../a", True),
			("C:/a", True),
		],
		indirect=['gpath1']
	)
	def test_bool(self, gpath1: GPath, expected: bool):
		"""
			Test `__bool__()`.
		"""
		result = bool(gpath1)
		assert result == expected
		result = not gpath1
		assert result == (not expected)


	@pytest.mark.parametrize(
		('path'),
		[
			("/"),
			("."),
			(".."),
			("../.."),
			("C:/"),
			("/a"),
			("/a/b"),
			("a"),
			("a/b"),
			("../a"),
			("../a/b"),
			("C:/a"),
			("C:/a/b"),
		]
	)
	def test_str_repr(self, path: str):
		"""
			Test `__str__()` and `__repr__()`.
		"""
		gpath = GPath(path)
		result = str(gpath)
		assert result == path

		result = repr(gpath)
		result_eval = eval(result)
		assert result_eval == gpath


	@pytest.mark.parametrize(
		('gpath1', 'expected'),
		[
			("/", 0),
			("", 0),
			("..", 0),
			("../..", 0),
			("C:/", 0),
			("/a", 1),
			("/a/b", 2),
			("a", 1),
			("a/b", 2),
			("../a", 1),
			("../a/b", 2),
			("C:/a", 1),
			("C:/a/b", 2),
		],
		indirect=['gpath1']
	)
	def test_len(self, gpath1: GPath, expected: int):
		"""
			Test `__len__()`.
		"""
		result = len(gpath1)
		assert result == expected


	@pytest.mark.parametrize(
		('gpath1', 'expected_list'),
		[
			("/", []),
			("", []),
			("..", []),
			("../..", []),
			("C:/", []),
			("/a", ["a"]),
			("/a/b", ["a", "b"]),
			("a", ["a"]),
			("a/b", ["a", "b"]),
			("../a", ["a"]),
			("../a/b", ["a", "b"]),
			("C:/a", ["a"]),
			("C:/a/b", ["a", "b"]),
		],
		indirect=['gpath1']
	)
	@pytest.mark.parametrize(
		('index'),
		[
			0, 1, 2, -1, -2, -3,
			slice(0), slice(1), slice(-1),
			slice(None, 0), slice(None, 1), slice(None, -1),
			slice(1, 1), slice(1, 2), slice(1, -1),
			slice(-2, 1), slice(-2, 2), slice(-2, -1),
			slice(0, 1, 2), slice(0, 2, 2), slice(0, -1, 2),
		]
	)
	def test_getitem_iter(self, gpath1: GPath, index: Union[int, slice], expected_list: list[str]):
		"""
			Test `__getitem__()`, for both indexing and slicing, and `__iter__()`.
		"""
		try:
			expected = expected_list[index]
			result = gpath1[index]
			assert result == expected
		except IndexError:
			with pytest.raises(IndexError):
				gpath1[index]

		if index == 0:
			iter_result = iter(gpath1)
			i = 0
			for iter_item in iter_result:
				assert iter_item == expected_list[i]
				i += 1


	@pytest.mark.parametrize(
		('gpath1', 'gpath2', 'expected'),
		[
			("/", "", False),
			("", "/", False),
			("/", "..", False),
			("..", "/", False),
			("C:/", "/", False),
			("/", "C:/", False),
			("C:/", "", False),
			("", "C:/", False),
			("C:/", "..", False),
			("..", "C:/", False),
			("C:/", "D:/", False),
			("D:/", "C:/", False),

			("a", "b", False),
			("b", "a", False),
			("/a", "/b", False),
			("/b", "/a", False),
			("../a", "../b", False),
			("../b", "../a", False),
			("C:/a", "C:/b", False),
			("C:/b", "C:/a", False),

			("..", "", True),
			("../..", "", True),
			("../..", "..", True),
			("", "a", True),
			("..", "a", True),
			("../..", "a", True),
			("..", "../a", True),
			("../..", "../a", True),
			("../a", "a", False),
			("a", "../a", False),

			("a", "a/b", True),
			("/a", "/a/b", True),
			("../a", "../a/b", True),
			("C:/a", "C:/a/b", True),

			("a", "a", True),
			("/a", "/a", True),
			("../a", "../a", True),
			("C:/a", "C:/a", True),
		],
		indirect=['gpath1', 'gpath2']
	)
	def test_contains(self, gpath1: GPath, gpath2: GPath, expected: bool):
		"""
			Test `__contains__()`.
		"""
		result = gpath2 in gpath1
		assert result == expected

		if expected and gpath1 != gpath2:
			result = gpath1 in gpath2
			assert result == False


	@pytest.mark.parametrize(
		('gpath1', 'gpath2', 'subpath_expected', 'relpath_expected'),
		[
			("/", "/", "", ""),
			("/", "", None, None),
			("/", "..", None, None),
			("/", "C:/", None, None),
			("/a", "/", "a", "a"),
			("/a", "/a", "", ""),
			("/a/b", "/", "a/b", "a/b"),
			("/a/b", "/a", "b", "b"),
			("/a/b", "/b", None, "../a/b"),

			("", "/", None, None),
			("", "", "", ""),
			("", "..", None, None),
			("", "C:/", None, None),
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
			("C:/a", "C:/", "a", "a"),
			("C:/a", "C:/a", "", ""),
			("C:/a/b", "C:/", "a/b", "a/b"),
			("C:/a/b", "C:/a", "b", "b"),
			("C:/a/b", "D:/a", None, None),
			("C:/a/b", "C:/b", None, "../a/b"),
		],
		indirect=['gpath1', 'gpath2']
	)
	def test_subpath_relpath(self, gpath1: GPath, gpath2: GPath, subpath_expected: str, relpath_expected: Union[str, GPath]):
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
		if gpath1._device != "" and result != None:
			print(result._parts, result._absolute, result._device, result._parent)
		assert result == relpath_expected_gpath


	@pytest.mark.parametrize(
		('gpath1', 'gpath2', 'expected_gpath'),
		[
			("/", "/", "/"),
			("/", "", "/"),
			("/", "..", "/"),
			("/", "C:/", "/"),
			("/", "a", "/a"),
			("/", "../a", "/a"),
			("/a", "/", "/a"),
			("/a", "", "/a"),
			("/a", "..", "/"),
			("/a", "C:/", "/a"),
			("/a", "b", "/a/b"),
			("/a", "../b", "/b"),

			("", "/", ""),
			("", "", ""),
			("", "..", ".."),
			("", "C:/", ""),
			("", "a", "a"),
			("", "../a", "../a"),
			("a", "/", "a"),
			("a", "", "a"),
			("a", "..", ""),
			("a", "C:/", "a"),
			("a", "b", "a/b"),
			("a", "../b", "b"),

			("..", "/", ".."),
			("..", "", ".."),
			("..", "..", "../.."),
			("..", "C:/", ".."),
			("..", "a", "../a"),
			("..", "../a", "../../a"),
			("../a", "/", "../a"),
			("../a", "", "../a"),
			("../a", "..", ".."),
			("../a", "C:/", "../a"),
			("../a", "b", "../a/b"),
			("../a", "../b", "../b"),

			("C:/", "/", "C:/"),
			("C:/", "", "C:/"),
			("C:/", "..", "C:/"),
			("C:/", "C:/", "C:/"),
			("C:/", "D:/", "C:/"),
			("C:/", "a", "C:/a"),
			("C:/", "../a", "C:/a"),
			("C:/a", "/", "C:/a"),
			("C:/a", "", "C:/a"),
			("C:/a", "..", "C:/"),
			("C:/a", "C:/", "C:/a"),
			("C:/a", "D:/", "C:/a"),
			("C:/a", "b", "C:/a/b"),
			("C:/a", "../b", "C:/b"),
		],
		indirect=True
	)
	def test_add(self, gpath1: GPath, gpath2: GPath, expected_gpath: GPath):
		"""
			Test `__add__()`.
		"""
		result = gpath1 + gpath2
		assert result == expected_gpath


	@pytest.mark.parametrize(
		('gpath1', 'sub_value', 'expected_gpath'),
		[
			("/", 0, "/"),
			("/", 1, "/"),
			("/a/b", 0, "/a/b"),
			("/a/b", 1, "/a"),
			("/a/b", 2, "/"),
			("/a/b", 3, "/"),

			("", 0, ""),
			("", 1, ".."),
			("a/b", 0, "a/b"),
			("a/b", 1, "a"),
			("a/b", 2, ""),
			("a/b", 3, ".."),

			("..", 0, ".."),
			("..", 1, "../.."),
			("../a/b", 0, "../a/b"),
			("../a/b", 1, "../a"),
			("../a/b", 2, ".."),
			("../a/b", 3, "../.."),

			("C:/", 0, "C:/"),
			("C:/", 1, "C:/"),
			("C:/a/b", 0, "C:/a/b"),
			("C:/a/b", 1, "C:/a"),
			("C:/a/b", 2, "C:/"),
			("C:/a/b", 3, "C:/"),
		],
		indirect=['gpath1', 'expected_gpath']
	)
	def test_sub(self, gpath1: GPath, sub_value: int, expected_gpath: GPath):
		"""
			Test `__sub__()`.
		"""
		result = gpath1 - sub_value
		assert result == expected_gpath


	@pytest.mark.parametrize(
		('gpath1'),
		[("/"), ("/a/b"), (""), ("a/b"), (".."), ("../a/b"), ("../.."), ("../../a/b"), ("C:/"), ("C:/a/b")],
		indirect=['gpath1']
	)
	@pytest.mark.parametrize(('sub_value'), [-1])
	def test_sub_negative(self, gpath1: GPath, sub_value: int):
		"""
			Test `__sub__()` with negative inputs which should give errors.
		"""
		with pytest.raises(ValueError):
			gpath1 - sub_value


	@pytest.mark.parametrize(
		('gpath1', 'mul_value', 'expected_gpath'),
		[
			("/", 1, "/"),
			("/", 2, "/"),
			("/", 0, "/"),
			("/a/b", 1, "/a/b"),
			("/a/b", 2, "/a/b/a/b"),
			("/a/b", 0, "/"),

			("", 1, ""),
			("", 2, ""),
			("", 0, ""),
			("a/b", 1, "a/b"),
			("a/b", 2, "a/b/a/b"),
			("a/b", 0, ""),

			("..", 1, ".."),
			("..", 2, "../.."),
			("..", 0, ""),
			("../a/b", 1, "../a/b"),
			("../a/b", 2, "../../a/b/a/b"),
			("../a/b", 0, ""),

			("../..", 1, "../.."),
			("../..", 2, "../../../.."),
			("../..", 0, ""),
			("../../a/b", 1, "../../a/b"),
			("../../a/b", 2, "../../../../a/b/a/b"),
			("../../a/b", 0, ""),

			("C:/", 1, "C:/"),
			("C:/", 2, "C:/"),
			("C:/", 0, "C:/"),
			("C:/a/b", 1, "C:/a/b"),
			("C:/a/b", 2, "C:/a/b/a/b"),
			("C:/a/b", 0, "C:/"),
		],
		indirect=['gpath1', 'expected_gpath']
	)
	def test_mul(self, gpath1: GPath, mul_value: int, expected_gpath: GPath):
		"""
			Test `__mul__()`.
		"""
		result = gpath1 * mul_value
		assert result == expected_gpath


	@pytest.mark.parametrize(
		('gpath1'),
		[("/"), ("/a/b"), (""), ("a/b"), (".."), ("../a/b"), ("../.."), ("../../a/b"), ("C:/"), ("C:/a/b")],
		indirect=['gpath1']
	)
	@pytest.mark.parametrize(('mul_value'), [-1, -2])
	def test_mul_negative(self, gpath1: GPath, mul_value: int):
		"""
			Test `__mul__()` with negative inputs which should give errors.
		"""
		with pytest.raises(ValueError):
			gpath1 * mul_value


	@pytest.mark.parametrize(
		('gpath1', 'shift_value', 'lshift_expected', 'rshift_expected'),
		[
			("/", 0, "/", "/"),
			("/", 1, "/", "/"),
			("/a/b", 0, "/a/b", "/a/b"),
			("/a/b", 1, "/a/b", "/a/b"),

			("", 0, "", ""),
			("", 1, "", ".."),
			("a/b", 0, "a/b", "a/b"),
			("a/b", 1, "a/b", "../a/b"),

			("..", 0, "..", ".."),
			("..", 1, "", "../.."),
			("..", 2, "", "../../.."),
			("../a/b", 0, "../a/b", "../a/b"),
			("../a/b", 1, "a/b", "../../a/b"),
			("../a/b", 2, "a/b", "../../../a/b"),

			("../..", 0, "../..", "../.."),
			("../..", 1, "..", "../../.."),
			("../..", 2, "", "../../../.."),
			("../../a/b", 0, "../../a/b", "../../a/b"),
			("../../a/b", 1, "../a/b", "../../../a/b"),
			("../../a/b", 2, "a/b", "../../../../a/b"),

			("C:/", 0, "C:/", "C:/"),
			("C:/", 1, "C:/", "C:/"),
			("C:/a/b", 0, "C:/a/b", "C:/a/b"),
			("C:/a/b", 1, "C:/a/b", "C:/a/b"),
		],
		indirect=['gpath1']
	)
	def test_lshift_rshift(self, gpath1: GPath, shift_value: int, lshift_expected: str, rshift_expected: str):
		"""
			Test `__lshift__()` and `__rshift__()`.
		"""
		lshift_expected_gpath = GPath(lshift_expected)
		rshift_expected_gpath = GPath(rshift_expected)

		result = gpath1 << shift_value
		assert result == lshift_expected_gpath
		result = gpath1 << (-1 * shift_value)
		assert result == rshift_expected_gpath

		result = gpath1 >> shift_value
		assert result == rshift_expected_gpath
		result = gpath1 >> (-1 * shift_value)
		assert result == lshift_expected_gpath


	@pytest.mark.parametrize(
		#('path1', 'path2', 'allow_current', 'allow_parents', 'expected_path'),
		('path1', 'path2', 'allow_current_expected', 'allow_parents_expected', 'allow_current_parent_expected', 'no_common_expected'),
		[
			("/", "/", "/", "/", "/", "/"),
			("/", "", None, None, None, None),
			("/", "..", None, None, None, None),
			("/", "C:/", None, None, None, None),
			("/", "/a", "/", "/", "/", "/"),
			("/", "a", None, None, None, None),
			("/", "../a", None, None, None, None),
			("/a", "/", "/", "/", "/", "/"),
			("/a", "", None, None, None, None),
			("/a", "..", None, None, None, None),
			("/a", "C:/", None, None, None, None),
			("/a", "/b", "/", "/", "/", "/"),
			("/a", "b", None, None, None, None),
			("/a", "../b", None, None, None, None),

			("", "", "", "", "", ""),
			("", "..", None, "..", "..", None),
			("", "C:/", None, None, None, None),
			("", "a", "", "", "", None),
			("", "../a", None, "..", "..", None),
			#("a", "", "", "", "", None),
			("a", "..", None, "..", "..", None),
			("a", "C:/", None, None, None, None),
			("a", "b", "", "", "", None),
			("a", "../b", None, "..", "..", None),

			("..", "..", "..", "..", "..", ".."),
			("..", "../..", None, "../..", "../..", None),
			("..", "C:/", None, None, None, None),
			("..", "../a", "..", "..", "..", ".."),
			("..", "../../a", None, "../..", "../..", None),
			("../a", "..", "..", "..", "..", ".."),
			("../a", "../..", None, "../..", "../..", None),
			("../a", "C:/", None, None, None, None),
			("../a", "../b", "..", "..", "..", ".."),
			("../a", "../../b", None, "../..", "../..", None),

			("C:/", "C:/", "C:/", "C:/", "C:/", "C:/"),
			("C:/", "D:/", None, None, None, None),
			("C:/a", "C:/", "C:/", "C:/", "C:/", "C:/"),
			("C:/a", "D:/", None, None, None, None),
			("C:/a", "C:/b", "C:/", "C:/", "C:/", "C:/"),
		]
	)
	def test_find_common(self,
		path1: str,
		path2: str,
		allow_current_expected: str,
		allow_parents_expected: str,
		allow_current_parent_expected: str,
		no_common_expected: str
	):
		"""
			Test `find_common()`.
		"""
		assert allow_parents_expected == allow_current_parent_expected

		if allow_current_expected is not None:
			allow_current_expected_gpath = GPath(allow_current_expected)
		else:
			allow_current_expected_gpath = None

		result = GPath.find_common(path1, path2)
		assert result == allow_current_expected_gpath
		result = GPath.find_common(path2, path1)
		assert result == allow_current_expected_gpath

		result = GPath.find_common(GPath(path1), GPath(path2))
		assert result == allow_current_expected_gpath
		result = GPath.find_common(GPath(path2), GPath(path1))
		assert result == allow_current_expected_gpath

		result = GPath.find_common(path1, path2, allow_current=True, allow_parents=False)
		assert result == allow_current_expected_gpath
		result = GPath.find_common(path2, path1, allow_current=True, allow_parents=False)
		assert result == allow_current_expected_gpath

		result = GPath.find_common(GPath(path1), GPath(path2), allow_current=True, allow_parents=False)
		assert result == allow_current_expected_gpath
		result = GPath.find_common(GPath(path2), GPath(path1), allow_current=True, allow_parents=False)
		assert result == allow_current_expected_gpath

		if allow_parents_expected is not None:
			allow_parents_expected_gpath = GPath(allow_parents_expected)
		else:
			allow_parents_expected_gpath = None

		result = GPath.find_common(path1, path2, allow_current=False, allow_parents=True)
		assert result == allow_parents_expected_gpath
		result = GPath.find_common(path2, path1, allow_current=False, allow_parents=True)
		assert result == allow_parents_expected_gpath

		result = GPath.find_common(GPath(path1), GPath(path2), allow_current=False, allow_parents=True)
		assert result == allow_parents_expected_gpath
		result = GPath.find_common(GPath(path2), GPath(path1), allow_current=False, allow_parents=True)
		assert result == allow_parents_expected_gpath

		if allow_current_parent_expected is not None:
			allow_current_parent_expected_gpath = GPath(allow_current_parent_expected)
		else:
			allow_current_parent_expected_gpath = None

		result = GPath.find_common(path1, path2, allow_current=True, allow_parents=True)
		assert result == allow_current_parent_expected_gpath
		result = GPath.find_common(path2, path1, allow_current=True, allow_parents=True)
		assert result == allow_current_parent_expected_gpath

		result = GPath.find_common(GPath(path1), GPath(path2), allow_current=True, allow_parents=True)
		assert result == allow_current_parent_expected_gpath
		result = GPath.find_common(GPath(path2), GPath(path1), allow_current=True, allow_parents=True)
		assert result == allow_current_parent_expected_gpath

		if no_common_expected is not None:
			no_common_expected_gpath = GPath(no_common_expected)
		else:
			no_common_expected_gpath = None

		result = GPath.find_common(path1, path2, allow_current=False, allow_parents=False)
		assert result == no_common_expected_gpath
		result = GPath.find_common(path2, path1, allow_current=False, allow_parents=False)
		assert result == no_common_expected_gpath

		result = GPath.find_common(GPath(path1), GPath(path2), allow_current=False, allow_parents=False)
		assert result == no_common_expected_gpath
		result = GPath.find_common(GPath(path2), GPath(path1), allow_current=False, allow_parents=False)
		assert result == no_common_expected_gpath



	@pytest.mark.parametrize(
		('paths', 'allow_current', 'allow_parents', 'expected'),
		[
			(
				[
					"/usr/bin",
					"/usr/bin/python",
					"/home/username/Documents/Secret Documents/Secret Document.txt",
					"usr/bin",
					"usr/bin/python",
					"../usr/bin",
					"../usr/bin/python",
					"../../usr/bin",
					"../../usr/bin/python",
					"C:/Program Files",
					"C:/Program Files/python.exe",
					"D:/Documents",
					"E:/",
					"E:/Secret Documents/Secret Document.txt",
				],
				True,
				False,
				{
					GPath("/"): [
						GPath("usr/bin"),
						GPath("usr/bin/python"),
						GPath("home/username/Documents/Secret Documents/Secret Document.txt"),
					],
					GPath("usr/bin"): [
						GPath(""),
						GPath("python"),
					],
					GPath("../usr/bin"): [
						GPath(""),
						GPath("python"),
					],
					GPath("../../usr/bin"): [
						GPath(""),
						GPath("python"),
					],
					GPath("C:/Program Files"): [
						GPath(""),
						GPath("python.exe"),
					],
					GPath("D:/Documents"): [
						GPath(""),
					],
					GPath("E:/"): [
						GPath(""),
						GPath("Secret Documents/Secret Document.txt"),
					],
				}
			),
			([""], True, False, {GPath(""): [GPath("")]}),
			([""], True, True, {GPath(""): []}),
			([""], False, True, {GPath(""): []}),
			([""], False, False, {GPath(""): [GPath("")]}),
			([], True, False, {}),
			([], True, True, {}),
			([], False, True, {}),
			([], False, False, {}),
			(["", "usr/bin", "home/username", "../usr/bin", "../../usr/bin"], True, False, {
				GPath(""): [
					GPath(""),
					GPath("usr/bin"),
					GPath("home/username"),
				],
				GPath("../usr/bin"): [
					GPath(""),
				],
				GPath("../../usr/bin"): [
					GPath(""),
				],
			}),
			(["", "usr/bin", "home/username"], True, True, {
				GPath(""): [],
			}),
			(["", "usr/bin", "home/username", "../usr/bin", "../../usr/bin"], True, True, {
				GPath("../.."): [],
			}),
			(["", "usr/bin", "home/username"], False, True, {
				GPath(""): [],
			}),
			(["", "usr/bin", "home/username", "../usr/bin", "../../usr/bin"], False, True, {
				GPath("../.."): [],
			}),
			(["", "usr/bin", "home/username", "../usr/bin", "../../usr/bin"], False, False, {
				GPath(""): [
					GPath(""),
				],
				GPath("usr/bin"): [
					GPath(""),
				],
				GPath("home/username"): [
					GPath(""),
				],
				GPath("../usr/bin"): [
					GPath(""),
				],
				GPath("../../usr/bin"): [
					GPath(""),
				],
			}),
		]
	)
	def test_partition(self, paths: list[str], allow_current: bool, allow_parents: bool, expected: dict[GPath, list[GPath]]):
		"""
			Test `partition()`.
		"""
		result = GPath.partition(paths, allow_current=allow_current, allow_parents=allow_parents)
		assert result == expected
		result = GPath.partition(*paths, allow_current=allow_current, allow_parents=allow_parents)
		assert result == expected

		gpaths = [GPath(path) for path in paths]
		result = GPath.partition(gpaths, allow_current=allow_current, allow_parents=allow_parents)
		assert result == expected
		result = GPath.partition(*gpaths, allow_current=allow_current, allow_parents=allow_parents)
		assert result == expected


	@pytest.mark.parametrize(
		('paths', 'expected_gpath'),
		[
			(["", "/", "usr", "bin"], "usr/bin"),
			(["/", "", "usr", "bin"], "/usr/bin"),
			(["/", "usr", "", "bin"], "/usr/bin"),
			(["/", "usr", "bin", ""], "/usr/bin"),
			(["..", "/", "usr", "bin"], "../usr/bin"),
			(["/", "..", "usr", "bin"], "/usr/bin"),
			(["/", "usr", "..", "bin"], "/bin"),
			(["/", "usr", "bin", ".."], "/usr"),

			(["/usr", "local", "bin"], "/usr/local/bin"),
			(["/usr", "/local", "bin"], "/usr/bin"),
			(["/usr", "../local", "bin"], "/local/bin"),
			(["/usr", "../../local", "bin"], "/local/bin"),
			(["/usr", "../local", "../bin"], "/bin"),
			(["/usr", "C:/local", "bin"], "/usr/bin"),
			(["/", "usr", "bin"], "/usr/bin"),
			(["/", "usr", "bin"], "/usr/bin"),

			(["usr", "local", "bin"], "usr/local/bin"),
			(["usr", "/local", "bin"], "usr/bin"),
			(["usr", "../local", "bin"], "local/bin"),
			(["usr", "../../local", "bin"], "../local/bin"),
			(["usr", "../local", "../bin"], "bin"),
			(["usr", "C:/local", "bin"], "usr/bin"),
			(["", "usr", "bin"], "usr/bin"),

			(["../usr", "local", "bin"], "../usr/local/bin"),
			(["../usr", "/local", "bin"], "../usr/bin"),
			(["../usr", "../local", "bin"], "../local/bin"),
			(["../usr", "../../local", "bin"], "../../local/bin"),
			(["../usr", "../local", "../bin"], "../bin"),
			(["../usr", "../local", "../../bin"], "../../bin"),
			(["../usr", "C:/local", "bin"], "../usr/bin"),
			(["..", "usr", "bin"], "../usr/bin"),
			(["../..", "usr", "bin"], "../../usr/bin"),
			(["..", "..", "usr", "bin"], "../../usr/bin"),

			(["C:/Windows", "System32", "drivers"], "C:/Windows/System32/drivers"),
			(["C:/Windows", "/System32", "Containers"], "C:/Windows/Containers"),
			(["C:/Windows", "../System32", "Containers"], "C:/System32/Containers"),
			(["C:/Windows", "../../System32", "Containers"], "C:/System32/Containers"),
			(["C:/Windows", "../System32", "../Containers"], "C:/Containers"),
			(["C:/Windows", "C:/System32", "Containers"], "C:/Windows/Containers"),
			(["C:/Windows", "D:/System32", "Containers"], "C:/Windows/Containers"),
			(["C:/", "Windows", "System32"], "C:/Windows/System32"),
		],
		indirect=['expected_gpath']
	)
	def test_join(self, paths: list[str], expected_gpath: GPath):
		"""
			Test `join()`.
		"""
		result = GPath.join(paths)
		assert result == expected_gpath

		gpaths = [GPath(path) for path in paths]
		result = GPath.join(gpaths)
		assert result == expected_gpath
