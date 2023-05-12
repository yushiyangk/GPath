from __future__ import annotations

import dataclasses
from typing import Generator
from unittest.mock import patch

import pytest

from gpath import render
from gpath.platform import Platform
from util import RenderableData



class TestGenericRenderedPath:
	@staticmethod
	@pytest.fixture
	def rendered_path1(request: pytest.FixtureRequest) -> Generator[render.GenericRenderedPath, None, None]:
		with patch.object(render, 'Renderable', new=RenderableData):
			yield render.GenericRenderedPath(render.Renderable(**dataclasses.asdict(request.param)))  # type: ignore

	@staticmethod
	@pytest.fixture
	def rendered_path2(request: pytest.FixtureRequest) -> Generator[render.GenericRenderedPath, None, None]:
		with patch.object(render, 'Renderable', new=RenderableData):
			yield render.GenericRenderedPath(render.Renderable(**dataclasses.asdict(request.param)))  # type: ignore


	@staticmethod
	@pytest.mark.parametrize(
		('rendered_path1', 'expected_str'),
		[
			(RenderableData([], True, "", 0), "/"),
			(RenderableData(["a", "b"], True, "", 0), "/a/b"),
			(RenderableData([], False, "", 0), "."),
			(RenderableData(["a", "b"], False, "", 0), "a/b"),
			(RenderableData([], False, "", 1), ".."),
			(RenderableData(["a", "b"], False, "", 1), "../a/b"),
			(RenderableData([], False, "", 2), "../.."),
			(RenderableData(["a", "b"], False, "", 2), "../../a/b"),
			(RenderableData([], True, "C", 0), "C:/"),
			(RenderableData(["a", "b"], True, "C", 0), "C:/a/b"),
			(RenderableData([], False, "C", 0), "C:"),
			(RenderableData(["a", "b"], False, "C", 0), "C:a/b"),
			(RenderableData([], False, "C", 1), "C:.."),
			(RenderableData(["a", "b"], False, "C", 1), "C:../a/b"),
		],
		indirect=['rendered_path1']
	)
	def test_str_repr(rendered_path1: render.GenericRenderedPath, expected_str: str):
		"""
			Test `__str__()` and `__repr__()`.
		"""
		result_str = str(rendered_path1)
		assert result_str == expected_str

		GenericRenderedPath = render.GenericRenderedPath
		result_repr = repr(rendered_path1)
		result_eval = eval(result_repr)
		assert result_eval == rendered_path1


	@staticmethod
	@pytest.mark.parametrize(
		('rendered_path1', 'rendered_path2', 'expected_lt', 'expected_eq'),
		[
			(RenderableData(["a"], False, "", 0), RenderableData(["a", "b"], False, "", 0), True, False),
			(RenderableData(["a", "b"], False, "", 0), RenderableData(["b"], False, "", 0), True, False),
			(RenderableData(["b"], False, "", 0), RenderableData([], False, "", 1), True, False),

			(RenderableData([], False, "", 0), RenderableData([], False, "", 0), False, True),
			(RenderableData([], False, "", 0), RenderableData(["a"], False, "", 0), True, False),
			(RenderableData(["a"], False, "", 0), RenderableData(["a"], False, "", 0), False, True),
			(RenderableData(["a"], False, "", 0), RenderableData([], False, "", 1), True, False),

			(RenderableData([], False, "", 1), RenderableData([], False, "", 1), False, True),
			(RenderableData([], False, "", 1), RenderableData(["a"], False, "", 1), True, False),
			(RenderableData(["a"], False, "", 1), RenderableData(["a"], False, "", 1), False, True),
			(RenderableData(["a"], False, "", 1), RenderableData([], False, "", 2), True, False),

			(RenderableData([], False, "", 2), RenderableData([], False, "", 2), False, True),
			(RenderableData([], False, "", 2), RenderableData(["a"], False, "", 2), True, False),
			(RenderableData(["a"], False, "", 2), RenderableData(["a"], False, "", 2), False, True),
			(RenderableData(["a"], False, "", 2), RenderableData([], False, "C", 0), True, False),

			(RenderableData([], False, "C", 0), RenderableData([], False, "C", 0), False, True),
			(RenderableData([], False, "C", 0), RenderableData(["a"], False, "C", 0), True, False),
			(RenderableData(["a"], False, "C", 0), RenderableData(["a"], False, "C", 0), False, True),
			(RenderableData(["a"], False, "C", 0), RenderableData([], False, "C", 1), True, False),

			(RenderableData([], False, "C", 1), RenderableData([], False, "C", 1), False, True),
			(RenderableData([], False, "C", 1), RenderableData(["a"], False, "C", 1), True, False),
			(RenderableData(["a"], False, "C", 1), RenderableData(["a"], False, "C", 1), False, True),
			(RenderableData(["a"], False, "C", 1), RenderableData([], True, "", 0), True, False),

			(RenderableData([], True, "", 0), RenderableData([], True, "", 0), False, True),
			(RenderableData([], True, "", 0), RenderableData(["a"], True, "", 0), True, False),
			(RenderableData(["a"], True, "", 0), RenderableData(["a"], True, "", 0), False, True),
			(RenderableData(["a"], True, "", 0), RenderableData([], True, "C", 0), True, False),

			(RenderableData([], True, "C", 0), RenderableData([], True, "C", 0), False, True),
			(RenderableData([], True, "C", 0), RenderableData(["a"], True, "C", 0), True, False),
			(RenderableData(["a"], True, "C", 0), RenderableData(["a"], True, "C", 0), False, True),
			(RenderableData(["a"], True, "C", 0), RenderableData([], True, "D", 0), True, False),
		],
		indirect=['rendered_path1', 'rendered_path2']
	)
	def test_order(
		rendered_path1: render.GenericRenderedPath,
		rendered_path2: render.GenericRenderedPath,
		expected_lt: bool,
		expected_eq: bool,
	):
		"""
			Test `__eq__()`, `__lt__()`, `__lte__()`, `__gt__()` and `__gte__()`.
		"""
		expected_lte = expected_lt or expected_eq
		expected_gt = ((not expected_lt) and (not expected_eq))
		expected_gte = expected_gt or expected_eq

		result = rendered_path1 == rendered_path2
		assert result == expected_eq
		result = rendered_path2 == rendered_path1
		assert result == expected_eq

		result = rendered_path1 < rendered_path2
		assert result == expected_lt
		result = rendered_path2 > rendered_path1
		assert result == expected_lt

		result = rendered_path1 <= rendered_path2
		assert result == expected_lte
		result = rendered_path2 >= rendered_path1
		assert result == expected_lte

		result = rendered_path1 > rendered_path2
		assert result == expected_gt
		result = rendered_path2 < rendered_path1
		assert result == expected_gt

		result = rendered_path1 >= rendered_path2
		assert result == expected_gte
		result = rendered_path2 <= rendered_path1
		assert result == expected_gte



