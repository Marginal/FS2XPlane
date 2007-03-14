#!/usr/bin/python

#
# Copyright (c) 2005 Jonathan Harris
# 
# Mail: <x-plane@marginal.org.uk>
# Web:  http://marginal.org.uk/x-planescenery/
#
# See FS2XPlane.html for usage.
#
# This software is licensed under a Creative Commons License
#   Attribution-ShareAlike 2.5:
#
#   You are free:
#     * to copy, distribute, display, and perform the work
#     * to make derivative works
#     * to make commercial use of the work
#   Under the following conditions:
#     * Attribution: You must give the original author credit.
#     * Share Alike: If you alter, transform, or build upon this work, you
#       may distribute the resulting work only under a license identical to
#       this one.
#   For any reuse or distribution, you must make clear to others the license
#   terms of this work.
#
# This is a human-readable summary of the Legal Code (the full license):
#   http://creativecommons.org/licenses/by-sa/2.5/legalcode
#

import os	# for startfile
from os import chdir, listdir, mkdir
from os.path import abspath, basename, curdir, dirname, exists, isdir, join, sep
from sys import argv, exit, platform
from traceback import print_exc
import wx

from convmain import Output
from convutil import FS2XError

appname='FS2XPlane'
app=wx.PySimpleApp()

mypath=dirname(abspath(argv[0]))
if not isdir(mypath):
    wx.MessageDialog(None, '"%s" is not a folder' % mypath,
                     appname, wx.ICON_ERROR|wx.CANCEL).ShowModal()
    exit(1)
chdir(mypath)

fspath=''
lbpath=''
xppath=''
FSBROWSE=wx.NewId()
LBBROWSE=wx.NewId()
XPBROWSE=wx.NewId()


# callbacks
def status(percent, msg):
    if percent<0:
        # New dialog
        if frame.progress: frame.progress.Destroy()
        frame.progress = wx.ProgressDialog(msg, '', 100, frame,
                                           wx.PD_APP_MODAL|wx.PD_CAN_ABORT|wx.PD_SMOOTH)
    else:
        if not frame.progress.Update(percent, msg):
            raise FS2XError('Stopped')

def log(msg):
    if not isdir(dirname(frame.logname)):
        mkdir(dirname(frame.logname))
    logfile=file(frame.logname, 'at')
    logfile.write('%s\n' % msg)
    logfile.close()
    

if platform=='win32':
    from _winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER
    if isdir('C:\\X-Plane\\Custom Scenery'):
        xppath='C:\\X-Plane\\Custom Scenery'
    for key in [HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER]:
        try:
            handle=OpenKey(key, 'SOFTWARE\\Microsoft\\Microsoft Games\\Flight Simulator\\9.0\\')
            (v,t)=QueryValueEx(handle, 'EXE Path')
            if t==1 and isdir(v):
                v=v+'\\Addon Scenery'	# Don't think this is localised?
                fspath=v+'\\'+listdir(v)[0]
                lbpath=v
                break
        except:
            pass


