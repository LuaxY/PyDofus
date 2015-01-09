#!/usr/bin/python3
# -*- coding: utf-8 -*-

import zlib, tempfile, io, unicodedata
from ._binarystream import _BinaryStream
from collections import OrderedDict

class InvalidDXFile(Exception):
    def __init__(self, message):
        super(InvalidDXFile, self).__init__(message)
        self.message = message

class DX:
    def __init__(self, stream):
        self._stream = stream
        self._obj = OrderedDict()

    def read(self, out):
        raw = _BinaryStream(self._stream, True)
        out_stream = _BinaryStream(out, True)

        file = raw.read_char()
        version = raw.read_char()
        keyLen = raw.read_int16()
        key = raw.read_bytes(keyLen)

        swfDataPosition = self._stream.tell()
        swfData = raw.read_bytes()
        swfLenght = self._stream.tell() - swfDataPosition

        for i in range(0, swfLenght):
            out_stream.write_uchar(swfData[i] ^ key[i % keyLen])

    def write(self, obj):
        raw = _BinaryStream(self._stream, True)
