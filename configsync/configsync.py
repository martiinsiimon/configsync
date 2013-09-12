#!/usr/bin/env python3
#-*- coding: UTF-8 -*-

# Copyright (c) 2013 Martin Simon
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
This is the main file, executive one. Using this file ConfigSync is started into the GUI
as well as into the CLI variant.
"""

from configsync.configsync_config import ConfigSyncConfig
from configsync.configsync_gui import ConfigSyncGui
from configsync.configsync_core import ConfigSyncCore
from gi.repository import Gtk, GObject, Gdk
import argparse
import sys
import os


def printConfiguration():
    """
    Print formatted configuration
    """
    config = ConfigSyncConfig()
    if not config.data.synced:
        printError('No configuration is stored! You can\'t print configuration if don\'t have any.')
        return False
    print("Machine name [name]:\t", config.data.name)
    print("Repository [repo]:\t", config.data.repo)
    print("Working path [path]:\t", config.data.path)
    print("Synchronized files:")
    for f in config.data.files:
        print("\t",f)

def printError(msg):
    """
    Print error message to stderr

    :param msg: Error message
    :type msg: string
    """
    print(msg, file = sys.stderr)

def cliWizard():
    """
    Command line wizard to ask user for few information about configuration

    :return: False if any error appears during configuration wizard
    :rtype: bool
    """
    print('Welcome to ConfigSync wizard. Please, provide some information to set-up ConfigSync.')

    print('Name of this machine:', end = " ")
    _name = input()

    home = '[' + os.path.expanduser("~") + '/.configsync/syncdir/' + ']'
    print('Working directory ', home, ':', sep = "", end = " ")
    _dir = input()
    if _dir == "" or _dir == "y":
        _dir = os.path.expanduser("~") + '/.configsync/syncdir/'

    print('Git repository:', end = " ")
    _repo = input()

    print()
    print('Summary:\n--------')
    print('Name of machine:  ', _name)
    print('Working directory:', _dir)
    print('Git repository:   ', _repo)

    print()
    while True:
        print('Do you really want to use this configuration [Y/n]?', end = " ")
        _answer = input()

        if _answer == "" or _answer == "y" or _answer == "Y":
            break
        elif _answer == "n" or _answer == "N":
            print('The configuration has not been saved.')
            return


    config = ConfigSyncConfig()
    core = ConfigSyncCore(config)

    if not core.createWorkingDirectory(_dir):
        printError('Unable to create working directory!')
        return False

    if not core.gitClone(_repo, _dir):
        printError('Unable to clone repository!')
        return False

    config.data.name = _name
    config.data.repo = _repo
    config.data.path = _dir
    config.storeConfiguration()

    config.restoreFileList()

    return True

def addFile(f):
    """
    Adds a file to make it synchronized. Few checks are done before the actual addition.

    :param f: Name (path) of a file to be added
    :type f: string
    :return: False if any error appears during file adding
    :rtype: bool
    """
    config = ConfigSyncConfig()
    if not config.data.synced:
        printError('The configuration of configsync is not stored! Execute command `configsync -c`.')
        return False

    if not os.path.isfile(f):
        printError('Your requested file does not exists! Choose existing file instead.')
        return False

    if os.path.getsize(f) > 1048576:
        printError('The selected file is too big! You can\'t synchronize files bigger than 1MB')
        return False

    core = ConfigSyncCore(config)
    config.data.addFile(f,f)
    config.files.addFile(f, self.config.data.name)
    s = config.data.path +"/"+ os.path.basename(f)
    core.linkFile(f, s)
    config.storeFileList()
    config.storeConfiguration()

    core.gitAdd(s)
    core.gitAddFilelist()
    core.gitCommit()

def removeFile(f):
    """
    Removes a file to not synchronize it any more. Few checks are done before the actual
    removing.

    :param f: Name (path) of a file to be removed
    :type f: string
    :return: False if any error appears during file removing
    :rtype: bool
    """
    config = ConfigSyncConfig()
    if not config.data.synced:
        printError('The configuration of configsync is not stored! Execute command `configsync -c`.')
        return False

    if not config.data.existsFile(f):
        printError('The selected file is not synced! You can\'t unlink file which is not linked')
        return False

    core = ConfigSyncCore(config)

    config.data.delFile(f)
    syncedFile = config.data.path + "/" + os.path.basename(f)
    core.unlinkFile(syncedFile)
    if config.files.delFileLink(f):
        core.gitRemove(syncedFile)
        config.files.delFile(f)

    config.storeFileList()
    core.gitAddFilelist()
    core.gitCommit()
    config.storeConfiguration()

    return True

def main():
    """
    Main function, the entry point of whole ConfigSync. Parameters are parsed and
    according to them, appropriate function is chosen. If there isn't any parameter set
    (or parameter `-w`), the graphic interfase is launched.
    """
    params = argparse.ArgumentParser("configsync", description = "ConfigSync - synchronize config files among different systems")
    group = params.add_mutually_exclusive_group()
    group.add_argument("-s", "--synchronize", action = "store_true", dest = "par_sync", required = False, help = "Synchronize now")
    group.add_argument("-l", "--list", action = "store_true", dest = "par_list", required = False, help = "Show configuration")
    group.add_argument("-c", "--configure", action = "store_true", dest = "par_conf", required = False, help = "Start commandline wizard")
    group.add_argument("-a", "--add", action = "store", dest = "par_add", required = False, help = "Add a file to synchronize")
    group.add_argument("-r", "--remove", action = "store", dest = "par_remove", required = False, help = "Remove a file from synchronization")
    group.add_argument("-w", "--wizard", action = "store_true", dest = "par_wizard", required = False, help = "Start graphical wizard")

    try:
        args = params.parse_args()
    except:
        sys.exit(1)


    if args.par_sync or args.par_list or args.par_conf or args.par_add != None or args.par_remove != None:
        """
        The command line variant will be started
        """
        if args.par_list:
            if not printConfiguration():
                sys.exit(1)

        elif args.par_conf:
            if not cliWizard():
                sys.exit(1)

        elif args.par_sync:
            core = ConfigSyncCore()
            core.synchronize()

        elif args.par_add != None:
            if addFile(args.par_add):
                core = ConfigSyncCore()
                core.synchronize()
            else:
                sys.exit(1)

        elif args.par_remove != None:
            if removeFile(args.par_remove):
                core = ConfigSyncCore()
                core.synchronize()
            else:
                sys.exit(1)

    else:
        """
        The GUI variant will be started
        """
        GObject.threads_init()
        if args.par_wizard:
            main = ConfigSyncGui(wizard = True)
        else:
            main = ConfigSyncGui()
        Gdk.threads_init()

        Gdk.threads_enter()
        Gtk.main()
        Gdk.threads_leave()

    sys.exit(0)

if __name__ == "__main__":
    main()
