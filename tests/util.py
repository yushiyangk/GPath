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
