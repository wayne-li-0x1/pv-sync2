#!/usr/bin/env python
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
import gflags
import os

if __name__ != "__main__":
    sys.exit(0)

#==============================================================================
# Option handling
#==============================================================================
GFLAGS = gflags.FlagValues()
gflags.DEFINE_boolean("help", False, "print help information", GFLAGS)

#option parsing
try:
    GARGV = GFLAGS(sys.argv)
except gflags.FlagsError, e:
    print '%s\n%s\nOPTIONS:\n%s' % (e, __doc__, GFLAGS.MainModuleHelp())
    sys.exit(1)

#option and argument check
if GFLAGS.help:
    print '%s\nOPTIONS:\n%s' % (__doc__, GFLAGS.MainModuleHelp())
    sys.exit(0)

try:
    GARGV[1]
    GARGV[2]
except:
    print '%s\nOPTIONS:\n%s' % (__doc__, GFLAGS.MainModuleHelp())
    sys.exit(2)

FROM_DIR = GARGV[1]
TO_DIR = GARGV[2]

FROM_DIR_ABS = os.path.abspath(GARGV[1])
TO_DIR_ABS = os.path.abspath(GARGV[2])

#==============================================================================
# program body
#==============================================================================
import logging
logging.basicConfig()

from PVSync import *

syncer = PVSync(FROM_DIR, TO_DIR)

syncer.sync_all_picture_video()
