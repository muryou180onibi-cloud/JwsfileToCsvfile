import pytest
from Jws2Csv.extractor import Extractor
from typing import List, Tuple

# Dummy Extractor for testing without real files
class DummyExtractor(Extractor):
    def read_header(self) -> None:
        self.sample_name = "TestSample"
        self.comment = "TestComment"
        self.numchanells = 2
        self.npoints = 3
        self.x_for_first_point = 400.0
        self.x_for_last_point = 402.0
        self.x_increment = 1.0

    def read_data(self) -> List[Tuple[float, ...]]:
        # X data + Y channel data
        return [
            (400.0, 401.0, 402.0),  # X
            (0.1, 0.2, 0.3),        # Y1
            (0.4, 0.5, 0.6)         # Y2
        ]


def test_read_header() -> None:
    extractor = DummyExtractor("dummy.jws")
    extractor.read_header()
    assert extractor.sample_name == "TestSample"
    assert extractor.comment == "TestComment"
    assert extractor.numchanells == 2
    assert extractor.npoints == 3


def test_read_data() -> None:
    extractor = DummyExtractor("dummy.jws")
    extractor.read_header()
    data = extractor.read_data()
    assert isinstance(data, list)
    assert all(isinstance(row, tuple) for row in data)
    assert data[0] == (400.0, 401.0, 402.0)  # X data
