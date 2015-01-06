#!/usr/bin/python3
# -*- coding: utf-8 -*-

from ._binarystream import _BinaryStream
from collections import OrderedDict
import zlib, tempfile, io

# Exceptions


class InvalidDLMFile(Exception):
    def __init__(self, message):
        super(InvalidDLMFile, self).__init__(message)
        self.message = message

# Class itself


class DLMReader:
    """Read DLM files"""
    def __init__(self, stream, key, autoload=True):
        """Init the class with the informations about files in the DLM"""

        # Uncompress zlib map
        dlm_uncompressed = tempfile.TemporaryFile()
        dlm_uncompressed.write(zlib.decompress(stream.read()))
        dlm_uncompressed.seek(0)

        # Attributes
        self._stream = dlm_uncompressed
        self._key = key

        # TODO: add properties

        self._loaded = False

        # Load the DLM
        DLM_file_binary = _BinaryStream(self._stream, True)

        if autoload:
            self.load()

        dlm_uncompressed.close()

    def load(self):
        """Load the class with the actual DML files in it"""
        # Populate _Files

        if self._loaded:
            raise Exception("DML instance is already populated.")

        DLM_file_binary = _BinaryStream(self._stream, True)

        # TODO: read file infos
        header = DLM_file_binary.read_byte()[0]
        mapVersion = DLM_file_binary.read_byte()[0]
        mapId = DLM_file_binary.read_uint32()

        print("header: " + str(header))
        print("mapVersion: " + str(mapVersion))
        print("mapId: " + str(mapId))

        #print(int.from_bytes(mapVersion, byteorder="big"))

        if mapVersion >= 7:
            encrypted = DLM_file_binary.read_bool()
            encryptionVersion = DLM_file_binary.read_byte()
            dataLen = DLM_file_binary.read_int32()

            print("encrypted: " + str(encrypted))
            print("encryptionVersion: " + str(encryptionVersion[0]))
            print("dataLen: " + str(dataLen))

            if encrypted:
                encryptedData = DLM_file_binary.read_bytes(dataLen)
                decryptedData = bytearray()
                for i in range(0, dataLen):
                    a = encryptedData[i]
                    b = ord(self._key[i % len(self._key)][0])
                    decryptedData.append(a ^ b)

                tmp = io.BytesIO(decryptedData)
                raw = _BinaryStream(tmp, True)

                relativeId = raw.read_uint32()
                mapType = raw.read_byte()[0]
                subareaId = raw.read_int32()
                topNeighbourId = raw.read_int32()
                bottomNeighbourId = raw.read_int32()
                leftNeighbourId = raw.read_int32()
                rightNeighbourId = raw.read_int32()
                shadowBonusOnEntities  = raw.read_int32()

                print("relativeId: " + str(relativeId))
                print("mapType: " + str(mapType))
                print("subareaId: " + str(subareaId))
                print("topNeighbourId: " + str(topNeighbourId))
                print("bottomNeighbourId: " + str(bottomNeighbourId))
                print("leftNeighbourId: " + str(leftNeighbourId))
                print("rightNeighbourId: " + str(rightNeighbourId))
                print("shadowBonusOnEntities: " + str(shadowBonusOnEntities))

                if mapVersion >= 3:
                    backgroundRed = raw.read_byte()[0]
                    backgroundGreen = raw.read_byte()[0]
                    backgroundBlue = raw.read_byte()[0]
                    backgroundColor = (backgroundRed & 255) << 16 | (backgroundGreen & 255) << 8 | backgroundBlue & 255

                if mapVersion >= 4:
                    zoomScale = raw.read_uint16()
                    zoomOffsetX = raw.read_int16()
                    zoomOffsetY = raw.read_int16()

                useLowPassFilter = raw.read_bool()
                useReverb = raw.read_bool()

                if useReverb:
                    presetId = raw.read_int32()
                else:
                    presetId = -1

                backgroundsCount = raw.read_byte()[0]
                # TODO: check code
                foregroundsCount = raw.read_byte()[0]
                # TODO: check code
                unknown_1 = raw.read_int32()
                groundCRC = raw.read_int32()
                layersCount = raw.read_byte()[0]

                print("backgroundRed: " + str(backgroundRed))
                print("backgroundGreen: " + str(backgroundGreen))
                print("backgroundBlue: " + str(backgroundBlue))
                print("backgroundColor: " + str(backgroundColor))
                print("zoomScale: " + str(zoomScale))
                print("zoomOffsetX: " + str(zoomOffsetX))
                print("zoomOffsetY: " + str(zoomOffsetY))
                print("useLowPassFilter: " + str(useLowPassFilter))
                print("useReverb: " + str(useReverb))
                print("presetId: " + str(presetId))
                print("backgroundsCount: " + str(backgroundsCount))
                print("foregroundsCount: " + str(foregroundsCount))
                print("groundCRC: " + str(groundCRC))
                print("layersCount: " + str(layersCount))

                # TODO: create Layer class
                # TODO: create cellData class

        self._loaded = True

    # Accessors

    def _get_stream(self):
        return self._stream

    def _get_loaded(self):
        return self._loaded

    # Properties

    stream = property(_get_stream)
    loaded = property(_get_loaded)
