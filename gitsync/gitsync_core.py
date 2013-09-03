#!/usr/bin/python3
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
File info:      This file contains the core of GitSync synchronization. It
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

from gitsync_config import GitSyncConfig
import os
import subprocess
import shutil

class GitSyncCore:
    """
    GitSync synchronize core
    """
    def __init__(self, _config):
        self.config = _config


    #def initialize(self):#FIXME deprecated
    #   """First time configured GitSync has to be initialized"""
    #    #self.config.restoreConfiguration()
    #    if not os.path.isdir(self.config.data.path):
    #        os.mkdir(self.config.data.path)
    #    else:
    #        if os.path.isdir(self.config.data.path + '.git'):
    #            shutil.rmtree(self.config.data.path + '.git')
    #
    #        self.gitClone()
    #        #TODO update file list from the remote files

    #    self.config.data.synced = True
    #    self.config.storeConfiguration()

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

    #def gitClone(self): #OBSOLETE
    #    """
    #    Clone given repo into the directory
    #    """
    #    link = self.config.data.repo
    #    path = self.config.data.path
    #    cmd = ['git', 'clone', link, path]
    #    p = subprocess.Popen(cmd)
    #    p.wait()

    def gitClone(self, _path, _repo):
        """
        Clone given repo into the directory
        """
        cmd = ['git', 'clone', _repo, _path]
        #p = subprocess.Popen(cmd)
        #p.wait()
        #TODO add git call and parse output
        output = True #FIXME hack!
        if output:
            return True
        else:
            return False

    def gitAddFilelist(self,f):
        """
        Add a file list to local branch. Execute: git add
        """
        _path = self.config.data.path
        _file = self.config.filesFile
        cmd = ['git', 'add', _file] #FIXME substitute with python native call
        #p = subprocess.Popen(cmd, pwd = _path)
        #p.wait()
        #FIXME the output should be parsed and checked for errors

    def gitAdd(self,f):
        """
        Add a file to local branch. Execute: git add
        """
        _path = self.config.data.path
        cmd = ['git', 'add', f] #FIXME substitute with python native call
        #p = subprocess.Popen(cmd, pwd = _path)
        #p.wait()
        #FIXME the output should be parsed and checked for errors

    def gitRemove(self,f):
        """
        Remove a file. Execute: git remove
        """
        _path = self.config.data.path
        cmd = ['git', 'remove', f] #FIXME substitute with python native call
        #p = subprocess.Popen(cmd, pwd = _path)
        #p.wait()
        #FIXME the output should be parsed and checked for errors

    def gitPull(self):
        """
        Git pull command
        """
        _path = self.config.data.path
        cmd = ['git', 'pull'] #FIXME substitute with python native call
        #p = subprocess.Popen(cmd, pwd = _path)
        #p.wait()
        #FIXME the output should be parsed and checked for errors

    def gitPush(self):
        """Git push command"""
        _path = self.config.data.path
        cmd = ['git', 'push', '-u', 'origin', 'master'] #TODO is this correct?
        #p = subprocess.Popen(cmd, pwd = _path)
        #p.wait()
        #FIXME the output should be parsed and checked for errors

    def linkFile(self, f):
        """
        Make a hardlink to the file to synchronize to gitsync working
        directory to begin synchronization
        """
        target = self.config.data.path +"/"+ os.path.basename(f)
        cmd = ['ln', f, target] #FIXME substitute with python native call
        p = subprocess.Popen(cmd)
        p.wait()

    def unlinkFile(self, f):
        """
        Split a hardlink connection between two files to make them independent
        """
        target = self.config.data.path +"/"+ os.path.basename(f)
        cmd = ['mv', target, "/tmp/tmpname"] #FIXME substitute with python native call
        p = subprocess.Popen(cmd)
        p.wait()

        cmd = ['cp', '/tmp/tmpname', target] #FIXME substitute with python native call
        p = subprocess.Popen(cmd)
        p.wait()

        cmd = ['rm', '/tmp/tmpname'] #FIXME substitute with python native call
        p = subprocess.Popen(cmd)
        p.wait()

    def synchronize(self):
        """Do the synchronization itself."""
        #TODO synchronize only existing files on both systems
        #TODO synchronize only changed files
        #TODO handle copying
        pass

    def daemonize(self):
        """Transform to a daemon. Note: FutureFeature"""
        #TODO
        pass


