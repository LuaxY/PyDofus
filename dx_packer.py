import sys, json
from pydofus.dx import DX, InvalidDXFile

file = sys.argv[1]

swf_input = open(file, "rb")
dx_output = open(file.replace("swf", "dx"), "wb")

dx = DX(dx_output)
dx.write(swf_input)

swf_input.close()
dx_output.close()
