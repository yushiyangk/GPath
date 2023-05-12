from __future__ import annotations

import pytest

from gpath import GPath
from util import TestGPath

class TestGPathEncoding(TestGPath):
	@staticmethod
	@pytest.mark.parametrize(
		('path', 'expected_parts', 'expected_drive', 'expected_root', 'expected_parent_level'),
		[
			("", tuple(), "", False, 0),
			("a/b", ("a", "b"), "", False, 0),
			("/", tuple(), "", True, 0),
			("/a/b", ("a", "b"), "", True, 0),
			("..", tuple(), "", False, 1),
			("../a/b", ("a", "b"), "", False, 1),
			("../..", tuple(), "", False, 2),
			("../../a/b", ("a", "b"), "", False, 2),
			("C:", tuple(), "C", False, 0),
			("C:a/b", ("a", "b"), "C", False, 0),
			("C:..", tuple(), "C", False, 1),
			("C:../a/b", ("a", "b"), "C", False, 1),
			("C:/", tuple(), "C", True, 0),
			("C:/a/b", ("a", "b"), "C", True, 0),

			("αβγ", ("αβγ",), "", False, 0),
			("абв", ("абв",), "", False, 0),
			("汉字/漢字", ("汉字", "漢字"), "", False, 0),
			("العربية", ("العربية",), "", False, 0),
			("देवनागरी", ("देवनागरी",), "", False, 0),
			("বাংলা", ("বাংলা",), "", False, 0),
			("かな/カナ", ("かな", "カナ"), "", False, 0),
			("한글/조선글", ("한글", "조선글"), "", False, 0),
			("తెలుగు", ("తెలుగు",), "", False, 0),
			("தமிழ்", ("தமிழ்",), "", False, 0),

		]
	)
	@pytest.mark.parametrize('encoding', ['utf_8', 'ascii', 'utf_32_be', 'utf_32_le', 'utf_16_be', 'utf_16_le', 'utf_7', 'cp037', 'cp720', 'cp855', 'big5'])
	# cp037 English, cp720 Arabic, cp855 Cyrllic
	def test_encoding(
		path: str,
		expected_parts: tuple[str, ...],
		expected_drive: str,
		expected_root: bool,
		expected_parent_level: int,
		encoding: str,
	):
		"""
			Test constructor with different encodings and test their propagation
		"""
		try:
			bytes_path = path.encode(encoding)
		except UnicodeEncodeError:
			pytest.skip("cannot encoded in given encoding")

		gpath = GPath(bytes_path, encoding=encoding)
		assert gpath.absolute == expected_root
		assert gpath.drive == expected_drive
		assert gpath.named_parts == list(expected_parts)
		assert gpath.parent_level == expected_parent_level
		assert gpath.encoding == encoding

		# Test copy propagation
		gpath_copy = GPath(gpath)
		assert gpath_copy.absolute == expected_root
		assert gpath_copy.drive == expected_drive
		assert gpath_copy.named_parts == list(expected_parts)
		assert gpath_copy.parent_level == expected_parent_level
		assert gpath_copy.encoding == encoding

		# Test copy with override
		gpath_copy = GPath(gpath, encoding='utf-8')
		assert gpath_copy.encoding == 'utf-8'

		# Test left-operand propagation
		gpath_result = gpath + "a"
		assert gpath_result.encoding == encoding
		gpath_result = gpath + GPath("a", encoding='utf-8')
		assert gpath_result.encoding == encoding

		# Test right-operand propagation
		default_encoding_gpath = GPath(path)
		assert default_encoding_gpath.encoding == None
		gpath_result = default_encoding_gpath + "a"
		assert default_encoding_gpath.encoding == None
		gpath_result = gpath + GPath("a", encoding=encoding)
		assert gpath_result.encoding == encoding
