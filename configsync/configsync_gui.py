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
Module describes the graphical interface and all the signal bindings connected to that.
"""

from configsync.configsync_config import ConfigSyncConfig
from configsync.configsync_core import ConfigSyncCore
from pkg_resources import Requirement, resource_filename
from gi.repository import Gtk, GObject
import os

class ConfigSyncGui:
    def __init__(self, wizard = False):
        """
        Constructor of ConfigSyncGui class object
        
        :param wizard: If True, force to start wizard first. Otherwise, the wizard is started only if the configuration is not set.
        :type wizard: bool
        """
        self.guifile = resource_filename(Requirement.parse("configsync"),"configsync/configsync.ui")

        self.builder = Gtk.Builder()
        self.builder.add_from_file(self.guifile)
        self.builder.connect_signals(self)
        self.window = self.builder.get_object('mainWindow')
        self.wizard = self.builder.get_object('wizardWindow')
        self.machineNameEntry = self.builder.get_object('machineNameEntry')
        self.synchronizationPathEntry = self.builder.get_object('synchronizationPathEntry')
        self.repoLinkEntry = self.builder.get_object('repoLinkEntry')
        self.filesTreeview = self.builder.get_object('filesTreeview')
        self.statusBar = self.builder.get_object('statusBar')
        self.progressBar = self.builder.get_object('progressBar')

        self.config = ConfigSyncConfig()
        self.core = ConfigSyncCore(self.config)

        if not self.config.data.synced or wizard:
            """Not yet initialized or wizard choosed"""
            self.show_wizard()
        else:
            self.core.gitPull()
            self.show_main_window()

    def show_main_window(self):
        """
        Initialize GUI fields and lists and show the whole window.
        """
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

    def show_wizard(self, page = 0):
        """
        Show wizard at the first page
        
        :param page: The current page of the wizard
        :type page: int
        """
        ntb = self.builder.get_object('wizardNotebook')
        ntb.set_current_page(page)
        home = os.path.expanduser("~")
        self.builder.get_object("directoryEntry").set_text(home + "/.configsync/syncdir/")
        self.wizard.show()

    def on_wizard_confirm_clicked(self, object, data=None):
        """
        Function called when the wizard is finished. Entered values are checked here and
        warning is shown if any error occurs. If everything passed, the wizard is hidden
        and the main window is shown.
        """
        directory = self.builder.get_object('directorySummary').get_text()
        repository = self.builder.get_object('repoSummary').get_text()

        if not self.core.createWorkingDirectory(directory):
            print('Unable to create working directory! Is the path correct?')
            #TODO add visible warning and return to the appropriate wizard page
            self.wizard.hide()
            self.show_wizard(2)
            return

        if not self.core.gitClone(repository, directory):
            print('Unable to clone repository!')
            #TODO add visible warning and possible more options (key, password, etc.)
            self.wizard.hide()
            self.show_wizard(3)
            return

        self.config.data.name = self.builder.get_object('nameSummary').get_text()
        self.config.data.repo = repository
        self.config.data.path = directory
        self.config.storeConfiguration()

        self.config.restoreFileList()

        self.wizard.hide()
        self.show_main_window()

    def on_wizard_next_clicked(self, object, data=None):
        """
        Handle wizard's 'next button'
        """
        ntb = self.builder.get_object('wizardNotebook')
        ntb.next_page()

    def on_wizardNotebook_switch_page(self, object, data=None, tab=None):
        """
        Watch the wizard page number and if the number is 4 (the last page - summary),
        call the refresh function to refresh fields in the summary.
        """
        if tab == 4:
            self.refresh_summary_forms()

    def refresh_summary_forms(self):
        """
        Refresh values in wizard's summary page.
        """
        self.builder.get_object('nameSummary').set_text(self.builder.get_object('nameEntry').get_text())
        self.builder.get_object('directorySummary').set_text(self.builder.get_object('directoryEntry').get_text())
        self.builder.get_object('repoSummary').set_text(self.builder.get_object('repoEntry').get_text())

    def on_wizard_back_clicked(self, object, data=None):
        """
        Handle wizard's 'back button'
        """
        ntb = self.builder.get_object('wizardNotebook')
        ntb.prev_page()

    def on_wizard_cancel_clicked(self, object, data=None):
        """
        Handle wizard 'cancel button'
        """
        Gtk.main_quit()

    def on_mainWindow_delete(self, object, data=None):
        """
        Handle mainWindow delete widget event
        """
        self.core.synchronize()
        Gtk.main_quit()

    def on_addFileButton_clicked(self, object, data=None):
        """
        Handle event by button 'Add file'. It shows 'choose file' dialog, checks if
        selected file is correct and if so, adds it to the remote repo and stores the
        configurations as well as the file list. At the end the dialog is hidden.
        """
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

            self.core.gitAdd(s)
            self.core.gitAddFilelist()
            self.core.gitCommit()

            self.updateFileList()
        dialog.hide()

    def on_removeFileButton_clicked(self, object, data=None):
        """
        Handle event by button 'Unlink file'. It shows the question dialog asking the user
        if he is sure and if so, the file is unlinked from the tracking. If no other
        machine is tracking the file any more, it's also removed from the remote repo.
        Before the actual deleting are two actions states - to select any file and to
        have the file linked. If these two states are not met, warning is shown.
        """
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
                self.core.gitRemove(syncedFile)
                self.config.files.delFile(f)

            self.config.storeFileList()
            self.core.gitAddFilelist()
            self.core.gitCommit()
            self.config.storeConfiguration()

            self.updateFileList()

        dialog.hide()

    def on_linkFileButton_clicked(self, object, data=None):
        """
        Handle event by button 'Link file'.
        """
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
            self.config.storeFileList()
            self.core.gitAddFilelist()
            self.core.gitCommit()

            self.config.storeConfiguration()

            self.updateFileList()

        dialog.hide()

    def on_syncButton_clicked(self, object, data=None):
        """
        Evoke synchronization immediately. It connected to 'Synchronize now' button.
        """
        self.core.synchronize()

    def on_resetButton_clicked(self, object, data=None):
        """
        Invalidate the configuration status and show the wizard to apply new configuration.
        """
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
        """
        Fill the fileList in the GUI widget with file entries if there're any. Also check
        if the shown entries are actually linked with something locally.
        """
        self.filesListstore = Gtk.ListStore(str,str,str)
        self.filesListstore.clear()
        if len(self.config.files.files) > 0:
            lst = sorted(self.config.files.files)
            for f in lst:
                l = "Not linked"
                o = self.config.files.files[f][0]
                if self.config.data.existsFile(f):
                    l = self.config.data.getValue(f)
                self.filesListstore.append([f,l,o])

        self.filesTreeview.set_model(self.filesListstore)
        self.filesTreeview.expand_all()

    def checkFileSize(self, f):
        """
        Simple function to check file size. Maximal valid file size is 1MB.
        
        :param f: Name of the file (path)
        :type f: string
        :return: True if the file is bigger than the limit
        :rtype: bool
        """
        if os.path.getsize(f) > 1048576: # 1MB is the limit
            return False
        else:
            return True

    def notifyStrong(self, text):
        """
        Evoke warning popup dialog with custom text.
        
        :param text: The cumstom text of a warning
        :type text: string
        """
        dialog = self.builder.get_object('notifyStrongDialog')
        self.builder.get_object('notifyStrongLabel').set_text(text)
        dialog.run()
        dialog.hide()


    def notifyWeak(self, text):
        """
        Flush a custom warning text into status bar.
        
        :param text: The cumstom text of a warning
        :type text: string
        """
        msgId = self.statusBar.push(1, text)
        GObject.timeout_add(4000, self.statusBar.remove,1,msgId)
