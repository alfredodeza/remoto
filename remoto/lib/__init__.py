import sys
import os
this_dir = os.path.abspath(os.path.dirname(__file__))

if this_dir not in sys.path:
    sys.path.insert(0, this_dir)
import execnet