class TestPosixRenderedPath:
	@staticmethod
	@pytest.fixture
	def rendered_path1(request: pytest.FixtureRequest) -> Generator[render.PosixRenderedPath, None, None]:
		with patch.object(render, 'Renderable', new=RenderableData):
			yield render.PosixRenderedPath(render.Renderable(**dataclasses.asdict(request.param)))  # type: ignore

	@staticmethod
	@pytest.fixture
	def rendered_path2(request: pytest.FixtureRequest) -> Generator[render.PosixRenderedPath, None, None]:
		with patch.object(render, 'Renderable', new=RenderableData):
			yield render.PosixRenderedPath(render.Renderable(**dataclasses.asdict(request.param)))  # type: ignore


	@staticmethod
	@pytest.mark.parametrize(
		('rendered_path1', 'expected_str'),
		[
			(RenderableData([], True, "", 0), "/"),
			(RenderableData(["a", "b"], True, "", 0), "/a/b"),
			(RenderableData([], False, "", 0), "."),
			(RenderableData(["a", "b"], False, "", 0), "a/b"),
			(RenderableData([], False, "", 1), ".."),
			(RenderableData(["a", "b"], False, "", 1), "../a/b"),
			(RenderableData([], False, "", 2), "../.."),
			(RenderableData(["a", "b"], False, "", 2), "../../a/b"),
			(RenderableData([], True, "C", 0), "/"),
			(RenderableData(["a", "b"], True, "C", 0), "/a/b"),
			(RenderableData([], False, "C", 0), "."),
			(RenderableData(["a", "b"], False, "C", 0), "a/b"),
			(RenderableData([], False, "C", 1), ".."),
			(RenderableData(["a", "b"], False, "C", 1), "../a/b"),
		],
		indirect=['rendered_path1']
	)
	def test_str_repr(rendered_path1: render.PosixRenderedPath, expected_str: str):
		"""
			Test `__str__()` and `__repr__()`.
		"""
		result_str = str(rendered_path1)
		assert result_str == expected_str

		PosixRenderedPath = render.PosixRenderedPath
		result_repr = repr(rendered_path1)
		result_eval = eval(result_repr)
		assert result_eval == rendered_path1


	@staticmethod
	@pytest.mark.parametrize(
		('rendered_path1', 'rendered_path2', 'expected_lt', 'expected_eq'),
		[
			(RenderableData(["a"], False, "", 0), RenderableData(["a", "b"], False, "", 0), True, False),
			(RenderableData(["a", "b"], False, "", 0), RenderableData(["b"], False, "", 0), True, False),
			(RenderableData(["b"], False, "", 0), RenderableData([], False, "", 1), True, False),

			(RenderableData([], False, "", 0), RenderableData([], False, "", 0), False, True),
			(RenderableData([], False, "", 0), RenderableData(["a"], False, "", 0), True, False),
			(RenderableData(["a"], False, "", 0), RenderableData(["a"], False, "", 0), False, True),
			(RenderableData(["a"], False, "", 0), RenderableData([], False, "", 1), True, False),

			(RenderableData([], False, "", 1), RenderableData([], False, "", 1), False, True),
			(RenderableData([], False, "", 1), RenderableData(["a"], False, "", 1), True, False),
			(RenderableData(["a"], False, "", 1), RenderableData(["a"], False, "", 1), False, True),
			(RenderableData(["a"], False, "", 1), RenderableData([], False, "", 2), True, False),

			(RenderableData([], False, "", 2), RenderableData([], False, "", 2), False, True),
			(RenderableData([], False, "", 2), RenderableData(["a"], False, "", 2), True, False),
			(RenderableData(["a"], False, "", 2), RenderableData(["a"], False, "", 2), False, True),
			(RenderableData(["a"], False, "", 2), RenderableData([], True, "", 0), True, False),

			(RenderableData([], True, "", 0), RenderableData([], True, "", 0), False, True),
			(RenderableData([], True, "", 0), RenderableData(["a"], True, "", 0), True, False),
			(RenderableData(["a"], True, "", 0), RenderableData(["a"], True, "", 0), False, True),
			(RenderableData(["a"], True, "", 0), RenderableData(["b"], True, "", 0), True, False),

			(RenderableData([], True, "C", 0), RenderableData([], True, "C", 0), False, True),
			(RenderableData([], True, "", 0), RenderableData([], True, "C", 0), False, True),
			(RenderableData([], False, "C", 0), RenderableData([], False, "C", 0), False, True),
			(RenderableData([], False, "", 0), RenderableData([], False, "C", 0), False, True),
			(RenderableData(["a"], True, "C", 0), RenderableData(["a"], True, "C", 0), False, True),
			(RenderableData(["a"], True, "", 0), RenderableData(["a"], True, "C", 0), False, True),
			(RenderableData(["a"], False, "C", 0), RenderableData(["a"], False, "C", 0), False, True),
			(RenderableData(["a"], False, "", 0), RenderableData(["a"], False, "C", 0), False, True),
		],
		indirect=['rendered_path1', 'rendered_path2']
	)
	def test_order(
		rendered_path1: render.PosixRenderedPath,
		rendered_path2: render.PosixRenderedPath,
		expected_lt: bool,
		expected_eq: bool,
	):
		"""
			Test `__eq__()`, `__lt__()`, `__lte__()`, `__gt__()` and `__gte__()`.
		"""
		expected_lte = expected_lt or expected_eq
		expected_gt = ((not expected_lt) and (not expected_eq))
		expected_gte = expected_gt or expected_eq

		result = rendered_path1 == rendered_path2
		assert result == expected_eq
		result = rendered_path2 == rendered_path1
		assert result == expected_eq

		result = rendered_path1 < rendered_path2
		assert result == expected_lt
		result = rendered_path2 > rendered_path1
		assert result == expected_lt

		result = rendered_path1 <= rendered_path2
		assert result == expected_lte
		result = rendered_path2 >= rendered_path1
		assert result == expected_lte

		result = rendered_path1 > rendered_path2
		assert result == expected_gt
		result = rendered_path2 < rendered_path1
		assert result == expected_gt

		result = rendered_path1 >= rendered_path2
		assert result == expected_gte
		result = rendered_path2 <= rendered_path1
		assert result == expected_gte



