import os
import pytest
from Jws2Csv import cli
from Jws2Csv.extractor import Extractor

# Patch Extractor in cli to use DummyExtractor
class DummyExtractor(Extractor):
    def read_header(self) -> None:
        self.sample_name = "TestSample"
        self.comment = "TestComment"
        self.numchanells = 2
        self.npoints = 3
        self.x_for_first_point = 400.0
        self.x_for_last_point = 402.0
        self.x_increment = 1.0

    def read_data(self):
        return [
            (400.0, 401.0, 402.0),  # X
            (0.1, 0.2, 0.3),        # Y1
            (0.4, 0.5, 0.6)         # Y2
        ]


def test_main_creates_csv(tmp_path):
    # Prepare dummy JWS folder
    jws_folder = tmp_path / "JWS"
    jws_folder.mkdir()
    (jws_folder / "dummy.jws").write_text("dummy")

    # Prepare CSV output folder
    csv_folder = tmp_path / "CSV"
    csv_folder.mkdir()

    # Patch cli.py paths
    original_jws_path = cli.JWS_FOLDER = str(jws_folder)
    original_csv_path = cli.CSV_FOLDER = str(csv_folder)

    # Patch Extractor class
    cli.Extractor = DummyExtractor

    # Run main
    cli.main()

    # Check CSV file exists
    csv_files = list(csv_folder.glob("*.csv"))
    assert len(csv_files) == 1
    content = csv_files[0].read_text()
    assert "TestSample" in content
    assert "Wavelength,Absorbance" in content
