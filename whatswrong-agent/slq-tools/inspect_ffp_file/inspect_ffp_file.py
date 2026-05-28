#!/usr/bin/python3
# vim: et: ts=4: sw=4: nows: ai
"""@copyright Confidential Proprietary, Copyright 2018-2022 GE Healthcare

Tools for reading FFP files as defined by DOC1147345

"""
import logging
import ctypes
import os
import hashlib
import io
try:
    import numpy
except ImportError:
    numpy = None

logger = logging.getLogger(__name__)

HIQ_MAX_SEGMENTS=64
HIQ_MAGIC_NUMBER=0xe9d7c5b3

_segNames = (
    (0, "PROD_SCAN_DATA_FILE_HDR"),
    (1, "PROD_SCAN_DATA_ACQUISITION_HDR"),
    (2, "PROD_SCAN_DATA_HISTORY_DATA"),
    (3, "PROD_SCAN_DATA_OFFSET_VECTOR_1"),
    (4, "PROD_SCAN_DATA_OFFSET_VECTOR_2"),
    (5, "PROD_SCAN_DATA_CAL_MODULE"),
    (6, "PROD_SCAN_DATA_VIEW_DATA_IEEE"),
    (7, "PROD_SCAN_DATA_VIEW_DATA_FFP"),
    (8, "PROD_SCAN_DATA_VIEW_DATA_PREP_IEEE"),
    (9, "PROD_SCAN_DATA_CARDIAC_EKG_FILE"),
    (10, "PROD_SCAN_DATA_CARDIAC_RPEAK_FILE"),
    (11, "PROD_SCAN_DATA_CAL_MODULE_2"),
    (12, "PROD_SCAN_DATA_Z_POSITION_FILE"),
    (13, "PROD_SCAN_DATA_CAL_MODULE_GSI_MD"),
    (14, "PROD_SCAN_DATA_EXAM_SESSION_FILE"),
    (15, "PROD_SCAN_DATA_EXAM_UIRX_FILE"),
    (16, "PROD_SCAN_DATA_EXAM_RPEAKS_FILE"),
    (17, "PROD_SCAN_DATA_EXAM_EDITED_RPEAKS_FILE"),
    (18, "PROD_SCAN_DATA_EXAM_WAVEFORM_FILE"),
    )

_segByNum = dict(_segNames)
_segByName = dict([(y,x) for (x,y) in _segNames] )

def segNames():
    "Return a tuple of all valid FFP segment names"
    return tuple([a for (a,b) in _segNames ])

def segName(x):
    "Return the name of the specified segment, where x is int"
    if not isinstance(x,int):
        raise TypeError("segName requires an int")
    return _segByNum.get(x,None)

def segNum(name):
    "Return the index of the named segment"
    if not isinstance(name,str):
        raise TypeError("segNum requires name, not '{0}'".format(name))
    return _segByName.get(name,None)

class segment_table_entry_t(ctypes.Structure):
    _fields_ = [
      ("offset", ctypes.c_uint),
      ("num_sets", ctypes.c_uint),
      ("num_vectors", ctypes.c_ushort),
      ("num_elements", ctypes.c_ushort),
      ("element_size", ctypes.c_uint),
    ]
    def __str__(self):
        return "%08d - %d sets, %d vectors, %d elements, %d bytes" % (
            self.offset, self.num_sets, self.num_vectors, self.num_elements, self.element_size )

class filehdr(ctypes.Structure):
    _fields_ = [
        ("magic_number",ctypes.c_uint),
        ("byte_order",ctypes.c_uint),
        ("version",ctypes.c_uint),
        ("offset",ctypes.c_uint),
        ("reserved",ctypes.c_uint),
    ]
    def __str__(self):
        return "filehdr version {0}".format(self.version)

class segment_table_t(ctypes.Structure):
    _fields_ = [
      ("num_segments", ctypes.c_uint),
      ("pad", ctypes.c_uint * 3),
      ("st_segment", segment_table_entry_t * HIQ_MAX_SEGMENTS),
    ]
    def __str__(self):
        return "segment_table_t {0} segments".format(self.num_segments)

