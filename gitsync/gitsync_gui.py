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
File info:      This file describes the graphical interface and all the signal
                bindings connected to that. This is not executable file!

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

from gi.repository import Gtk, GObject
from gitsync_config import GitSyncConfig
from gitsync_core import GitSyncCore
import os

class GitSyncGui:
    def __init__(self):
        """
        Contructor
        """
        self.gladefile = 'gitsync.ui'

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.gladefile)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object('mainWindow')
        self.wizard = self.builder.get_object('wizardWindow')
        self.machineNameEntry = self.builder.get_object('machineNameEntry')
        self.synchronizationPathEntry = self.builder.get_object('synchronizationPathEntry')
        self.repoLinkEntry = self.builder.get_object('repoLinkEntry')
        self.filesTreeview = self.builder.get_object('filesTreeview')
        self.statusBar = self.builder.get_object('statusBar')
        self.progressBar = self.builder.get_object('progressBar')

        self.config = GitSyncConfig()
        self.core = GitSyncCore(self.config)

        if not self.config.data.synced:
            """Not yet initialized"""
            self.show_wizard()
        else:
            self.show_main_window()

    def show_main_window(self):
        self.initFields()

        cell = Gtk.CellRendererText()
        if len(self.filesTreeview.get_columns()) == 0:
            column1 = Gtk.TreeViewColumn("Remote file", cell, text=0)
            column1.set_clickable(True)   
            column1.set_resizable(True)
            column2 = Gtk.TreeViewColumn("Synchronized with", cell, text=1)
            column2.set_clickable(True)   
            column2.set_resizable(True)
            column3 = Gtk.TreeViewColumn("Origin", cell, text=2)
            column3.set_clickable(True)   
            column3.set_resizable(True)
            self.filesTreeview.append_column(column1)
            self.filesTreeview.append_column(column2)
            self.filesTreeview.append_column(column3)
            self.filesTreeview.expand_all()

        self.window.show()

    def show_wizard(self):
        ntb = self.builder.get_object('wizardNotebook')
        ntb.set_current_page(0)
        home = os.path.expanduser("~")
        self.builder.get_object("directoryEntry").set_text(home + "/.gitsync")
        self.wizard.show()

    def on_wizard_confirm_clicked(self, object, data=None):
        directory = self.builder.get_object('directorySummary').get_text()
        repository = self.builder.get_object('repoSummary').get_text()
        valid = True # set to False if any check fails
        #TODO check if the given address is address to repo
        #TODO check if user have correct permissions to the repo

        if valid and not self.core.createWorkingDirectory(directory):
            print('DBG: Unable to create working directory!')
            #TODO add visible warning and return to the appropriate wizard page

        if valid and not self.core.gitClone(repository, directory):
            print('DBG: Unable to clone repository!')
            #TODO add visible warning and possible more options (key, password, etc.)

        if valid:
            self.config.data.name = self.builder.get_object('nameSummary').get_text()
            self.config.data.repo = repository
            self.config.data.path = directory
            self.config.storeConfiguration()

            self.config.restoreFileList()

        else:
            print('DBG: Any error occured before, configuration hasn\'t been stored')
            #TODO add visible warning

        self.wizard.hide()
        self.show_main_window()

    def on_wizard_next_clicked(self, object, data=None):
        ntb = self.builder.get_object('wizardNotebook')
        ntb.next_page()

    def on_wizardNotebook_switch_page(self, object, data=None, tab=None):
        if tab == 4:
            self.refresh_summary_forms()

    def refresh_summary_forms(self):
        print('DBG: Refresh summary forms')
        self.builder.get_object('nameSummary').set_text(self.builder.get_object('nameEntry').get_text())
        self.builder.get_object('directorySummary').set_text(self.builder.get_object('directoryEntry').get_text())
        self.builder.get_object('repoSummary').set_text(self.builder.get_object('repoEntry').get_text())

    def on_wizard_back_clicked(self, object, data=None):
        ntb = self.builder.get_object('wizardNotebook')
        ntb.prev_page()

    def on_wizard_cancel_clicked(self, object, data=None):
        Gtk.main_quit()

    def on_mainWindow_delete(self, object, data=None):
        Gtk.main_quit()

    def on_addFileButton_clicked(self, object, data=None):
        print("addFileButton clicked")

        dialog = self.builder.get_object('fileChooseDialog')
        response = dialog.run()
        big = False
        if response == 1:
            f = dialog.get_filename()
            if not self.checkFileSize(f):
                dialog.hide()
                self.notifyWeak('The file is too big!')
                return

            self.config.data.addFile(f,f)
            self.config.files.addFile(f, self.config.data.name)
            s = self.config.data.path +"/"+ os.path.basename(f)
            self.core.linkFile(f, s)
            self.config.storeFileList()
            self.config.storeConfiguration()
            #TODO Git add na file list
            self.core.gitAdd(f)

            #TODO git commit and git push?

            self.updateFileList()
        dialog.hide()

    def on_removeFileButton_clicked(self, object, data=None):
        print("DBG: removeFileButton clicked")
        model, treeiter = self.filesTreeview.get_selection().get_selected()
        if treeiter == None:
            self.notifyStrong('You haven\'t selected any file to remove!')
            return
        
        f = model[treeiter][0]
        s = model[treeiter][1]
        
        if not self.config.data.existsFile(f):
            self.notifyStrong('The selected file is not synced!')
            return

        dialog = self.builder.get_object('questionRemoveFileDialog')
        
        self.builder.get_object('fileLabel').set_text(f)
        response = dialog.run()

        if response == 1:
            self.config.data.delFile(f)
            syncedFile = self.config.data.path + "/" + os.path.basename(f)
            self.core.unlinkFile(syncedFile)
            if self.config.files.delFileLink(f):
                self.core.gitRemove(f)
                self.config.files.delFile(f)
            self.config.storeConfiguration()
            self.config.storeFileList()

            self.updateFileList()

        dialog.hide()

    def on_linkFileButton_clicked(self, object, data=None):
        print("DBG: linkFileButton clicked")
        model, treeiter = self.filesTreeview.get_selection().get_selected()
        if treeiter == None:
            self.notifyStrong('You haven\'t selected any file to link!')
            return
        dialog = self.builder.get_object('fileChooseDialog')
        response = dialog.run()
        big = False
        if response == 1:
            s = dialog.get_filename()
            f = model[treeiter][0]
            self.config.data.addFile(f,s)
            self.core.linkFile(f, s)
            self.config.files.addFileLink(f)

            self.config.storeConfiguration()
            self.config.storeFileList()

            self.updateFileList()

        dialog.hide()

    def on_syncButton_clicked(self, object, data=None):
        print("DBG: syncButton clicked")
        self.core.synchronize()
        #TODO handle the progress bar

    def on_resetButton_clicked(self, object, data=None):
        print("DBG: resetButton clicked")
        self.config.data.synced = False
        self.config.data.files.clear()
        self.window.hide()
        self.show_wizard()

    def initFields(self):
        """
        Initialize fields in GUI widget
        """
        self.machineNameEntry.set_text(self.config.data.name)
        self.synchronizationPathEntry.set_text(self.config.data.path)
        self.repoLinkEntry.set_text(self.config.data.repo)

        self.updateFileList()

    def updateFileList(self):
        self.filesListstore = Gtk.ListStore(str,str,str)
        self.filesListstore.clear()
        if len(self.config.files.files) > 0:
            lst = sorted(self.config.files.files)
            for f in lst:
                l = "Not linked"
                o = self.config.files.files[f][0]
                print("\tFile: ",f,", Linked: ",l,", Origin",o)
                if self.config.data.existsFile(f):
                    l = self.config.data.getValue(f)
                self.filesListstore.append([f,l,o])

        self.filesTreeview.set_model(self.filesListstore)
        self.filesTreeview.expand_all()

    def checkFileSize(self,f):
        if os.path.getsize(f) > 1048576: # 1MB is the limit
            return False
        else:
            return True

    def notifyStrong(self, text):
        dialog = self.builder.get_object('notifyStrongDialog')
        self.builder.get_object('notifyStrongLabel').set_text(text)
        dialog.run()
        dialog.hide()


    def notifyWeak(self, text):
        msgId = self.statusBar.push(1, text)
        GObject.timeout_add(4000, self.statusBar.remove,1,msgId)
