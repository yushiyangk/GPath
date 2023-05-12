from dataclasses import dataclass
from typing import Optional

import pytest

from gpath import GPath


class TestGPath:
	@staticmethod
	@pytest.fixture
	def gpath1(request: pytest.FixtureRequest) -> GPath:
		return GPath(request.param)

	@staticmethod
	@pytest.fixture
	def gpath2(request: pytest.FixtureRequest) -> GPath:
		return GPath(request.param)

	@staticmethod
	@pytest.fixture
	def expected_gpath(request: pytest.FixtureRequest) -> Optional[GPath]:
		if request.param is None:
			return None
		else:
			return GPath(request.param)


@dataclass
class RenderableData:
	named_parts: list[str]
	absolute: bool
	drive: str
	parent_level: int

	@property
	def relative_parts(self) -> list[str]:
		return [".." for i in range(self.parent_level)] + self.named_parts
