import olefile  # type: ignore
from struct import pack, unpack
from typing import Iterator, List, Tuple
from olefile import OleFileIO

DATAINFO_FMT = '<LLLLLLdddLLLLdddd'


class Extractor:
    filename: str
    file: OleFileIO
    data: bytes
    numchanells: int
    npoints: int
    x_for_first_point: float
    x_for_last_point: float
    x_increment: float
    sample_name: str
    comment: str

    def __init__(self, filename: str) -> None:
        """
        Initialize the Extractor with a JWS file path.
        """
        self.filename = filename
        self.sample_name = ''
        self.comment = ''
        self.numchanells = 0
        self.npoints = 0
        self.x_for_first_point = 0.0
        self.x_for_last_point = 0.0
        self.x_increment = 0.0

    def read_header(self) -> None:
        """
        Read the header information from the JWS file and extract metadata.
        """
        self.file = OleFileIO(self.filename)
        self.data = self.file.openstream('DataInfo').read()[:96]
        data_tuple = unpack(DATAINFO_FMT, self.data)

        self.numchanells = data_tuple[3]
        self.npoints = data_tuple[5]
        self.x_for_first_point = data_tuple[6]
        self.x_for_last_point = data_tuple[7]
        self.x_increment = data_tuple[8]

        # Read sample info bytes
        sample_info_bytes = self.file.openstream('SampleInfo').read()[8:].split(
            b'\x00\x00\x00\x54\x00\x00\x00'
        )

        self.decode_sample_info(sample_info_bytes)

    def read_data(self) -> List[Tuple[float, ...]]:
        """
        Read the Y-Data from the JWS file and return as list of tuples.
        """
        if not self.file.exists('Y-Data'):
            raise Exception("Y-Data not found!")

        y_data: bytes = self.file.openstream('Y-Data').read()
        fmt: str = 'f' * self.npoints

        try:
            unpacked_data: List[Tuple[float, ...]] = self.unpackY(y_data, fmt, self.numchanells)
        except Exception:
            raise Exception("Error unpacking Y-Data!")

        return unpacked_data

    def unpackY(self, y_data: bytes, format: str, num_chanels: int) -> List[Tuple[float, ...]]:
        """
        Unpack Y data into tuples per channel and prepend X data.
        """
        chunk_size: int = int(len(y_data) / num_chanels)
        data_chunked: List[bytes] = [y_data[i:i + chunk_size] for i in range(0, len(y_data), chunk_size)]
        unpacked_data: List[Tuple[float, ...]] = [unpack(format, chunk) for chunk in data_chunked]

        # Generate X data and insert at the beginning
        x_data: List[float] = list(self.frange(self.x_for_first_point, self.x_for_last_point + self.x_increment, self.x_increment))
        unpacked_data.insert(0, tuple(x_data))
        return unpacked_data

    def frange(self, start: float, stop: float = 0, step: float = 1.0) -> Iterator[float]:
        """
        Return evenly spaced numbers over a specified range.
        """
        count = 0
        while True:
            value = round(start + count * step, 2)
            if step > 0 and value >= stop:
                break
            elif step < 0 and value <= stop:
                break
            yield value
            count += 1

    def decode_sample_info(self, sample_info_bytes: List[bytes]) -> None:
        """
        Decode sample name and comment from raw sample info bytes.
        """
        if len(sample_info_bytes) == 2:
            sample_name = sample_info_bytes[0].split(b'\x00\x00')[0]
            self.sample_name = self.unpack_sample_info(sample_name)

            comment = sample_info_bytes[1].split(b'\x00\x00')[0]
            self.comment = self.unpack_sample_info(comment)

        elif len(sample_info_bytes) == 1:
            sample_name = sample_info_bytes[0].split(b'\x00\x00')[0]
            self.sample_name = self.unpack_sample_info(sample_name)
            self.comment = ''

    def unpack_sample_info(self, packed_bytes: bytes) -> str:
        """
        Convert packed bytes into a UTF-16 string.
        """
        if packed_bytes[-1:] not in {b'\x00', b''}:
            packed_bytes += b'\x00'

        format_specifier: str = f'{len(packed_bytes)}s'
        unpacked_str: str = unpack(format_specifier, packed_bytes)[0].decode('utf16')
        return unpacked_str
