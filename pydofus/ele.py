#!/usr/bin/python3
# -*- coding: utf-8 -*-

import zlib, tempfile, io
from ._binarystream import _BinaryStream
from collections import OrderedDict

class InvalidELEFile(Exception):
    def __init__(self, message):
        super(InvalidELEFile, self).__init__(message)
        self.message = message

class ELE:
    def __init__(self, stream):
        self._stream = stream

    def read(self):
        ele_uncompressed = tempfile.TemporaryFile()
        ele_uncompressed.write(zlib.decompress(self._stream.read()))
        ele_uncompressed.seek(0)

        raw = _BinaryStream(ele_uncompressed, True)

        ele = Element(raw)
        ele.read()

        ele_uncompressed.close()

        return ele.getObj()

    def write(self, obj):
        buffer = tempfile.TemporaryFile()
        buffer_stream = _BinaryStream(buffer, True)

        #raw = _BinaryStream(self._stream, True)

        ele = Element(buffer_stream)
        #ele = Element(raw)
        ele.setObj(obj)
        ele.write()

        buffer.seek(0)

        self._stream.write(zlib.compress(buffer.read()))

        buffer.close()

class Element:
    def __init__(self, raw):
        self._raw = raw
        self._obj = OrderedDict()

    def raw(self):
        return self._raw

    def read(self):
        self._obj["header"] = self.raw().read_char()
        self._obj["fileVersion"] = self.raw().read_char()
        self._obj["elementsCount"] = self.raw().read_uint32()

        #self._obj["elementsIndex"] = OrderedDict()
        self._obj["elementsIndex"] = []

        skypLen = 0
        for i in range(0, self._obj["elementsCount"]):
            if self._obj["fileVersion"] >= 9:
                skypLen = self.raw().read_uint16()

            edId = self.raw().read_int32()
            #edType = self.raw().read_char()
            self._obj["elementsIndex"].append(edId)

            self.raw().position(self.raw().position() + (skypLen - 4));

            #data = { "type":edType }

            #self._obj["elementsIndex"][edId] = data

            #self._obj["elementsIndex"][edId] = self.raw().position()

        #if self._obj["fileVersion"] >= 8:


    def write(self):
        self.raw().write_char(69) # header
        self.raw().write_char(9) # fileVersion
        self.raw().write_uint32(self._obj["elementsCount"]) # elementsCount
        #for i in range(0, self._obj["elementsCount"]):
        for edId in self._obj["elementsIndex"]:
            self.raw().write_uint16(7) # skypLen
            self.raw().write_int32(edId) # elementId
            self.raw().write_char(4) # elementType
            self.raw().write_int16(1) # scriptId
        self.raw().write_int32(0) # gfxCount

    def getObj(self):
        return self._obj

    def setObj(self, obj):
        self._obj = obj
