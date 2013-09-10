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
File info:      This file contains the core of ConfigSync synchronization. It
                contains all the real functionality.

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

from configsync_config import ConfigSyncConfig
import os
import subprocess
import shutil
import time

class ConfigSyncCore:
    """
    ConfigSync synchronize core
    """
    def __init__(self, _config):
        self.config = _config


    def createWorkingDirectory(self, _path):
        """
        Creates working directory or returns False
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
        Clone given repo into the directory
        """
        cmd = ['git', 'clone', _repo, _path] #FIXME substitute with python native call and parse output
        p = subprocess.Popen(cmd)
        p.wait()
        #TODO add git call and parse output
        output = True #FIXME hack!
        if output:
            return True
        else:
            return False

    def gitAddFilelist(self):
        """
        Add a file list to local branch. Execute: git add
        """
        _path = self.config.data.path
        _file = self.config.filesFile
        print("DBG: 'git add",_file,"'")
        cmd = ['git', 'add', _file] #FIXME substitute with python native call
        p = subprocess.Popen(cmd, cwd = _path)
        p.wait()
        #FIXME the output should be parsed and checked for errors

    def gitAdd(self,f):
        """
        Add a file to local branch. Execute: git add
        """
        print("DBG: 'git add",f,"'")
        _path = self.config.data.path
        cmd = ['git', 'add', f] #FIXME substitute with python native call
        p = subprocess.Popen(cmd, cwd = _path)
        p.wait()
        #FIXME the output should be parsed and checked for errors

    def gitRemove(self,f):
        """
        Remove a file. Execute: git remove
        """
        print("DBG: 'git rm",f,"'")
        _path = self.config.data.path
        cmd = ['git', 'rm', f] #FIXME substitute with python native call
        p = subprocess.Popen(cmd, cwd = _path)
        p.wait()
        #FIXME the output should be parsed and checked for errors

    def gitPull(self):
        """
        Git pull command
        """
        #TODO do the synchronization on background
        print("DBG: 'git pull'")
        _path = self.config.data.path
        cmd = ['git', 'pull'] #FIXME substitute with python native call
        p = subprocess.Popen(cmd, cwd = _path)
        p.wait()
        #FIXME the output should be parsed and checked for errors

    def gitPush(self):
        """
        Git push command
        """
        #TODO do the synchronization on background
        print("DBG: 'git push -u origin master'")
        _path = self.config.data.path
        cmd = ['git', 'push', '-u', 'origin', 'master'] #TODO is this correct?
        p = subprocess.Popen(cmd, cwd = _path)
        p.wait()
        #FIXME the output should be parsed and checked for errors

    def gitCommit(self):
        """
        Git commit command
        """
        _path = self.config.data.path
        _msg = "\"" + self.config.data.name + time.strftime("%Y-%m-%d(%H:%M:%S)") + "\""
        print("DBG: 'git commit -m", _msg,"'")
        cmd = ['git', 'commit', '-m', _msg]
        p = subprocess.Popen(cmd, cwd = _path) #FIXME substitute with python native call
        p.wait()
        #FIXME the output should be parsed and checked for errors

    def linkFile(self, f, s):
        """
        Make a hardlink to the file to synchronize to configsync working
        directory to begin synchronization
        """
        print("DBG: 'ln -f", f, s,"'")
        cmd = ['ln', '-f', f, s] #FIXME substitute with python native call
        p = subprocess.Popen(cmd)
        p.wait()

    def unlinkFile(self, remoteFile):
        """
        Split a hardlink connection between two files to make them independent
        """
        print("DBG: unlink file")
        #target = self.config.data.path +"/"+ os.path.basename(f)
        cmd = ['mv', remoteFile, "/tmp/tmpname"] #FIXME substitute with python native call
        p = subprocess.Popen(cmd)
        p.wait()

        cmd = ['cp', '/tmp/tmpname', remoteFile] #FIXME substitute with python native call
        p = subprocess.Popen(cmd)
        p.wait()

        cmd = ['rm', '/tmp/tmpname'] #FIXME substitute with python native call
        p = subprocess.Popen(cmd)
        p.wait()

    def synchronize(self):
        """
        Do the synchronization itself.
        """
        #TODO do the synchronization on background
        self.gitCommit()
        self.gitPush()
