import json
from pydofus.dlm import DLMReader, InvalidDLMFile

dlm_input = open("94116864.dlm", "rb")
dlm_reader = DLMReader(dlm_input, "649ae451ca33ec53bbcbcc33becf15f4")
print(json.dumps(dlm_reader.json(), indent=2))
