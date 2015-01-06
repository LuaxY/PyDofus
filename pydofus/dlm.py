#!/usr/bin/python3
# -*- coding: utf-8 -*-

import zlib, tempfile, io
from ._binarystream import _BinaryStream
from collections import OrderedDict

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

        m = Map(DLM_file_binary, self._key)
        m.read()
        m.debug()

        self._loaded = True

class Map:
    def __init__(self, raw, key):
        self._raw = raw
        self._key = key

        self.topArrowCell = []
        self.bottomArrowCell = []
        self.leftArrowCell = []
        self.rightArrowCell = []

    def read(self):
        self.header = self._raw.read_char()
        self.mapVersion = self._raw.read_char()
        self.mapId = self._raw.read_uint32()

        if self.mapVersion >= 7:
            self.encrypted = self._raw.read_bool()
            self.encryptionVersion = self._raw.read_char()
            self.dataLen = self._raw.read_int32()

            if self.encrypted:
                self.encryptedData = self._raw.read_bytes(self.dataLen)
                decryptedData = bytearray()
                for i in range(0, self.dataLen):
                    decryptedData.append(self.encryptedData[i] ^ ord(self._key[i % len(self._key)][0]))

                tmp = io.BytesIO(decryptedData)
                self._raw = _BinaryStream(tmp, True)

                self.relativeId = self._raw.read_uint32()
                self.mapType = self._raw.read_char()
                self.subareaId = self._raw.read_int32()
                self.topNeighbourId = self._raw.read_int32()
                self.bottomNeighbourId = self._raw.read_int32()
                self.leftNeighbourId = self._raw.read_int32()
                self.rightNeighbourId = self._raw.read_int32()
                self.shadowBonusOnEntities  = self._raw.read_int32()

                if self.mapVersion >= 3:
                    self.backgroundRed = self._raw.read_char()
                    self.backgroundGreen = self._raw.read_char()
                    self.backgroundBlue = self._raw.read_char()
                    self.backgroundColor = (self.backgroundRed & 255) << 16 | (self.backgroundGreen & 255) << 8 | self.backgroundBlue & 255

                if self.mapVersion >= 4:
                    self.zoomScale = self._raw.read_uint16()
                    self.zoomOffsetX = self._raw.read_int16()
                    self.zoomOffsetY = self._raw.read_int16()

                self.useLowPassFilter = self._raw.read_bool()
                self.useReverb = self._raw.read_bool()

                if self.useReverb:
                    self.presetId = self._raw.read_int32()
                else:
                    self.presetId = -1

                self.backgroundsCount = self._raw.read_char()
                # TODO: Fixture
                self.foregroundsCount = self._raw.read_char()
                # TODO: Fixture
                self.cellsCount = 560 # MAP_CELLS_COUNT
                self.unknown_1 = self._raw.read_int32()
                self.groundCRC = self._raw.read_int32()
                self.layersCount = self._raw.read_char()

                self.layers = []
                for i in range(0, self.layersCount):
                    la = Layer(self, self.mapVersion)
                    la.read()
                    self.layers.append(la)

                self.cells = []
                for i in range(0, self.cellsCount):
                    cd = CellData(self, i, self.mapVersion)
                    cd.read()
                    self.cells.append(cd)

    def write(self):
        pass

    def debug(self):
        print("header: " + str(self.header))
        print("mapVersion: " + str(self.mapVersion))
        print("mapId: " + str(self.mapId))
        print("encrypted: " + str(self.encrypted))
        print("encryptionVersion: " + str(self.encryptionVersion))
        print("dataLen: " + str(self.dataLen))
        print("relativeId: " + str(self.relativeId))
        print("mapType: " + str(self.mapType))
        print("subareaId: " + str(self.subareaId))
        print("topNeighbourId: " + str(self.topNeighbourId))
        print("bottomNeighbourId: " + str(self.bottomNeighbourId))
        print("leftNeighbourId: " + str(self.leftNeighbourId))
        print("rightNeighbourId: " + str(self.rightNeighbourId))
        print("shadowBonusOnEntities: " + str(self.shadowBonusOnEntities))
        print("backgroundRed: " + str(self.backgroundRed))
        print("backgroundGreen: " + str(self.backgroundGreen))
        print("backgroundBlue: " + str(self.backgroundBlue))
        print("backgroundColor: " + str(self.backgroundColor))
        print("zoomScale: " + str(self.zoomScale))
        print("zoomOffsetX: " + str(self.zoomOffsetX))
        print("zoomOffsetY: " + str(self.zoomOffsetY))
        print("useLowPassFilter: " + str(self.useLowPassFilter))
        print("useReverb: " + str(self.useReverb))
        print("presetId: " + str(self.presetId))
        print("backgroundsCount: " + str(self.backgroundsCount))
        print("foregroundsCount: " + str(self.foregroundsCount))
        print("cellsCount: " + str(self.cellsCount))
        print("unknown_1: " + str(self.unknown_1))
        print("groundCRC: " + str(self.groundCRC))
        print("layersCount: " + str(self.layersCount))

        for i in range(0, self.layersCount):
            la = self.layers[i]
            la.debug()

        for i in range(0, self.cellsCount):
            cd = self.cells[i]
            cd.debug()

        print("topArrowCell: " + str(self.topArrowCell))
        print("bottomArrowCell: " + str(self.bottomArrowCell))
        print("leftArrowCell: " + str(self.leftArrowCell))
        print("rightArrowCell: " + str(self.rightArrowCell))

