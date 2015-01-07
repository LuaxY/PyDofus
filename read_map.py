import json
from pydofus.dlm import DLM, InvalidDLMFile

dlm_input = open("94116864.dlm", "rb")
dlm_reader = DLM(dlm_input, "649ae451ca33ec53bbcbcc33becf15f4")
print(json.dumps(dlm_reader.read(), indent=2))
