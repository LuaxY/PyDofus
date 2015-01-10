import sys, json
from pydofus.ele import ELE, InvalidELEFile

# python ele_pack.py file.json
# file output: file.ele

file = sys.argv[1]

json_input = open(file, "r")
ele_output = open(file.replace(".json", ".ele"), "wb")

ele = ELE(ele_output)
data = ele.write(json.load(json_input))

json_input.close()
ele_output.close()