class Fixture:
    def __init__(self, map):
        self._map = map
        self._raw = map._raw

    def read(self):
        pass

    def write(self):
        pass

    def debug(self):
        pass

class Layer:
    def __init__(self, map, mapVersion):
        self._map = map
        self._raw = map._raw
        self.mapVersion = mapVersion

    def read(self):
        self.layerId = self._raw.read_int32()
        self.cellsCount = self._raw.read_int16()

        self.cells = []
        for i in range(0, self.cellsCount):
            ce = Cell(self, self.mapVersion)
            ce.read()
            self.cells.append(ce)

    def write(self):
        pass

    def debug(self):
        print("\tlayerId: " + str(self.layerId))
        print("\tcellsCount: " + str(self.cellsCount))

        for i in range(0, self.cellsCount):
            ce = self.cells[i]
            ce.debug()

class Cell:
    def __init__(self, layer, mapVersion):
        self._layer = layer
        self._raw = layer._raw
        self.mapVersion = mapVersion

    def read(self):
        self.cellId = self._raw.read_int16()
        self.elementsCount = self._raw.read_int16()

        self.elements = []
        for i in range(0, self.elementsCount):
            el = BasicElement.GetElementFromType(self, self._raw.read_char(), self.mapVersion)
            el.read()
            self.elements.append(el)

    def write(self):
        pass

    def debug(self):
        print("\t\tcellId: " + str(self.cellId))
        print("\t\telementsCount: " + str(self.elementsCount))

        for i in range(0, self.elementsCount):
            el = self.elements[i]
            el.debug()

class CellData:
    def __init__(self, map, id, mapVersion):
        self._map = map
        self._raw = map._raw
        self.cellId = id
        self.mapVersion = mapVersion

    def read(self):
        self.floor = self._raw.read_char() # * 10
        self.losmov = self._raw.read_uchar()
        self.speed = self._raw.read_char()
        self.mapChangeData = self._raw.read_uchar()

        if self.mapVersion > 5:
            self.moveZone = self._raw.read_uchar()
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

    def debug(self):
        pass

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
        self.mapVersion = mapVersion

    def read(self):
        self.elementId = self._raw.read_uint32()

        # hue
        self._raw.read_byte()
        self._raw.read_byte()
        self._raw.read_byte()

        # shadow
        self._raw.read_byte()
        self._raw.read_byte()
        self._raw.read_byte()

        if self.mapVersion <= 4:
            self.pixelOffsetX = self._raw.read_char()
            self.pixelOffsetY = self._raw.read_char()
        else:
            self.pixelOffsetX = self._raw.read_int16()
            self.pixelOffsetY = self._raw.read_int16()

        self.altitude = self._raw.read_char()
        self.identifier = self._raw.read_uint32()

    def write(self):
        pass

    def debug(self):
        print("\t\t\telementId: " + str(self.elementId))
        print("\t\t\tpixelOffsetX: " + str(self.pixelOffsetX))
        print("\t\t\tpixelOffsetY: " + str(self.pixelOffsetY))
        print("\t\t\taltitude: " + str(self.altitude))
        print("\t\t\tidentifier: " + str(self.identifier))

class SoundElement:
    def __init__(self, cell, mapVersion):
        self._cell = cell
        self._raw = cell._raw
        self.mapVersion = mapVersion

    def read(self):
        self.soundId = self._raw.read_int32()
        self.baseVolume = self._raw.read_int16()
        self.fullVolumeDistance = self._raw.read_int32()
        self.nullVolumeDistance = self._raw.read_int32()
        self.minDelayBetweenLoops = self._raw.read_int16()
        self.maxDelayBetweenLoops = self._raw.read_int16()

    def write(self):
        pass

    def debug(self):
        print("\t\t\tsoundId: " + str(self.soundId))
        print("\t\t\tbaseVolume: " + str(self.baseVolume))
        print("\t\t\tfullVolumeDistance: " + str(self.fullVolumeDistance))
        print("\t\t\tnullVolumeDistance: " + str(self.nullVolumeDistance))
        print("\t\t\tminDelayBetweenLoops: " + str(self.minDelayBetweenLoops))
        print("\t\t\tmaxDelayBetweenLoops: " + str(self.maxDelayBetweenLoops))
