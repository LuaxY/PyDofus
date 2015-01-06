#!/usr/bin/python3
# -*- coding: utf-8 -*-

import zlib, tempfile, io
from ._binarystream import _BinaryStream

class InvalidDLMFile(Exception):
    def __init__(self, message):
        super(InvalidDLMFile, self).__init__(message)
        self.message = message

class DLMReader:
    """Read DLM files"""
    def __init__(self, stream, key=None, autoload=True):
        """Init the class with the informations about files in the DLM"""

        if key == None:
            raise InvalidDLMFile("Map decryption key is empty.")

        # Uncompress zlib map
        dlm_uncompressed = tempfile.TemporaryFile()
        dlm_uncompressed.write(zlib.decompress(stream.read()))
        dlm_uncompressed.seek(0)

        # Attributes
        self._stream = dlm_uncompressed
        self._key = key

        self._loaded = False

        if autoload:
            self.load()

        dlm_uncompressed.close()

    def load(self):
        """Load the class with the actual DML files in it"""

        if self._loaded:
            raise Exception("DML instance is already populated.")

        DLM_file_binary = _BinaryStream(self._stream, True)

        self._map = Map(DLM_file_binary, self._key)
        self._map.read()

        self._loaded = True

    def json(self):
        return self._map.json()

class Map:
    def __init__(self, raw, key):
        self._raw = raw
        self._key = key
        self._obj = {}

        self.topArrowCell = []
        self.bottomArrowCell = []
        self.leftArrowCell = []
        self.rightArrowCell = []

    def read(self):
        self._obj["header"] = self._raw.read_char()
        self._obj["mapVersion"] = self._raw.read_char()
        self._obj["mapId"] = self._raw.read_uint32()

        if self._obj["mapVersion"] >= 7:
            self._obj["encrypted"] = self._raw.read_bool()
            self._obj["encryptionVersion"] = self._raw.read_char()
            self.dataLen = self._raw.read_int32()

            if self._obj["encrypted"]:
                self.encryptedData = self._raw.read_bytes(self.dataLen)
                decryptedData = bytearray()
                for i in range(0, self.dataLen):
                    decryptedData.append(self.encryptedData[i] ^ ord(self._key[i % len(self._key)][0]))

                tmp = io.BytesIO(decryptedData)
                self._raw = _BinaryStream(tmp, True)

        self._obj["relativeId"] = self._raw.read_uint32()
        self._obj["mapType"] = self._raw.read_char()
        self._obj["subareaId"] = self._raw.read_int32()
        self._obj["topNeighbourId"] = self._raw.read_int32()
        self._obj["bottomNeighbourId"] = self._raw.read_int32()
        self._obj["leftNeighbourId"] = self._raw.read_int32()
        self._obj["rightNeighbourId"] = self._raw.read_int32()
        self._obj["shadowBonusOnEntities"]  = self._raw.read_int32()

        if self._obj["mapVersion"] >= 3:
            self._obj["backgroundRed"] = self._raw.read_char()
            self._obj["backgroundGreen"] = self._raw.read_char()
            self._obj["backgroundBlue"] = self._raw.read_char()
            self._obj["backgroundColor"] = (self._obj["backgroundRed"] & 255) << 16 | (self._obj["backgroundGreen"] & 255) << 8 | self._obj["backgroundBlue"] & 255

        if self._obj["mapVersion"] >= 4:
            self._obj["zoomScale"] = self._raw.read_uint16()
            self._obj["zoomOffsetX"] = self._raw.read_int16()
            self._obj["zoomOffsetY"] = self._raw.read_int16()

        self._obj["useLowPassFilter"] = self._raw.read_bool()
        self._obj["useReverb"] = self._raw.read_bool()

        if self._obj["useReverb"]:
            self._obj["presetId"] = self._raw.read_int32()
        else:
            self._obj["presetId"] = -1

        self._obj["backgroundsCount"] = self._raw.read_char()
        self._obj["backgroundFixtures"] = []
        for i in range(0, self._obj["backgroundsCount"]):
            bg = Fixture(self)
            bg.read()
            self._obj["backgroundFixtures"].append(bg.json())

        self._obj["foregroundsCount"] = self._raw.read_char()
        self._obj["foregroundsFixtures"] = []
        for i in range(0, self._obj["foregroundsCount"]):
            fg = Fixture(self)
            fg.read()
            self._obj["foregroundsFixtures"].append(fg.json())

        self._obj["cellsCount"] = 560 # MAP_CELLS_COUNT
        self._obj["unknown_1"] = self._raw.read_int32()
        self._obj["groundCRC"] = self._raw.read_int32()
        self._obj["layersCount"] = self._raw.read_char()

        self._obj["layers"] = []
        for i in range(0, self._obj["layersCount"]):
            la = Layer(self, self._obj["mapVersion"])
            la.read()
            self._obj["layers"].append(la.json())

        self._obj["cells"] = []
        for i in range(0, self._obj["cellsCount"]):
            cd = CellData(self, i, self._obj["mapVersion"])
            cd.read()
            self._obj["cells"].append(cd.json())

    def write(self):
        pass

    def json(self):
        return self._obj

