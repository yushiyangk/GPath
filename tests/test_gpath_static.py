from __future__ import annotations

import pytest

from gpath import GPath
from util import TestGPath

class TestGPathStatic(TestGPath):
	@staticmethod
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
					"E:",
					"E:Apples",
					"E:Secret Documents/Secret Document.txt",
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
					GPath("E:"): [
						GPath(""),
						GPath("Apples"),
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
	def test_partition(paths: list[str], allow_current: bool, allow_parents: bool, expected: dict[GPath, list[GPath]]):
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

	@staticmethod
	@pytest.mark.parametrize(
		('paths', 'expected_gpath'),
		[
			(["", "usr", "bin"], "usr/bin"),
			(["", "/", "usr", "bin"], "/usr/bin"),
			(["/", "", "usr", "bin"], "/usr/bin"),
			(["/", "usr", "", "bin"], "/usr/bin"),
			(["/", "usr", "bin", ""], "/usr/bin"),
			(["..", "usr", "bin"], "../usr/bin"),
			(["..", "/", "usr", "bin"], "/usr/bin"),
			(["/", "..", "usr", "bin"], "/usr/bin"),
			(["/", "usr", "..", "bin"], "/bin"),
			(["/", "usr", "bin", ".."], "/usr"),

			(["/usr", "local", "bin"], "/usr/local/bin"),
			(["/usr", "/local", "bin"], "/local/bin"),
			(["/usr", "../local", "bin"], "/local/bin"),
			(["/usr", "../../local", "bin"], "/local/bin"),
			(["/usr", "../local", "../bin"], "/bin"),
			(["/usr", "C:/local", "bin"], "C:/local/bin"),
			(["/usr", "C:local", "bin"], "C:/usr/local/bin"),
			(["/", "usr", "bin"], "/usr/bin"),

			(["usr", "local", "bin"], "usr/local/bin"),
			(["usr", "/local", "bin"], "/local/bin"),
			(["usr", "../local", "bin"], "local/bin"),
			(["usr", "../../local", "bin"], "../local/bin"),
			(["usr", "../local", "../bin"], "bin"),
			(["usr", "C:/local", "bin"], "C:/local/bin"),
			(["usr", "C:local", "bin"], "C:usr/local/bin"),
			(["", "usr", "bin"], "usr/bin"),

			(["../usr", "local", "bin"], "../usr/local/bin"),
			(["../usr", "/local", "bin"], "/local/bin"),
			(["../usr", "../local", "bin"], "../local/bin"),
			(["../usr", "../../local", "bin"], "../../local/bin"),
			(["../usr", "../local", "../bin"], "../bin"),
			(["../usr", "../local", "../../bin"], "../../bin"),
			(["../usr", "C:/local", "bin"], "C:/local/bin"),
			(["../usr", "C:local", "bin"], "C:../usr/local/bin"),
			(["..", "usr", "bin"], "../usr/bin"),
			(["../..", "usr", "bin"], "../../usr/bin"),
			(["..", "..", "usr", "bin"], "../../usr/bin"),

			(["C:/Windows", "System32", "drivers"], "C:/Windows/System32/drivers"),
			(["C:/Windows", "/System32", "Containers"], "C:/System32/Containers"),
			(["C:/Windows", "../System32", "Containers"], "C:/System32/Containers"),
			(["C:/Windows", "../../System32", "Containers"], "C:/System32/Containers"),
			(["C:/Windows", "../System32", "../Containers"], "C:/Containers"),
			(["C:/Windows", "C:/System32", "Containers"], "C:/System32/Containers"),
			(["C:/Windows", "C:System32", "Containers"], "C:/Windows/System32/Containers"),
			(["C:/Windows", "D:/System32", "Containers"], "D:/System32/Containers"),
			(["C:/Windows", "D:System32", "Containers"], "D:/Windows/System32/Containers"),
			(["C:/", "Windows", "System32"], "C:/Windows/System32"),
		],
		indirect=['expected_gpath']
	)
	def test_join(paths: list[str], expected_gpath: GPath):
		"""
			Test `join()`.
		"""
		result = GPath.join(paths)
		assert result == expected_gpath

		gpaths = [GPath(path) for path in paths]
		result = GPath.join(gpaths)
		assert result == expected_gpath