class TestWindowsRenderedPath:
	@staticmethod
	@pytest.fixture
	def rendered_path1(request: pytest.FixtureRequest) -> Generator[render.WindowsRenderedPath, None, None]:
		with patch.object(render, 'Renderable', new=RenderableData):
			yield render.WindowsRenderedPath(render.Renderable(**dataclasses.asdict(request.param)))  # type: ignore

	@staticmethod
	@pytest.fixture
	def rendered_path2(request: pytest.FixtureRequest) -> Generator[render.WindowsRenderedPath, None, None]:
		with patch.object(render, 'Renderable', new=RenderableData):
			yield render.WindowsRenderedPath(render.Renderable(**dataclasses.asdict(request.param)))  # type: ignore


	@staticmethod
	@pytest.mark.parametrize(
		('rendered_path1', 'expected_str'),
		[
			(RenderableData([], True, "", 0), "\\"),
			(RenderableData(["a", "b"], True, "", 0), "\\a\\b"),
			(RenderableData([], False, "", 0), "."),
			(RenderableData(["a", "b"], False, "", 0), "a\\b"),
			(RenderableData([], False, "", 1), ".."),
			(RenderableData(["a", "b"], False, "", 1), "..\\a\\b"),
			(RenderableData([], False, "", 2), "..\\.."),
			(RenderableData(["a", "b"], False, "", 2), "..\\..\\a\\b"),
			(RenderableData([], True, "C", 0), "C:\\"),
			(RenderableData(["a", "b"], True, "C", 0), "C:\\a\\b"),
			(RenderableData([], False, "C", 0), "C:"),
			(RenderableData(["a", "b"], False, "C", 0), "C:a\\b"),
			(RenderableData([], False, "C", 1), "C:.."),
			(RenderableData(["a", "b"], False, "C", 1), "C:..\\a\\b"),
		],
		indirect=['rendered_path1']
	)
	def test_str_repr(rendered_path1: render.WindowsRenderedPath, expected_str: str):
		"""
			Test `__str__()` and `__repr__()`.
		"""
		result_str = str(rendered_path1)
		assert result_str == expected_str

		WindowsRenderedPath = render.WindowsRenderedPath
		result_repr = repr(rendered_path1)
		result_eval = eval(result_repr)
		assert result_eval == rendered_path1


	@staticmethod
	@pytest.mark.parametrize(
		('rendered_path1', 'rendered_path2', 'expected_lt', 'expected_eq'),
		[
			(RenderableData(["a"], False, "", 0), RenderableData(["a", "b"], False, "", 0), True, False),
			(RenderableData(["a", "b"], False, "", 0), RenderableData(["b"], False, "", 0), True, False),
			(RenderableData(["b"], False, "", 0), RenderableData([], False, "", 1), True, False),

			(RenderableData([], False, "", 0), RenderableData([], False, "", 0), False, True),
			(RenderableData([], False, "", 0), RenderableData(["a"], False, "", 0), True, False),
			(RenderableData(["a"], False, "", 0), RenderableData(["a"], False, "", 0), False, True),
			(RenderableData(["a"], False, "", 0), RenderableData([], False, "", 1), True, False),

			(RenderableData([], False, "", 1), RenderableData([], False, "", 1), False, True),
			(RenderableData([], False, "", 1), RenderableData(["a"], False, "", 1), True, False),
			(RenderableData(["a"], False, "", 1), RenderableData(["a"], False, "", 1), False, True),
			(RenderableData(["a"], False, "", 1), RenderableData([], False, "", 2), True, False),

			(RenderableData([], False, "", 2), RenderableData([], False, "", 2), False, True),
			(RenderableData([], False, "", 2), RenderableData(["a"], False, "", 2), True, False),
			(RenderableData(["a"], False, "", 2), RenderableData(["a"], False, "", 2), False, True),
			(RenderableData(["a"], False, "", 2), RenderableData([], False, "C", 0), True, False),

			(RenderableData([], False, "C", 0), RenderableData([], False, "C", 0), False, True),
			(RenderableData([], False, "C", 0), RenderableData(["a"], False, "C", 0), True, False),
			(RenderableData(["a"], False, "C", 0), RenderableData(["a"], False, "C", 0), False, True),
			(RenderableData(["a"], False, "C", 0), RenderableData([], False, "C", 1), True, False),

			(RenderableData([], False, "C", 1), RenderableData([], False, "C", 1), False, True),
			(RenderableData([], False, "C", 1), RenderableData(["a"], False, "C", 1), True, False),
			(RenderableData(["a"], False, "C", 1), RenderableData(["a"], False, "C", 1), False, True),
			(RenderableData(["a"], False, "C", 1), RenderableData([], True, "", 0), True, False),

			(RenderableData([], True, "", 0), RenderableData([], True, "", 0), False, True),
			(RenderableData([], True, "", 0), RenderableData(["a"], True, "", 0), True, False),
			(RenderableData(["a"], True, "", 0), RenderableData(["a"], True, "", 0), False, True),
			(RenderableData(["a"], True, "", 0), RenderableData([], True, "C", 0), True, False),

			(RenderableData([], True, "C", 0), RenderableData([], True, "C", 0), False, True),
			(RenderableData([], True, "C", 0), RenderableData(["a"], True, "C", 0), True, False),
			(RenderableData(["a"], True, "C", 0), RenderableData(["a"], True, "C", 0), False, True),
			(RenderableData(["a"], True, "C", 0), RenderableData([], True, "D", 0), True, False),
		],
		indirect=['rendered_path1', 'rendered_path2']
	)
	def test_order(
		rendered_path1: render.PosixRenderedPath,
		rendered_path2: render.PosixRenderedPath,
		expected_lt: bool,
		expected_eq: bool,
	):
		"""
			Test `__eq__()`, `__lt__()`, `__lte__()`, `__gt__()` and `__gte__()`.
		"""
		expected_lte = expected_lt or expected_eq
		expected_gt = ((not expected_lt) and (not expected_eq))
		expected_gte = expected_gt or expected_eq

		result = rendered_path1 == rendered_path2
		assert result == expected_eq
		result = rendered_path2 == rendered_path1
		assert result == expected_eq

		result = rendered_path1 < rendered_path2
		assert result == expected_lt
		result = rendered_path2 > rendered_path1
		assert result == expected_lt

		result = rendered_path1 <= rendered_path2
		assert result == expected_lte
		result = rendered_path2 >= rendered_path1
		assert result == expected_lte

		result = rendered_path1 > rendered_path2
		assert result == expected_gt
		result = rendered_path2 < rendered_path1
		assert result == expected_gt

		result = rendered_path1 >= rendered_path2
		assert result == expected_gte
		result = rendered_path2 <= rendered_path1
		assert result == expected_gte



def test_platforms():
	"""
		Test `get_type()` for different platforms.
	"""
	for platform in Platform:
		rendered_type = render.get_type(platform)
		assert issubclass(rendered_type, render.RenderedPath)