class Fixture:
    def __init__(self, map):
        self._map = map
        self._raw = map._raw
        self._obj = {}

    def read(self):
        self._obj["fixtureId"] = self._raw.read_int32()
        self._obj["offsetX "]= self._raw.read_int16()
        self._obj["offsetY"] = self._raw.read_int16()
        self._obj["rotation"] = self._raw.read_int16()
        self._obj["xScale"] = self._raw.read_int16()
        self._obj["yScale"] = self._raw.read_int16()
        self._obj["redMultiplier"] = self._raw.read_char()
        self._obj["greenMultiplier"] = self._raw.read_char()
        self._obj["lueMultiplier"] =  self._raw.read_char()
        self._obj["hue"] = self._obj["redMultiplier"] | self._obj["greenMultiplier"] | self._obj["blueMultiplier"]
        self._obj["alpha"] =  self._raw.read_uchar()

    def write(self):
        pass

    def json(self):
        return self._obj

class Layer:
    def __init__(self, map, mapVersion):
        self._map = map
        self._raw = map._raw
        self._obj = {}
        self.mapVersion = mapVersion

    def read(self):
        self._obj["layerId"] = self._raw.read_int32()
        self._obj["cellsCount"] = self._raw.read_int16()

        self._obj["cells"] = []
        for i in range(0, self._obj["cellsCount"]):
            ce = Cell(self, self.mapVersion)
            ce.read()
            self._obj["cells"].append(ce.json())

    def write(self):
        pass

    def json(self):
        return self._obj

class Cell:
    def __init__(self, layer, mapVersion):
        self._layer = layer
        self._raw = layer._raw
        self._obj = {}
        self.mapVersion = mapVersion

    def read(self):
        self._obj["cellId"] = self._raw.read_int16()
        self._obj["elementsCount"] = self._raw.read_int16()

        self._obj["elements"] = []
        for i in range(0, self._obj["elementsCount"]):
            el = BasicElement.GetElementFromType(self, self._raw.read_char(), self.mapVersion)
            el.read()
            self._obj["elements"].append(el.json())

    def write(self):
        pass

    def json(self):
        return self._obj

class CellData:
    def __init__(self, map, id, mapVersion):
        self._map = map
        self._raw = map._raw
        self._obj = {}
        self.cellId = id
        self.mapVersion = mapVersion

    def read(self):
        self._obj["floor"] = self._raw.read_char() # * 10
        self._obj["losmov"] = self._raw.read_uchar()
        self._obj["speed"] = self._raw.read_char()
        self._obj["mapChangeData"] = self._raw.read_uchar()

        if self.mapVersion > 5:
            self._obj["moveZone"] = self._raw.read_uchar()
        if self.mapVersion > 7:
            tmpBits = self._raw.read_char()
            self.arrow = 15 & tmpBits

            if self.useTopArrow():
                self._map.topArrowCell.append(self.cellId)

            if self.useBottomArrow():
                self._map.bottomArrowCell.append(self.cellId)

            if self.useLeftArrow():
                self._map.leftArrowCell.append(self.cellId)

            if self.useRightArrow():
                self._map.rightArrowCell.append(self.cellId)

    def write(self):
        pass

    def json(self):
        return self._obj

    def useTopArrow(self):
        if (self.arrow & 1) == 0:
            return False
        else:
            return True

    def useBottomArrow(self):
        if (self.arrow & 2) == 0:
            return False
        else:
            return True

    def useLeftArrow(self):
        if (self.arrow & 4) == 0:
            return False
        else:
            return True

    def useRightArrow(self):
        if (self.arrow & 8) == 0:
            return False
        else:
            return True

class BasicElement:
    def GetElementFromType(cell, type, mapVersion):
        if type == 2: # GRAPHICAL
            return GraphicalElement(cell, mapVersion)
        elif type == 33: # SOUND
            return SoundElement(cell, mapVersion)

class GraphicalElement:
    def __init__(self, cell, mapVersion):
        self._cell = cell
        self._raw = cell._raw
        self._obj = {}
        self.mapVersion = mapVersion

        self._obj["elementName"] = "Graphical"

    def read(self):
        self._obj["elementId"] = self._raw.read_uint32()

        # hue
        self._raw.read_byte()
        self._raw.read_byte()
        self._raw.read_byte()

        # shadow
        self._raw.read_byte()
        self._raw.read_byte()
        self._raw.read_byte()

        if self.mapVersion <= 4:
            self._obj["offsetX"] = self._raw.read_char()
            self._obj["offsetY"] = self._raw.read_char()
        else:
            self._obj["offsetX"] = self._raw.read_int16()
            self._obj["offsetY"] = self._raw.read_int16()

        self._obj["altitude"] = self._raw.read_char()
        self._obj["identifier"] = self._raw.read_uint32()

    def write(self):
        pass

    def json(self):
        return self._obj

class SoundElement:
    def __init__(self, cell, mapVersion):
        self._cell = cell
        self._raw = cell._raw
        self._obj = {}
        self.mapVersion = mapVersion

        self._obj["elementName"] = "Sound"

    def read(self):
        self._obj["soundId"] = self._raw.read_int32()
        self._obj["baseVolume"] = self._raw.read_int16()
        self._obj["fullVolumeDistance"] = self._raw.read_int32()
        self._obj["nullVolumeDistance"] = self._raw.read_int32()
        self._obj["minDelayBetweenLoops"] = self._raw.read_int16()
        self._obj["maxDelayBetweenLoops"] = self._raw.read_int16()

    def write(self):
        pass

    def json(self):
        return self._obj
