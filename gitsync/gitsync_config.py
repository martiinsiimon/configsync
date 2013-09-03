#!/usr/bin/python
#-*- coding: UTF-8 -*-

"""
Author:         Martin Simon
Email:          martiin.siimon@gmail.com
Git:            https://github.com/martiinsiimon/gitsync
License:        See bellow
Project info:   GitSync is an easy tool to maintain small files synchronization
                over remote git repository. It's not supposed to synchronize
                big files. To such files use services as DropBox or SpiderOak.
                The main purpose is to synchronize config files among very
                similar systems to keep them sycnhronized and as much same
                as possible.
File info:      This file contains objects to manipulate, execute and resolve
                the GitSync configuration.

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

import pickle
#import json
import os

class GitSyncConfigContainer:
    def __init__(self):
        self.name = ''
        self.path = ''
        self.repo = ''
        self.synced = False
        self.files = {}

    def addFile(self, _file, _synced):
        if not _file in self.files:
            self.files[_file] = _synced

    def delFile(self, _file):
        del self.files[_file]

    def existsFile(self, _file):
        return _file in self.files

    def getValue(self, _file):
        return self.files[_file]


class GitSyncFilesContainer:
    """
    Container of file list. This file list is synchornized.
    The file list consists from trio - file name, file original owner, count of linked sides
    """
    def __init__(self):
        self.files = {}

    def addFile(self, _file, _owner):
        if not self.existsFile(_file):
            self.files[_file] = [_owner, 1]

    def delFile(self, _file):
        del self.files[_file]

    def addFileLink(self, _file):
        if self.existsFile(_file):
            self.files[_file][1] = self.files[_file][1] + 1

    def delFileLink(self, _file):
        if self.existsFile(_file):
            cnt = self.files[_file][1]
            if cnt == 1:
                return True #TODO do git remove and remove the file from repository
            elif cnt > 1:
                self.files[_file][1] = cnt - 1
                return False
        else:
            return False

    def existsFile(self, _file):
        return _file in self.files



class GitSyncConfig:
    def __init__(self):
        self.confFile = '.gitsync.config'
        self.filesFile = ''
        self.data = GitSyncConfigContainer()
        self.files = GitSyncFilesContainer()
        self.restoreConfiguration()
        self.restoreFileList()

    def setConfigDefaults(self):
        self.data.name = 'My Synchronized Machine'
        self.data.path = '/home/martin/.gitsync/'
        self.data.repo = 'ssh://git@bitbucket.org/martiinsiimon/synchronization.git'
        self.data.synced = False

    def restoreFileList(self):
        """
        Restore file list from remote directory
        """
        print("DBG: filelist restored")
        self.filesFile = self.data.path + "/.files"
        if os.path.exists(self.filesFile):
            f = open(self.filesFile,"rb")
            self.files.files = pickle.load(f)
        else:
            self.files.files.clear()

    def storeFileList(self):
        """
        Store file list to the file on remote directory
        """
        print("DBG: filelist stored")
        f = open(self.filesFile, "wb+")
        pickle.dump(self.files.files, f)
        f.close()

    def restoreConfiguration(self):
        """
        Restore stored configuration
        """
        print("DBG: configuration restored")

        if os.path.exists(self.confFile):
            f = open(self.confFile,"rb")
            self.data = pickle.load(f)
            f.close()
            self.data.synced = True
        else:
            self.setConfigDefaults()

    def storeConfiguration(self):
        """
        Store configuration into file to make them persistent
        """
        print("DBG: configuration stored")
        self.data.synced = True
        f = open(self.confFile, "wb+")
        pickle.dump(self.data, f)
        f.close()
