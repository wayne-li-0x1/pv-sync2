#!/usr/bin/env python
#-*-coding: utf-8 -*-
#pylint: disable=W0141

import os
import exifread
import hashlib
import string

def FillFileInfo(fn, info=None):
    if info == None:
        info = {}
    stat = os.stat(fn)
    info["size"] = stat.st_size
    info["atime"] = (int)(stat.st_atime)
    info["mtime"] = (int)(stat.st_mtime)
    info["ctime"] = (int)(stat.st_ctime)
    return info


def FillImgInfo(fn, info=None):
    if info == None:
        info = {}
    FillFileInfo(fn, info)

    fp = open(fn, 'rb')
    try:
        exif = exifread.process_file(fp)
    except Exception, e:
        print "Exif Read Error: " , e
        return None

    try:
        exif["EXIF DateTimeOriginal"]
    except:

        fp.close()
        return None

    if "EXIF LensModel" in exif and 'iPhone 5' in exif["EXIF LensModel"].values:
        info["DeviceId"] = "ip5"
    else:
        info["DeviceId"] = None

    dt = exif["EXIF DateTimeOriginal"].values
    dt = dt.encode("utf-8")
    year = dt.split(":")[0].strip()
    month = dt.split(":")[1].strip()
    #dt = dt.translate(None, ':')
    tbl = string.maketrans(' :','-.')
    dt = dt.translate(tbl)
    info["PicTakenTime"]  = dt
    info["year"]  = year
    info["month"]  = month 
    
    fp.close()

    return info

def FillMd5(fn, info=None):
    if info == None:
        info = {}

    fp = open(fn, 'rb')

    #md5
    fp.seek(0,0) #to beginning
    md5 = hashlib.md5(fp.read()).hexdigest()
    info["md5"] = md5

    fp.close()

    return info
