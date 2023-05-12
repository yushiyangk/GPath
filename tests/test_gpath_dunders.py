from __future__ import annotations

import os
from typing import Union

import pytest

from gpath import GPath
from util import TestGPath

class TestGPathDunders(TestGPath):
	@staticmethod
	@pytest.mark.parametrize(
		('path1', 'path2', 'expected'),
		[
			("/", "/", True),
			("", "", True),
			("..", "..", True),
			("C:/", "C:/", True),
			("C:", "C:", True),
			("/", "", False),
			("..", "", False),
			("..", "/", False),
			("..", "../..", False),
			("C:/", "c:/", False),
			("C:/", "D:/", False),
			("C:/", "C:", False),
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
	def test_eq_hash(path1: str, path2: str, expected: bool):
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
		assert result == expected
		result = gpath2 == path1
		assert result == expected

		if expected is True:
			assert hash(gpath1) == hash(gpath2)
		else:
			assert hash(gpath1) != hash(gpath2)


	@staticmethod
	@pytest.mark.parametrize(
		('gpath1', 'expected'),
		[
			("/", True),
			("", False),
			("..", True),
			("../..", True),
			("C:/", True),
			("C:", True),

			("/a", True),
			("a", True),
			("../a", True),
			("C:/a", True),
			("C:a", True),
		],
		indirect=['gpath1']
	)
	def test_bool(gpath1: GPath, expected: bool):
		"""
			Test `__bool__()`.
		"""
		result = bool(gpath1)
		assert result == expected
		result = not gpath1
		assert result == (not expected)


	@staticmethod
	@pytest.mark.parametrize(
		('path'),
		[
			("."),
			(".."),
			("../.."),
			("C:/"),
			("C:"),
			("/a"),
			("/a/b"),
			("a"),
			("a/b"),
			("../a"),
			("../a/b"),
			("C:/a"),
			("C:/a/b"),
			("C:a"),
			("C:a/b"),
		]
	)
	def test_str_repr(path: str):
		"""
			Test `__str__()` and `__repr__()` for cross-platform outputs.
		"""
		gpath = GPath(path)
		result = str(gpath)
		assert result == path

		result = repr(gpath)
		result_eval = eval(result)
		assert result_eval == gpath


	@staticmethod
	@pytest.mark.parametrize(
		('path', 'expected'),
		[
			("/", {'posix': "/", 'nt': "/", 'java': "/"}),
		]
	)
	def test_str_repr_platform(path: str, expected: dict[str, str]):
		"""
			Test `__str__()` and `__repr__()` for outputs that may (or may not) dependent on local operating system
		"""
		gpath = GPath(path)
		result = str(gpath)
		assert result == expected[os.name]

		result = repr(gpath)
		result_eval = eval(result)
		assert result_eval == gpath


	@staticmethod
	@pytest.mark.parametrize(
		('gpath1', 'expected'),
		[
			("/", 0),
			("", 0),
			("..", 0),
			("../..", 0),
			("C:/", 0),
			("C:", 0),
			("/a", 1),
			("/a/b", 2),
			("a", 1),
			("a/b", 2),
			("../a", 1),
			("../a/b", 2),
			("C:/a", 1),
			("C:/a/b", 2),
			("C:a", 1),
			("C:a/b", 2),
		],
		indirect=['gpath1']
	)
	def test_len(gpath1: GPath, expected: int):
		"""
			Test `__len__()`.
		"""
		result = len(gpath1)
		assert result == expected


	@staticmethod
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
			("C:a", ["a"]),
			("C:a/b", ["a", "b"]),
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
	def test_getitem_iter(gpath1: GPath, index: Union[int, slice], expected_list: list[str]):
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


	@staticmethod
	@pytest.mark.parametrize(
		('gpath1', 'gpath2', 'expected'),
		[
			("/", "", False),
			("", "/", False),
			("/", "..", False),
			("..", "/", False),
			("/", "C:/", False),
			("C:/", "/", False),
			("/", "C:", False),
			("C:", "/", False),

			("C:/", "", False),
			("", "C:/", False),
			("C:/", "..", False),
			("..", "C:/", False),
			("C:/", "D:/", False),
			("D:/", "C:/", False),
			("C:/", "C:", False),
			("C:", "C:/", False),

			("a", "b", False),
			("b", "a", False),
			("/a", "/b", False),
			("/b", "/a", False),
			("../a", "../b", False),
			("../b", "../a", False),
			("C:/a", "C:/b", False),
			("C:/b", "C:/a", False),
			("C:a", "C:b", False),
			("C:b", "C:a", False),

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
			("C:a", "C:a/b", True),

			("a", "a", True),
			("/a", "/a", True),
			("../a", "../a", True),
			("C:/a", "C:/a", True),
			("C:a", "C:a", True),
		],
		indirect=['gpath1', 'gpath2']
	)
	def test_contains(gpath1: GPath, gpath2: GPath, expected: bool):
		"""
			Test `__contains__()`.
		"""
		result = gpath2 in gpath1
		assert result == expected

		if expected and gpath1 != gpath2:
			result = gpath1 in gpath2
			assert result == False


	@staticmethod
	@pytest.mark.parametrize(
		('gpath1', 'gpath2', 'expected_gpath'),
		[
			("/", "/", "/"),
			("/", "", "/"),
			("/", "..", "/"),
			("/", "C:/", "C:/"),
			("/", "C:", "C:/"),
			("/", "a", "/a"),
			("/", "../a", "/a"),
			("/a", "/", "/"),
			("/a", "", "/a"),
			("/a", "..", "/"),
			("/a", "C:/", "C:/"),
			("/a", "C:", "C:/a"),
			("/a", "b", "/a/b"),
			("/a", "../b", "/b"),

			("", "/", "/"),
			("", "", ""),
			("", "..", ".."),
			("", "C:/", "C:/"),
			("", "C:", "C:"),
			("", "a", "a"),
			("", "../a", "../a"),
			("a", "/", "/"),
			("a", "", "a"),
			("a", "..", ""),
			("a", "C:/", "C:/"),
			("a", "C:", "C:a"),
			("a", "b", "a/b"),
			("a", "../b", "b"),

			("..", "/", "/"),
			("..", "", ".."),
			("..", "..", "../.."),
			("..", "C:/", "C:/"),
			("..", "C:", "C:.."),
			("..", "a", "../a"),
			("..", "../a", "../../a"),
			("../a", "/", "/"),
			("../a", "", "../a"),
			("../a", "..", ".."),
			("../a", "C:/", "C:/"),
			("../a", "C:", "C:../a"),
			("../a", "b", "../a/b"),
			("../a", "../b", "../b"),

			("C:/", "/", "C:/"),
			("C:/", "", "C:/"),
			("C:/", "..", "C:/"),
			("C:/", "C:/", "C:/"),
			("C:/", "C:", "C:/"),
			("C:/", "D:/", "D:/"),
			("C:/", "D:", "D:/"),
			("C:/", "a", "C:/a"),
			("C:/", "../a", "C:/a"),
			("C:/a", "/", "C:/"),
			("C:/a", "", "C:/a"),
			("C:/a", "..", "C:/"),
			("C:/a", "C:/", "C:/"),
			("C:/a", "C:", "C:/a"),
			("C:/a", "D:/", "D:/"),
			("C:/a", "D:", "D:/a"),
			("C:/a", "b", "C:/a/b"),
			("C:/a", "../b", "C:/b"),
		],
		indirect=True
	)
	def test_add(gpath1: GPath, gpath2: GPath, expected_gpath: GPath):
		"""
			Test `__add__()`.
		"""
		result = gpath1 + gpath2
		assert result == expected_gpath
		result = gpath1 / gpath2
		assert result == expected_gpath


	@staticmethod
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

			("C:", 0, "C:"),
			("C:", 1, "C:.."),
			("C:a/b", 0, "C:a/b"),
			("C:a/b", 1, "C:a"),
			("C:a/b", 2, "C:"),
			("C:a/b", 3, "C:.."),
		],
		indirect=['gpath1', 'expected_gpath']
	)
	def test_sub(gpath1: GPath, sub_value: int, expected_gpath: GPath):
		"""
			Test `__sub__()`.
		"""
		result = gpath1 - sub_value
		assert result == expected_gpath


	@staticmethod
	@pytest.mark.parametrize(
		('gpath1'),
		[("/"), ("/a/b"), (""), ("a/b"), (".."), ("../a/b"), ("../.."), ("../../a/b"), ("C:/"), ("C:/a/b"), ("C:"), ("C:a/b")],
		indirect=['gpath1']
	)
	@pytest.mark.parametrize(('sub_value'), [-1])
	def test_sub_negative(gpath1: GPath, sub_value: int):
		"""
			Test `__sub__()` with negative inputs which should give errors.
		"""
		with pytest.raises(ValueError):
			result = gpath1 - sub_value


	@staticmethod
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

			("C:", 1, "C:"),
			("C:", 2, "C:"),
			("C:", 0, "C:"),
			("C:a/b", 1, "C:a/b"),
			("C:a/b", 2, "C:a/b/a/b"),
			("C:a/b", 0, "C:"),
		],
		indirect=['gpath1', 'expected_gpath']
	)
	def test_mul(gpath1: GPath, mul_value: int, expected_gpath: GPath):
		"""
			Test `__mul__()`.
		"""
		result = gpath1 * mul_value
		assert result == expected_gpath


	@staticmethod
	@pytest.mark.parametrize(
		('gpath1'),
		[("/"), ("/a/b"), (""), ("a/b"), (".."), ("../a/b"), ("../.."), ("../../a/b"), ("C:/"), ("C:/a/b"), ("C:"), ("C:a/b")],
		indirect=['gpath1']
	)
	@pytest.mark.parametrize(('mul_value'), [-1, -2])
	def test_mul_negative(gpath1: GPath, mul_value: int):
		"""
			Test `__mul__()` with negative inputs which should give errors.
		"""
		with pytest.raises(ValueError):
			result = gpath1 * mul_value


	@staticmethod
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

			("C:", 0, "C:", "C:"),
			("C:", 1, "C:", "C:.."),
			("C:a/b", 0, "C:a/b", "C:a/b"),
			("C:a/b", 1, "C:a/b", "C:../a/b"),
		],
		indirect=['gpath1']
	)
	def test_lshift_rshift(gpath1: GPath, shift_value: int, lshift_expected: str, rshift_expected: str):
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
