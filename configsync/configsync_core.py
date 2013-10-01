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
Module contains the core of ConfigSync synchronization. It contains all the real
functionality of git control and file manipulation. Take a look into implemented methods
to get more perspective.
"""

from configsync.configsync_config  import ConfigSyncConfig
import os
import subprocess
import shutil
import time

class ConfigSyncCore:
    """
    ConfigSync synchronization core.
    """
    def __init__(self, _config = ConfigSyncConfig()):
        """
        Initialize class. The optional parameter can be instance of ConfigSyncConfig class
        to synchronize core actions with actual configuration (and file list as it's
        a part of configuration itself).
        
        :param _config: ConfigSyncConfig instance to synchronize core actions with configuration
        :type _config: ConfigSyncConfig instance
        """
        self.config = _config

    def createWorkingDirectory(self, _path):
        """
        Create git working directory. In this directory the ConfigSync synchronization git
        instance is proceed.
        
        :param _path: Path to the working directory
        :type _path: string
        :return: True if working directory created successfully
        :rtype: bool
        """
        try:
            if os.path.isdir(_path):
                shutil.rmtree(_path)
            os.mkdir(_path)
            return True
        except:
            return False

    def gitClone(self, _repo, _path):
        """
        Clone given repository into the given working directory. This method is proceed
        only once after configuration of ConfigSync is set.
        
        TODO: The command output should be checked. An error or password or encryption
        information could be required. The check should be added.
        
        TODO: The address should be parsed and checked if this is correct git address.
        
        FIXME: The executed command should use native module instead of calling system
        dependent program.
        
        :param _repo: Link to the git repository
        :type _repo: string
        :param _path: Path to the working directory
        :type _path: string
        :return: True if clone command passed without any error
        :rtype: bool
        """
        cmd = ['git', 'clone', _repo, _path]
        p = subprocess.Popen(cmd)
        p.wait()
        return True

    def gitAddFilelist(self):
        """
        Add a file list to local branch. This is called after every file change.
        
        TODO: The command output should be checked. An error or password or encryption
        information could be required. The check should be added.
        
        FIXME: The executed command should use native module instead of calling system
        dependent program.
        """
        _path = self.config.data.path
        _file = self.config.filesFile
        print("DBG: 'git add",_file,"'")
        cmd = ['git', 'add', _file]
        p = subprocess.Popen(cmd, cwd = _path)
        p.wait()

    def gitAdd(self, _file):
        """
        Add given file to local branch. This is called after every file change.
        
        TODO: The command output should be checked. An error or password or encryption
        information could be required. The check should be added.
        
        FIXME: The executed command should use native module instead of calling system
        dependent program.
        
        :param _file: File basename in working directory
        :type _file: string
        """
        print("DBG: 'git add", _file, "'")
        _path = self.config.data.path
        cmd = ['git', 'add', _file]
        p = subprocess.Popen(cmd, cwd = _path)
        p.wait()

    def gitRemove(self, _file):
        """
        Remove a file from local branch. This is called after every file remove.
        
        TODO: The command output should be checked. An error or password or encryption
        information could be required. The check should be added.
        
        FIXME: The executed command should use native module instead of calling system
        dependent program.
        
        :param _file: File basename in working directory
        :type _file: string
        """
        print("DBG: 'git rm", _file, "'")
        _path = self.config.data.path
        cmd = ['git', 'rm', _file]
        p = subprocess.Popen(cmd, cwd = _path)
        p.wait()

    def gitPull(self):
        """
        Git pull command.
        
        TODO: The command output should be checked. An error or password or encryption
        information could be required. The check should be added.
        
        FIXME: The command execution is quite time consuming. It should be done on
        background.
        
        FIXME: The executed command should use native module instead of calling system
        dependent program.
        """
        print("DBG: 'git pull'")
        _path = self.config.data.path
        cmd = ['git', 'pull']
        p = subprocess.Popen(cmd, cwd = _path)
        p.wait()

    def gitPush(self):
        """
        Git push command.
        
        TODO: The command output should be checked. An error or password or encryption
        information could be required. The check should be added.
        
        FIXME: The command execution is quite time consuming. It should be done on
        background.
        
        FIXME: The executed command should use native module instead of calling system
        dependent program.
        """
        print("DBG: 'git push -u origin master'")
        _path = self.config.data.path
        cmd = ['git', 'push', '-u', 'origin', 'master']
        p = subprocess.Popen(cmd, cwd = _path)
        p.wait()

    def gitCommit(self):
        """
        Git commit command. The commit message contains machine name and time stamp.
        
        TODO: The command output should be checked. An error or password or encryption
        information could be required. The check should be added.
        
        FIXME: The command execution is quite time consuming. It should be done on
        background.
        
        FIXME: The executed command should use native module instead of calling system
        dependent program.
        """
        _path = self.config.data.path
        _msg = "\"" + self.config.data.name + "-" + time.strftime("%Y-%m-%d(%H:%M:%S)") + "\""
        print("DBG: 'git commit -m", _msg,"'")
        cmd = ['git', 'commit', '-m', _msg]
        p = subprocess.Popen(cmd, cwd = _path)
        p.wait()

    def linkFile(self, _f, _s):
        """
        Make a hardlink to the file to synchronize to ConfigSync working
        directory to begin file tracking.
        
        FIXME: The executed command should use native module instead of calling system
        dependent program.
        
        :param _f: Path to the original file what should be synchronized
        :type _f: string
        :param _s: Path to the file in ConfigSync working directory
        :type _s: string
        """
        print("DBG: 'ln -f", _f, _s,"'")
        cmd = ['ln', '-f', _f, _s]
        p = subprocess.Popen(cmd)
        p.wait()

    def unlinkFile(self, _file):
        """
        Split a hardlink connection between two files to make them independent. This
        method is called when file should not be synchronized any longer.
        
        FIXME: The executed command should use native module instead of calling system
        dependent program.
        
        :param _file: Path to the file in ConfigSync working directory
        :type _file: string
        """
        print("DBG: unlink file")
        cmd = ['mv', _file, "/tmp/tmpname"]
        p = subprocess.Popen(cmd)
        p.wait()

        cmd = ['cp', '/tmp/tmpname', _file]
        p = subprocess.Popen(cmd)
        p.wait()

        cmd = ['rm', '/tmp/tmpname']
        p = subprocess.Popen(cmd)
        p.wait()

    def synchronize(self):
        """
        Do the synchronization itself.
        
        TODO: The command output should be checked. An error or password or encryption
        information could be required. The check should be added.
        
        FIXME: The command execution is quite time consuming. It should be done on
        background.
        """
        self.gitCommit()
        self.gitPush()
