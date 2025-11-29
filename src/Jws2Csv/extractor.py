from struct import pack, unpack
from typing import Iterator
from olefile import OleFileIO

DATAINFO_FMT = '<LLLLLLdddLLLLdddd'

class Extractor:
    filename = ""
    file = None
    data = None
    numchanells = 0
    npoints = None
    x_for_first_point = 0
    x_for_last_point = 0
    x_increment = 0
    sample_name = ''
    comment = ''


    def __init__(self,filename):
        self.filename = filename

    def read_header(self):
        self.file = OleFileIO(self.filename)
        self.data = self.file.openstream('DataInfo').read()
        self.data = self.data[:96]
        data_tuple = unpack(DATAINFO_FMT, self.data)
        self.numchanells = data_tuple[3]
        self.npoints = data_tuple[5]
        self.x_for_first_point = data_tuple[6]
        self.x_for_last_point = data_tuple[7]
        self.x_increment = data_tuple[8]

        sample_info_bytes = self.file.openstream('SampleInfo').read()[8:].split(b'\x00\x00\x00\x54\x00\x00\x00')

        # try:
        self.decode_sample_info(sample_info_bytes)
        # except Exception:
        #     self.sample_name = ''
        #     self.comment = ''

    def read_data(self):
        if not self.file.exists('Y-Data'):
            raise Exception("Y-Data not found!")
        y_data = self.file.openstream('Y-Data').read()
        fmt = 'f'*self.npoints
        try:
            unpacked_data = self.unpackY(y_data, fmt,self.numchanells)
        except Exception:
            raise Exception("Error unpacking Y-Data!")
        return unpacked_data

    def unpackY(self, y_data: bytes, format: str, num_chanels: int):
            chunk_size = int(len(y_data)/num_chanels)
            data_chunked = [y_data[i:i + chunk_size] for i
                            in range(0, len(y_data), chunk_size)]
            unpacked_data = [unpack(format, data_chunk) for data_chunk in data_chunked]
            # generate x_data
            x_data = self.frange(self.x_for_first_point,
                            self.x_for_last_point + self.x_increment,
                            self.x_increment)

            unpacked_data.insert(0, tuple(x_data))
            return unpacked_data

    def frange(self,start: float, stop: float = 0, step: float = 1.0) -> Iterator[float]:
        """Return evenly spaced number over specified range.

        Args:
            start (float): The starting value of the sequence.
            stop (float): The last value of the sequence.
            step (float): The step for which the sequence is generated.
            """

        count = 0
        while True:
            range = round(start + count * step,2)
            if step > 0 and range >= stop:
                break
            elif step < 0 and range <= stop:
                break
            yield range
            count += 1
    
    def decode_sample_info(self, sample_info_bytes: list):
        if len(sample_info_bytes) == 2:
            sample_name = sample_info_bytes[0].split(b'\x00\x00')[0]
            self.sample_name = (self.unpack_sample_info(sample_name))

            comment = sample_info_bytes[1].split(b'\x00\x00')[0]
            self.comment = self.unpack_sample_info(comment)

        elif len(sample_info_bytes) == 1:
            sample_name = sample_info_bytes[0].split(b'\x00\x00')[0]
            self.sample_name = self.unpack_sample_info(sample_name)
            self.comment = ''

    def unpack_sample_info(self, packed_bytes: bytes) -> str:
        if packed_bytes[-1:] not in {b'\x00', b''}:
            packed_bytes += b'\x00'
        format_specifier = f'{len(packed_bytes)}s'
        unpacked_str = unpack(format_specifier, packed_bytes)[0].decode('utf16')
        return (unpacked_str)
