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
Module contains objects to manipulate, execute and resolve the ConfigSync configuration.
"""

import pickle
import os

class ConfigSyncConfigContainer:
    """
    Container of the ConfigSync local configuration. The configuration is not synchronized
    remotelly and is store under user home directory in .configsync folder.
    """
    def __init__(self):
        """
        Initialize the configuration container. All the values are initialized to empty
        strings and the synchonization flag is set to False. The file list is initialized
        to empty set as there is nothing synced yet.
        """
        self.name = ''
        self.path = ''
        self.repo = ''
        self.synced = False
        self.files = {}

    def addFile(self, _file, _synced):
        """
        Add a file into list of synced files. Every entry consists of an original file
        name and a local file name the remote file is synced with. The 'file name' means
        a full path in this case.
        
        :param _file: Original file name (remote)
        :type _file: string
        :param _synced: Local sync target file
        :type _synced: string
        """
        if not _file in self.files:
            self.files[_file] = _synced

    def delFile(self, _file):
        """
        Delete a file entry from the list. It occurs when the file is not synchronized
        any more.
        
        :param _file: Full path of the synchronized file
        :type _file: string
        """
        del self.files[_file]

    def existsFile(self, _file):
        """
        Check the (remote) file existence in the list of synchronized files.
        
        :param _file: Full path of the expected synchronized file
        :type _file: string
        :return: True if the file exists in the list
        :rtype: bool
        """
        return _file in self.files

    def getValue(self, _file):
        """
        Return a name of the local file which is synchronized with the file given in
        parameter
        
        :param _file: Full path of the synchronized file
        :type _file: string
        :return: Full path of the local file which is synchronized with the given one
        :rtype: string
        """
        return self.files[_file]


class ConfigSyncFilesContainer:
    """
    Container of file list. This file list is synchornized.
    The file list consists from trio - file name, file original owner, count of linked sides
    """
    def __init__(self):
        """
        Initialize list of files. By default the list is empty after initialization.
        """
        self.files = {}

    def addFile(self, _file, _owner):
        """
        Add a file into a list of remote files. Every file is represented by its name with
        name of computer of its origin and count of linked sides. The count of linked
        sides is set to *1*.
        
        :param _file: Full name of the synchronized file
        :type _file: string
        :param _owner: Name of the computer of the file's origin
        :type _owner: string
        """
        if not self.existsFile(_file):
            self.files[_file] = [_owner, 1]

    def delFile(self, _file):
        """
        Deete a file entry from the list of synced files. The file should be deleted after
        the count of synced sides goes bellow *1*.
        
        :param _file: Full name of the synchronized file
        :type _file: string 
        """
        del self.files[_file]

    def addFileLink(self, _file):
        """
        Increase the count of synced sides by *1*.
        
        :param _file: Full name of the synchronized file
        :type _file: string
        """
        if self.existsFile(_file):
            self.files[_file][1] = self.files[_file][1] + 1

    def delFileLink(self, _file):
        """
        Decrease the count of synced sides by *1*. It also checks ify the count goes
        bellow *1*. It's represented by the return value.
        
        :param _file: Full name of the synchronized file
        :type _file: string
        :return: True if the decreasing makes the count be bellow *1* and the actual file deleting is needed.
        :rtype: bool
        """
        if self.existsFile(_file):
            cnt = self.files[_file][1]
            if cnt == 1:
                return True
            elif cnt > 1:
                self.files[_file][1] = cnt - 1
                return False
        else:
            return False

    def existsFile(self, _file):
        """
        Check the (remote) file existence in the list of synchronized files.
        
        :param _file: Full name of the synchronized file
        :type _file: string
        """
        return _file in self.files



class ConfigSyncConfig:
    """
    This class is supposed to manipulate the ConfigSync configuration. It also stores the
    list of remotelly synchronized files and methods to load/store configuration from/to
    files.
    """
    def __init__(self):
        """
        Initialize the ConfigSyncConfig class. ConfigSync default home directory is set
        to ~/.configsync and in this directory the configuration is stored as well as the
        git working directory. Also the name of configuration file is set. Part of
        initialization is restoring stored configuration (if any) and file list (if any).
        """
        self.homeDir = os.path.expanduser("~") + '/.configsync/'
        self.confFile = '.config'
        self.filesFile = ''
        self.data = ConfigSyncConfigContainer()
        self.files = ConfigSyncFilesContainer()
        self.restoreConfiguration()
        self.restoreFileList()

    def setConfigDefaults(self):
        """
        Set default values to configuration if there's no configuration stored yet.
        """
        self.data.name = 'My Synchronized Machine'
        self.data.path = self.homeDir + 'syncdir/'
        self.data.repo = 'ssh://git@gitserver.tld/user_name/repo.git'
        self.data.synced = False

    def restoreFileList(self):
        """
        Restore file list from remote directory if exists. Otherwise clear the file list
        as there shouldn't be any files stored. This should be called after
        ConfigSync.restoreConfiguration() method as the file list should be in the git
        working directory set in configuration.
        """
        self.filesFile = self.data.path + "/.files"
        if os.path.exists(self.filesFile):
            f = open(self.filesFile,"rb")
            self.files.files = pickle.load(f)
        else:
            self.files.files.clear()

    def storeFileList(self):
        """
        Store file list to a file on remote directory.
        """
        f = open(self.filesFile, "wb+")
        pickle.dump(self.files.files, f)
        f.close()

    def restoreConfiguration(self):
        """
        Restore stored configuration from a file or create the path to the configuration
        file and set the default values.
        """
        if os.path.exists(self.homeDir + self.confFile):
            f = open(self.homeDir + self.confFile, "rb")
            self.data = pickle.load(f)
            f.close()
            self.data.synced = True
        else:
            if not os.path.exists(self.homeDir):
                os.mkdir(self.homeDir)
            self.setConfigDefaults()

    def storeConfiguration(self):
        """
        Store configuration into file to make them persistent.
        """
        self.data.synced = True
        f = open(self.homeDir + self.confFile, "wb+")
        pickle.dump(self.data, f)
        f.close()
