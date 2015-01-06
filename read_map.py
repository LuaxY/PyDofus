import io, sys, os, tempfile, fnmatch, json
from collections import OrderedDict
from pydofus.dlm import DLMReader, InvalidDLMFile
from pydofus._binarystream import _BinaryStream

dlm_input = open("94116864.dlm", "rb")
dlm_reader = DLMReader(dlm_input, "649ae451ca33ec53bbcbcc33becf15f4")
