Dofus-Tools [![Build Status](https://travis-ci.org/marvinroger/Dofus-Tools.png)](https://travis-ci.org/marvinroger/Dofus-Tools)
===========

Python 3.x scripts to interact with Dofus 2.x special files, like .SWL or .D2P.

Usage
-----

#####Decompilation

Place .d2p files in `./input` folder and run uncompress.py

`python uncompress.py`

Data extracted is located in `./output` folder.

#####Compilation

Place original .d2p in `./input` folder, uncompress it  
Edit your files in `./output/your-file.d2p`  
And now run compress.py

`python compress.py your-file.d2p`

Data extracted is located in `./output/~generated` folder.

###Authors

**Marvin Roger** ([marvinroger](https://github.com/marvinroger)) : d2p/swl compress and uncompress lib  
**Yann Guineau** ([LuaxY](https://github.com/LuaxY)) : automated scripts for compress/uncompress d2p/swl
