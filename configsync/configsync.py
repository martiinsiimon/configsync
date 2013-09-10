#!/usr/bin/python3
#-*- coding: UTF-8 -*-

"""
Author:         Martin Simon
Email:          martiin.siimon@gmail.com
Git:            https://github.com/martiinsiimon/configsync
License:        See bellow
Project info:   ConfigSync is a tool with purpose to easy synchronize system config files
                over remote storage - git. It uses git repository because of its
                availability and easy way how to track file changes and origins. The main
                purpose is to synchronize config files among very similar systems to keep
                them sycnhronized and as much same as possible.
File info:      This is the main file, executive one. Using this file ConfigSync
                is started into the GUI as well as into the CLI variant.

The MIT License (MIT)

Copyright (c) 2013 Martin Simon

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from configsync_gui import ConfigSyncGui
from configsync_config import ConfigSyncConfig
from configsync_core import ConfigSyncCore
from gi.repository import Gtk, GObject, Gdk
import argparse
import sys
import os


def printConfiguration():
    config = ConfigSyncConfig()
    print("Machine name [name]:\t", config.data.name)
    print("Repository [repo]:\t", config.data.repo)
    print("Working path [path]:\t", config.data.path)
    print("Synchronized files:")
    for f in config.data.files:
        print("\t",f)

def setConfiguration(key,val):
    config = ConfigSyncConfig()
    if key == "name":
        config.data.name = val
    elif key == "repo":
        config.data.repo = val
        config.data.synced = False
    elif key == "path":
        config.data.path = val
        config.data.synced = False
    else:
        print("The entered key",key,"has not been found!")

    config.storeConfiguration()

    if not config.data.synced:
        gsc = ConfigSyncCore()
        gsc.initialize()

def addFile(f):
    #FIXME update this function
    config = ConfigSyncConfig()
    if not config.data.synced:
        gsc = ConfigSyncCore()
        gsc.initialize()

    if os.path.isfile(f):
        config.data.addFile(f,f)
        config.storeConfiguration()
    else:
        print("Your requested file does not exists!") #TODO is this problem?

def removeFile(f):
    #FIXME update this function
    config = ConfigSyncConfig()
    if not config.data.synced:
        gsc = ConfigSyncCore()
        gsc.initialize()

    config.data.delFile(f)
    config.storeConfiguration()

if __name__ == "__main__":
    params = argparse.ArgumentParser("./configsync.py", description = "ConfigSync - synchronize system config files")
    group = params.add_mutually_exclusive_group()
    group.add_argument("-s", "--synchronize", action = "store_true", dest = "par_sync", required = False, help = "Synchronize now")
    group.add_argument("-l", "--list", action = "store_true", dest = "par_list", required = False, help = "Show configuration")
    group.add_argument("-c", "--config", nargs = 2, type = str, metavar = ("KEY","VALUE"),dest = "par_conf", required = False, help = "Set a new value")
    group.add_argument("-a", "--add", action = "store", dest = "par_add", required = False, help = "Add a file to synchronize")
    group.add_argument("-r", "--remove", action = "store", dest = "par_remove", required = False, help = "Remove a file from synchronization")
    group.add_argument("-w", "--wizard", action = "store_true", dest = "par_wizard", required = False, help = "Start graphical wizard")
    #TODO CLI wizard?

    try:
        args = params.parse_args()
    except:
        sys.exit(1)


    if args.par_sync or args.par_list or args.par_conf != None or args.par_add != None or args.par_remove != None:
        """The CLI variant will be started"""
        if args.par_list:
            """List configuration"""
            printConfiguration()

        elif args.par_conf != None:
            setConfiguration(args.par_conf[0], args.par_conf[1])

        elif args.par_sync:
            gsc = ConfigSyncCore()
            gsc.synchronize()

        elif args.par_add != None:
            addFile(args.par_add)

        elif args.par_remove != None:
            removeFile(args.par_remove)

    else:
        """The GUI variant will be started"""
        GObject.threads_init()
        if args.par_wizard:
            main = ConfigSyncGui(wizard = True)
        else:
            main = ConfigSyncGui()
        Gdk.threads_init()

        Gdk.threads_enter()
        Gtk.main()
        Gdk.threads_leave()
