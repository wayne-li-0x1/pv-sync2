#!/usr/bin/env python
#-*-coding: utf-8 -*-
#pylint: disable=W0141

from ImgInfo import *
import shutil
import sys
import time
import datetime

from DBConfig import *


""" status printing """
"""
1024 scanned, 1021 exists, 2 copied, 1 registered.

"""


class PVSync:
    def __init__(self, from_dir, to_dir):
        self.stat_scanned = 0
        self.stat_exists = 0
        self.stat_copied = 0
        self.stat_registered = 0
        self.from_dir = from_dir
        self.to_dir = to_dir
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)
        self.mydb_path = os.path.join(to_dir, "index.sqlite.db")
        self.mydb = MyDB(DB_CONFIG, self.mydb_path)
        self.mydb.CheckTables()


        return

    def print_stat(self, s):
        print("%d scanned, %d exists, %d copied, %d registered. [ %s ] \r"%(self.stat_scanned, self.stat_exists, self.stat_copied, self.stat_registered,s))

        if self.stat_scanned%10 == 0:
            sys.stdout.flush()
        return


    def sync_all_picture_video(self):
        for root, dirs, files in os.walk(self.from_dir):
            for fn in files:
                fn = os.path.join(root,fn)
                fn_abs = os.path.abspath(fn)
                if fn.lower().endswith(('.jpg', '.jpeg')):
                    self.import_one_picture(fn, ".jpg")
                elif fn.lower().endswith(('.png')):
                    self.import_one_picture(fn, ".png")
                elif fn.lower().endswith(('.heic')):
                    self.import_one_picture(fn, ".heic")
                elif fn.lower().endswith(('.tif')):
                    self.import_one_picture(fn, ".tif")
                elif fn.lower().endswith(('.mov')):
                    self.import_one_video(fn, ".mov")
                else:
                    pass

        print("\n")
        return

    def import_one_video(self, fn, suffix):
        self.stat_scanned = self.stat_scanned + 1
        info = FillFileInfo(fn)
        try:
            exist = self.mydb.Search("TblFile", 
                {
                    "st_size":info["size"],
                    #"st_atime":info["atime"],
                    "st_mtime":info["mtime"],
                    "st_ctime":info["ctime"],
                    "from_abs_path":os.path.abspath(fn)
                }, disconn=False)
        except Exception as e:  
            print(e)
            self.mydb.Close(rollback=False)
            assert 0
            sys.exit(6)

        if exist:
            self.stat_exists = self.stat_exists + 1
            self.print_stat("%s exists"%fn)
            return

        FillMd5(fn, info)

        td = time.strftime("%Y.%m.%d-%H.%M.%S", time.localtime(info["ctime"]))
        newFn = td+"-"+info["md5"][0:5]+suffix
        year = time.strftime("%Y", time.localtime(info["ctime"]))
        month = time.strftime("%m", time.localtime(info["ctime"]))

        to_dir = os.path.join(self.to_dir , "videos")
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)
        to_dir = os.path.join(to_dir, year, month)
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)

        newFnPath = os.path.join(to_dir, newFn)
        newFnPathAbs = os.path.abspath(newFnPath)

        if os.path.exists(newFnPath):
            #print "%s already imported, now registered. "%fn
            try:
                self.mydb.Insert("TblFile", [ info["size"], info["atime"]
                    , info["mtime"], info["ctime"]
                    , os.path.abspath(fn)
                    , info["md5"], newFn ], disconn=True, commit=True)
                self.stat_registered = self.stat_registered + 1
                self.print_stat("registering: %s"%newFnPath)
            except Exception as e:  
                print(e)
                self.mydb.Close(rollback=False)
                assert 0
                sys.exit(5)

            return

        #copy the file
        self.stat_copied = self.stat_copied + 1
        ss = "%s ---> %s" % (fn, newFnPath)
        self.print_stat(ss)

        copy_ok = True
        try:
            shutil.copy2(fn, newFnPath)
            #os.system("cp %s %s" % (fn, newFnPath))
        except:
            copy_ok =False
            pass

        if copy_ok:
            try:
                self.mydb.Insert("TblFile", [ info["size"], info["atime"]
                    , info["mtime"], info["ctime"]
                    , os.path.abspath(fn)
                    , info["md5"], newFn ], disconn=True, commit=True)
            except Exception as e:  
                print(e)
                self.mydb.Close(rollback=False)
                assert 0
                sys.exit(7)


        return

    def import_notag_picture(self, fn, suffix):
        imgInfo = FillFileInfo(fn)

        try:
            exist = self.mydb.Search("TblFile", 
                {
                    "st_size":imgInfo["size"],
                    #"st_atime":imgInfo["atime"],
                    "st_mtime":imgInfo["mtime"],
                    "st_ctime":imgInfo["ctime"],
                    "from_abs_path":os.path.abspath(fn)
                }, disconn=False)
        except Exception as e:  
            print(e)
            self.mydb.Close(rollback=False)
            sys.exit(6)

        #exist = False

        if exist:
            self.stat_exists = self.stat_exists + 1
            self.print_stat("%s exist"%fn)
            return

        FillMd5(fn, imgInfo)

        mt = imgInfo["mtime"]
        ct = imgInfo["ctime"]
        dt = min(mt, ct)
        dt = datetime.datetime.fromtimestamp(dt)
        
        dts = dt.strftime("%Y.%m.%d")

        parts = []
        parts.append(dts)
        parts.append(imgInfo["md5"][0:5])

        newFn = "-".join(parts) + suffix

        year = "notag"
        to_dir = os.path.join(self.to_dir, year)

        if not os.path.exists(to_dir):
            os.makedirs(to_dir)

        year = dt.strftime("%Y")
        to_dir = os.path.join(to_dir, year)
        if not os.path.exists(to_dir):
            os.makedirs(to_dir)

        newFnPath = os.path.join(to_dir, newFn)
        newFnPathAbs = os.path.abspath(newFnPath)

        if os.path.exists(newFnPath):
            #print "%s already imported, now registered. "%fn
            try:
                self.mydb.Insert("TblFile", [ imgInfo["size"], imgInfo["atime"]
                    , imgInfo["mtime"], imgInfo["ctime"]
                    , os.path.abspath(fn)
                    , imgInfo["md5"], newFn ], disconn=True, commit=True)
                self.stat_registered = self.stat_registered + 1
                self.print_stat("registering: %s"%newFnPath)
            except Exception as e:  
                print(e)
                self.mydb.Close(rollback=False)
                assert 0
                sys.exit(5)

            return

        #copy the file
        self.stat_copied = self.stat_copied + 1
        ss = "no EXIF: %s ---> %s" % (fn, newFnPath)
        self.print_stat(ss)

        copy_ok = True
        try:
            shutil.copy2(fn, newFnPath)
        except:
            copy_ok =False
            pass

        if copy_ok:
            try:
                self.mydb.Insert("TblFile", [ imgInfo["size"], imgInfo["atime"]
                    , imgInfo["mtime"], imgInfo["ctime"]
                    , os.path.abspath(fn)
                    , imgInfo["md5"], newFn ], disconn=True, commit=True)
            except Exception as e:  
                print(e)
                self.mydb.Close(rollback=False)
                sys.exit(7)

        self.mydb.Close()
        return
        
    def import_one_picture(self, fn, suffix):
        self.stat_scanned = self.stat_scanned+1

        imgInfo = FillImgInfo(fn)
        if imgInfo == None:
            self.import_notag_picture(fn, suffix)

            return

        try:
            exist = self.mydb.Search("TblFile", 
                {
                    "st_size":imgInfo["size"],
                    #"st_atime":imgInfo["atime"],
                    "st_mtime":imgInfo["mtime"],
                    "st_ctime":imgInfo["ctime"],
                    "from_abs_path":os.path.abspath(fn)
                }, disconn=False)
        except Exception as e:  
            print(e)
            self.mydb.Close(rollback=False)
            sys.exit(6)

        if exist:
            self.stat_exists = self.stat_exists + 1
            self.print_stat("%s exist"%fn)
            return

        FillMd5(fn, imgInfo)

        parts = []
        parts.append(imgInfo["PicTakenTime"])
        dev =  imgInfo["DeviceId"]
        if dev: 
            parts.append(dev)
        parts.append(imgInfo["md5"][0:5])

        newFn = "-".join(parts) + suffix

        year = imgInfo["year"]
        month = imgInfo["month"]
        to_dir = os.path.join(self.to_dir, year, month)

        if not os.path.exists(to_dir):
            os.makedirs(to_dir)

        newFnPath = os.path.join(to_dir, newFn)
        newFnPathAbs = os.path.abspath(newFnPath)

        if os.path.exists(newFnPath):
            #print "%s already imported, now registered. "%fn
            try:
                self.mydb.Insert("TblFile", [ imgInfo["size"], imgInfo["atime"]
                    , imgInfo["mtime"], imgInfo["ctime"]
                    , os.path.abspath(fn)
                    , imgInfo["md5"], newFn ], disconn=True, commit=True)
                self.stat_registered = self.stat_registered + 1
                self.print_stat("registering: %s"%newFnPath)
            except Exception as e:  
                print(e)
                self.mydb.Close(rollback=False)
                assert 0
                sys.exit(5)

            #return

        #copy the file
        self.stat_copied = self.stat_copied + 1
        ss = "%s ---> %s" % (fn, newFnPath)
        self.print_stat(ss)

        copy_ok = True
        try:
            shutil.copy2(fn, newFnPath)
        except:
            copy_ok =False
            pass

        if copy_ok:
            try:
                self.mydb.Insert("TblFile", [ imgInfo["size"], imgInfo["atime"]
                    , imgInfo["mtime"], imgInfo["ctime"]
                    , os.path.abspath(fn)
                    , imgInfo["md5"], newFn ], disconn=True, commit=True)
            except Exception as e:  
                print(e)
                self.mydb.Close(rollback=False)
                sys.exit(7)

        return
        