class MainWindow(wx.Frame):
    def __init__(self,parent,id, title):
        
        self.progress = None	# Current progress dialog (or None)
        self.logname = None
        
        wx.Frame.__init__(self,parent,id,title)

        panel0 = wx.Panel(self,-1)
        panel1 = wx.Panel(panel0,-1)
        panel2 = wx.Panel(panel0,-1)
        panel3 = wx.Panel(panel0,-1)

        # 1st panel
        self.fspath=wx.TextCtrl(panel1, -1, fspath)
        self.lbpath=wx.TextCtrl(panel1, -1, lbpath)
        self.xppath=wx.TextCtrl(panel1, -1, xppath)
        self.fsbrowse=wx.Button(panel1, FSBROWSE, "Browse...")
        self.lbbrowse=wx.Button(panel1, LBBROWSE, "Browse...")
        self.xpbrowse=wx.Button(panel1, XPBROWSE, "Browse...")
        grid1 = wx.FlexGridSizer(2, 3, 7, 7)
        grid1.AddGrowableCol(1,proportion=1)
        grid1.SetFlexibleDirection(wx.HORIZONTAL)
        grid1.Add(wx.StaticText(panel1, -1, "MSFS scenery location:"
                                ), 0, wx.ALIGN_CENTER_VERTICAL)
        grid1.Add(self.fspath,     1, wx.EXPAND)
        grid1.Add(self.fsbrowse,   0, wx.ALIGN_CENTER_VERTICAL)
        grid1.Add(wx.StaticText(panel1, -1, "Additional MSFS libraries:"
                                ), 0, wx.ALIGN_CENTER_VERTICAL)
        grid1.Add(self.lbpath,     1, wx.EXPAND)
        grid1.Add(self.lbbrowse,   0, wx.ALIGN_CENTER_VERTICAL)
        grid1.Add(wx.StaticText(panel1, -1, "X-Plane scenery location:"
                                ), 0, wx.ALIGN_CENTER_VERTICAL)
        grid1.Add(self.xppath,     1, wx.EXPAND)
        grid1.Add(self.xpbrowse,   0, wx.ALIGN_CENTER_VERTICAL)
        panel1.SetSizer(grid1)

        wx.EVT_BUTTON(self, FSBROWSE, self.onFSbrowse)
        wx.EVT_BUTTON(self, LBBROWSE, self.onLBbrowse)
        wx.EVT_BUTTON(self, XPBROWSE, self.onXPbrowse)

        # 2nd panel
        self.season = wx.RadioBox(panel2,-1, "Season:",
                                  choices=["Spring", "Summer",
                                           "Autumn", "Winter"])
        # use panel and sizer so tab order works normally
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box2.Add(self.season, 1)
        panel2.SetSizer(box2)

        # 3rd panel
        if 'startfile' in dir(os):
            button31=wx.Button(panel3, wx.ID_HELP)
        button32=wx.Button(panel3, wx.ID_OK, "Convert")
        button33=wx.Button(panel3, wx.ID_EXIT)
        box3 = wx.BoxSizer(wx.HORIZONTAL)
        if 'startfile' in dir(os):
            box3.Add(button31, 0)
        box3.AddSpacer([0,0], 1)	# push following buttons to right
        box3.Add(button32, 0)
        box3.AddSpacer([6,0], 0)	# cosmetic
        box3.Add(button33, 0)
        button32.SetDefault()
        panel3.SetSizer(box3)

        if 'startfile' in dir(os):
            wx.EVT_BUTTON(self, wx.ID_HELP, self.onHelp)
        wx.EVT_BUTTON(self, wx.ID_OK, self.onConvert)
        wx.EVT_BUTTON(self, wx.ID_EXIT, self.onClose)

        # Top level
        box0 = wx.BoxSizer(wx.VERTICAL)
        box0.Add(panel1, 0, wx.ALL|wx.EXPAND, 7)
        box0.Add(panel2, 0, wx.ALL|wx.EXPAND, 7)
        box0.Add(panel3, 0, wx.ALL|wx.EXPAND, 7)
        panel0.SetSizer(box0)

        border = wx.BoxSizer()
        border.Add(panel0, 1, wx.EXPAND)
        self.SetSizer(border)

        # Go
        sz=self.GetBestSize()
        # +50 is a hack cos I can't work out how to change minsize of TextCtrl
        self.SetSize((sz.width+300, sz.height))
        self.SetSizeHints(sz.width+50, sz.height, -1, sz.height)
        self.Show(True)


    def onFSbrowse(self, evt):
        dlg=wx.DirDialog(self, "Location of MSFS scenery package:",
                         self.fspath.GetValue(), wx.DD_NEW_DIR_BUTTON)
        dlg.ShowModal()
        self.fspath.SetValue(dlg.GetPath())
        dlg.Destroy()

    def onLBbrowse(self, evt):
        dlg=wx.DirDialog(self,"Location of additional MSFS scenery libraries:",
                         self.lbpath.GetValue(), wx.DD_NEW_DIR_BUTTON)
        dlg.ShowModal()
        self.lbpath.SetValue(dlg.GetPath())
        dlg.Destroy()

    def onXPbrowse(self, evt):
        dlg=wx.DirDialog(self, "Location for new X-Plane scenery package:",
                         self.xppath.GetValue(), wx.DD_NEW_DIR_BUTTON)
        dlg.ShowModal()
        self.xppath.SetValue(dlg.GetPath())
        dlg.Destroy()

    def onClose(self, evt):
        self.Close()

    def onHelp(self, evt):
        os.startfile(curdir+sep+appname+'.html')

    def onConvert(self, evt):
        fspath=self.fspath.GetValue().strip()
        if not fspath:
            dlg=wx.MessageDialog(None, 'Must specify a MSFS scenery location',
                                 appname, wx.ICON_ERROR|wx.CANCEL)
            dlg.ShowModal()
            dlg.Destroy()
            return
        fspath=abspath(fspath)
        lbpath=self.lbpath.GetValue().strip()
        if not lbpath:
            lbpath=None
        else:
            lbpath=abspath(lbpath)
        xppath=self.xppath.GetValue().strip()
        if not xppath:
            dlg=wx.MessageDialog(None,
                                 'Must specify an X-Plane scenery location',
                                 appname, wx.ICON_ERROR|wx.CANCEL)
            dlg.ShowModal()
            dlg.Destroy()
            return
        xppath=abspath(xppath)
        self.logname=abspath(join(xppath, 'errors.txt'))
        season=self.season.GetSelection()	# zero-based

        try:
            output=Output(mypath,fspath,lbpath,xppath,season,status,log,
                          False, False)
            output.scanlibs()
            output.process()
            output.proclibs()
            output.export()
            if self.progress:
                self.progress.Destroy()
                self.progress=None
            if exists(self.logname):
                if 'startfile' in dir(os):
                    dlg=wx.MessageDialog(None,
                                         'Done.\nDisplaying error log "%s"' %(
                        self.logname), appname, wx.ICON_INFORMATION|wx.OK)
                    os.startfile(self.logname)
                else:
                    dlg=wx.MessageDialog(None,
                                         'Done.\nErrors found; see log "%s"' %(
                        self.logname), appname, wx.ICON_INFORMATION|wx.OK)
            else:
                dlg=wx.MessageDialog(None, 'Done.',
                                     appname, wx.ICON_INFORMATION|wx.OK)

        except FS2XError, e:
            dlg=wx.MessageDialog(None, e.msg,
                                 appname, wx.ICON_ERROR|wx.CANCEL)

        except:
            if not isdir(dirname(self.logname)):
                mkdir(dirname(self.logname))
            logfile=file(self.logname, 'at')
            logfile.write('\nInternal error\n')
            print_exc(None, logfile)
            logfile.close()
            dlg=wx.MessageDialog(None, 'Internal error.\nPlease report error in log\n"%s"' % self.logname, appname, wx.ICON_EXCLAMATION|wx.CANCEL)
            if 'startfile' in dir(os):
                os.startfile(self.logname)

        dlg.ShowModal()
        dlg.Destroy()
        if self.progress:
            self.progress.Destroy()
            self.progress=None


# main
frame=MainWindow(None,wx.ID_ANY,appname)
if platform=='win32':
    frame.SetIcon(wx.Icon('win32/FS2XPlane.ico', wx.BITMAP_TYPE_ICO))
elif platform.lower().startswith('linux'):	# PNG supported by GTK
    frame.SetIcon(wx.Icon('linux/FS2XPlane.png', wx.BITMAP_TYPE_PNG))
app.SetTopWindow(frame)
app.MainLoop()
