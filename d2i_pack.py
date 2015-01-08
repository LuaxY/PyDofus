import sys, json
from pydofus.d2i import D2I, InvalidD2IFile
from collections import OrderedDict

file = sys.argv[1]

json_input = open(file, "r", encoding="utf-8")
d2i_output = open(file.replace("json", "d2i"), "wb")

d2i = D2I(d2i_output)
data = d2i.write(json.load(json_input, object_pairs_hook=OrderedDict))

json_input.close()
d2i_output.close()
