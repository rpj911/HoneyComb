import ctypes
# from ScanSysData import EXAM_LEVEL_INFO_TYPE, SERIES_LEVEL_INFO_TYPE, SCAN_LEVEL_INFO_TYPE
from AcqHeaderDefination.ScanSysData import EXAM_LEVEL_INFO_TYPE, SERIES_LEVEL_INFO_TYPE, SCAN_LEVEL_INFO_TYPE

class ACQUISITION_HEADER_TYPE(ctypes.Structure):
    _fields_ = [
        ('padding_front', ctypes.c_byte * 408),
        ('scan_number', ctypes.c_int32),
        ('padding_middle', ctypes.c_byte * 36),
        ('exam_level_info', EXAM_LEVEL_INFO_TYPE),
        # ('padding_back', ctypes.c_byte * 11184)
        ('series_level_info', SERIES_LEVEL_INFO_TYPE),
        ('scan_level_info', SCAN_LEVEL_INFO_TYPE),
        ('padding_back', ctypes.c_byte * 8056)
    ]

def calcStructureInfo(struct_type):
    print(f"Size of {struct_type.__name__}: {ctypes.sizeof(struct_type)} bytes")
    # for field_name, field_type in struct_type._fields_:
    #     offset = ctypes.addressof(getattr(ctypes.pointer(struct_type()), field_name).contents)
    #     print(f"Offset of {field_name}: {offset} bytes")
    for field_name, field_type in struct_type._fields_:
        temp_struct = struct_type()
        offset = ctypes.addressof(getattr(temp_struct, field_name)) - ctypes.addressof(temp_struct)
        print(f"Offset of {field_name}: {offset} bytes")

if __name__ == "__main__":
    calcStructureInfo(ACQUISITION_HEADER_TYPE)
    # calcStructureInfo(EXAM_LEVEL_INFO_TYPE)
    # calcStructureInfo(SERIES_LEVEL_INFO_TYPE)
    # calcStructureInfo(SCAN_LEVEL_INFO_TYPE)