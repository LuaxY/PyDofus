d2p-tool
===========

Python 3.x scripts to compress/uncompress Dofus 2 files .d2p and .swl

Usage
-----

#####Uncompress

Place .d2p files in `./input` folder and run uncompress.py

`python uncompress.py`

Data extracted is located in `./output` folder.

#####Compress

Place original .d2p files in `./input` folder, uncompress it  
Edit your files in `./output/{file.d2p}`  
And now run compress.py

`python compress.py {file.d2p} {swl ture|false}`

Data extracted is located in `./output/~generated` folder.

###Authors

**Marvin Roger** ([marvinroger](https://github.com/marvinroger)) : d2p/swl compress and uncompress lib  
**Yann Guineau** ([LuaxY](https://github.com/LuaxY)) : automated scripts for compress/uncompress d2p/swl
