import sys, json
from pydofus.dx import DX, InvalidDXFile

file = sys.argv[1]

dx_input = open(file, "rb")
swf_output = open(file.replace("dx", "swf"), "wb")

dx = DX(dx_input)
dx.read(swf_output)

#swf_output.write(data)

dx_input.close()
swf_output.close()
