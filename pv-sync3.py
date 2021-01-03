#!/usr/bin/env python3
#-*-coding: utf-8 -*-
#pylint: disable=W0141

"""
pv-sync.py from_dir to_dir

DESCRITPION:
    sync all pictures and videos from <from_dir> to <to_dir> and keep them organized in a decent way.

    It will also do following things.
    1. record the importing
    2. the imported filename is uniq to
        YYYY-MM-DD-SS-<MD5[0:5].jpg
    3. An index file is maintained to track all the information.

    4. only deal with .jpg .png .mov 
"""

import sys
import os

if __name__ != "__main__":
    sys.exit(0)

FROM_DIR = sys.argv[1]
TO_DIR = sys.argv[2]

FROM_DIR_ABS = os.path.abspath(FROM_DIR)
TO_DIR_ABS = os.path.abspath(TO_DIR)

#==============================================================================
# program body
#==============================================================================
import logging
logging.basicConfig()

from PVSync import *

syncer = PVSync(FROM_DIR, TO_DIR)

syncer.sync_all_picture_video()
