from binaryninja.enums import SegmentFlag
from binaryninja.binaryview import BinaryView
from binaryninja.architecture import Architecture


class N64View(BinaryView):
    name = 'N64'
    long_name = 'Nintendo 64 ROM'

    @classmethod
    def is_valid_for_data(self, data):
        header = data.read(0x3b, 0x3d)
        return header == b'N'

    def __init__(self, data):
        # data is a binaryninja.binaryview.BinaryView
        BinaryView.__init__(self, parent_view=data, file_metadata=data.file)
        self.platform = Architecture['N64'].standalone_platform
        self.data = data

    def init(self):
        # self.add_auto_segment(0, 0x1000000, 0, 0x1000, SegmentFlag.SegmentReadable | SegmentFlag.SegmentExecutable)
        self.add_entry_point(0x0040)
        return True

    def perform_is_executable(self):
        return True

    def perform_get_entry_point(self):
        return 0x0040