class InspectFfpFile(object):
    "A class to inspect an FFP file"

    def __init__(self,filename):
        self.filename = filename
        self._stat = None
        if self.fileSize == 0:
            raise RuntimeError("{0} is an empty file".format(self.filename))

        self.hdr = filehdr()
        with open(self.filename, "rb") as fp:
            fp.readinto(self.hdr)

            if self.hdr.magic_number != HIQ_MAGIC_NUMBER:
                raise RuntimeError("{0} not an IQ file".format(self.filename))

            fp.seek(self.hdr.offset)
            self.tbl = segment_table_t()
            fp.readinto(self.tbl)

    def _nameToNum(self,nameOrNum):
        return nameOrNum if isinstance(nameOrNum,int) else segNum(nameOrNum)

    def __repr__(self):
        return "InspectFfpFile({0})".format(self.baseName)

    def __str__(self):
        segs = [ x for x in self.segmentIter() ]
        numSegs = len(segs)
        xmlValid = ", has session.xml" if self.isValid("PROD_SCAN_DATA_EXAM_SESSION_FILE") else ""
        return ("{self.baseName:15} {self.fileSize} bytes, "
            "{numSegs} segments{xmlValid}").format(**locals())

    @property
    def baseName(self):
        "Equivalent to os.path.basename(self.filename)"
        return os.path.basename(self.filename)

    @property
    def stat(self):
        "Deferred (and cached) stat result for filename"
        if self._stat is None:
            self._stat = os.stat(self.filename)
        return self._stat

    @property
    def fileSize(self):
        "File size reported by os.stat"
        return self.stat.st_size

    @property
    def expectedSize(self):
        "Expected size based on the offset and size of the last segment in the file"
        byOffset = [ (seg.offset, i) for (i,name,seg) in self.segmentIter() ]
        byOffset.sort()
        offset,num = byOffset[-1]
        return offset + self.segSize(num)

    def segmentIter(self,all=False):
        """Iterate over valid segments. Yields a tuple of
           (segment num, segment name, segment struct)
        """
        global _segNames
        for i,name in _segNames:
            if all or self.segSize(i) != 0:
                seg = self._getSegment(i)
                yield (i,name,seg)

    def isValid(self,nameOrNum):
        "Returns True if the given segment is valid"
        return self._getSegment(nameOrNum).num_sets != 0

    def _getSegment(self,nameOrNum):
        num = self._nameToNum(nameOrNum)
        return self.tbl.st_segment[num]

    def segSize(self,nameOrNum):
        "Size of the specified segment"
        seg = self._getSegment(nameOrNum)
        return seg.num_sets * seg.num_vectors * seg.num_elements * seg.element_size
    
    def segOffset(self,nameOrNum):
        "Offset of the specified segment"
        return self._getSegment(nameOrNum).offset

    def segSignature(self,nameOrNum,hasher="md5"):
        "Compute the MD5 (or other hashlib supported) hash for the given signature"
        data = self.mapSegment(nameOrNum)
        m = hashlib.new(hasher)
        m.update(data)
        return m

    def mapSegment(self,nameOrNum):
        """Return a numpy.memmap of the given segment
           The mapping has dtype=numpy.uint8 and is shaped if the segment is
           PROD_SCAN_DATA_VIEW_DATA_FFP or PROD_SCAN_DATA_CAL_MODULE
           Raises RuntimeError if numpy is not available
        """
        if numpy is None:
            raise RuntimeError("numpy not available")
            
        num = self._nameToNum(nameOrNum)
        name = segName(num)
        seg = self._getSegment(num)
        offset = self.segOffset(num)
        mapping = numpy.memmap(self.filename, dtype=numpy.uint8, mode='r', offset=offset)

        sizeBytes = self.segSize(nameOrNum)

        ret = mapping[:sizeBytes]
        num_sets = seg.num_sets
        if ret.size != sizeBytes:
            num_sets = ret.size // seg.element_size
            logger.warning("{0} has only {1} of {2} sets".format(name,num_sets,seg.num_sets))
            sizeBytes = num_sets * seg.element_size
            ret = mapping[:sizeBytes]

        if name in  ("PROD_SCAN_DATA_VIEW_DATA_FFP","PROD_SCAN_DATA_CAL_MODULE"):
            ret = ret.reshape((num_sets, seg.element_size))
        return ret

    def readSegment(self,nameOrNum):
        "Read the specified segment and return raw bytes"
        seg = self._getSegment(nameOrNum)
        with open(self.filename, 'rb') as fp:
            fp.seek(self.segOffset(nameOrNum))
            # return fp.read(self.segSize(nameOrNum))
            return fp.read(13920)
        
    def writeSegment(self, nameOrNum, blob):
        with open(self.filename, 'rb+') as fp:
            fp.seek(self.segOffset(nameOrNum))
            fp.write(blob)

__all__ = [ "InspectFfpFile","segNum","segName","segNames" ]
