#!/usr/bin/pythonw

#
# Copyright (c) 2006 Jonathan Harris
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
from os import chdir, getenv, listdir, mkdir
from os.path import abspath, basename, curdir, dirname, expanduser, exists, isdir, join, normpath, pardir, sep
from sys import argv, exit, platform
from traceback import print_exc
import wx

from convmain import Output
from convutil import FS2XError, viewer


if platform=='darwin':
    # Hack: wxMac 2.5 requires the following to get shadows to look OK:
    # ... wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM, 2)
    pad=2
    browse="Choose..."
else:
    pad=0
    browse="Browse..."


appname='FS2XPlane'
app=wx.PySimpleApp()


mypath=dirname(abspath(argv[0]))
if not isdir(mypath):
    myMessageBox('"%s" is not a folder' % mypath,
                  appname, wx.ICON_ERROR|wx.CANCEL)
    exit(1)
if basename(mypath)=='MacOS':
    chdir(normpath(join(mypath,pardir)))	# Starts in MacOS folder
else:
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
        if frame.progress:
            frame.progress.SetTitle(msg)
            if not frame.progress.Update(0, ''):
                raise FS2XError('Stopped')
        else:
            frame.progress = wx.ProgressDialog(msg, '', 100, frame,
                                               wx.PD_APP_MODAL|wx.PD_CAN_ABORT)
            if platform=='darwin':	# Too narrow on MacOS
                (x,y)=frame.progress.GetClientSize()
                frame.progress.SetClientSize((x+x,y))
                frame.progress.CenterOnParent()
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
    from _winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, REG_SZ, REG_EXPAND_SZ
    if isdir('C:\\X-Plane\\Custom Scenery'):
        xppath='C:\\X-Plane\\Custom Scenery'
    for key in [HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER]:
        try:
            handle=OpenKey(key, 'SOFTWARE\\Microsoft\\Microsoft Games\\Flight Simulator\\9.0\\')
            (v,t)=QueryValueEx(handle, 'EXE Path')
            handle.Close()
            if t==REG_EXPAND_SZ:
                dirs=v.split('\\')
                for i in range(len(dirs)):
                    if dirs[i][0]==dirs[i][-1]=='%':
                        dirs[i]=getenv(dirs[i][1:-1],dirs[i])
                v='\\'.join(dirs)
            if t in [REG_SZ,REG_EXPAND_SZ] and isdir(v):
                v=v+'\\Addon Scenery'	# Don't think this is localised?
                fspath=v+'\\'+listdir(v)[0]
                lbpath=v+'\\Scenery'
                break
        except:
            pass
    else:
        try:
            v="C:\\Program Files\\Microsoft Games\\Flight Simulator 9\\Addon Scenery"
            fspath=v+'\\'+listdir(v)[0]
            if exists(v+'\\Scenery'): lbpath=v+'\\Scenery'
        except:
            pass
        if 0:	# Don't do this - not very helpful
            handle=OpenKey(HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders\\')
            (v,t)=QueryValueEx(handle, 'Personal')
            handle.Close()
            if t==REG_EXPAND_SZ:
                dirs=v.split('\\')
                for i in range(len(dirs)):
                    if dirs[i][0]==dirs[i][-1]=='%':
                        dirs[i]=getenv(dirs[i][1:-1],dirs[i])
                v='\\'.join(dirs)
            if t in [REG_SZ,REG_EXPAND_SZ] and isdir(v):
                fspath=v
        #except:
        #    pass
elif 0:	# Don't do this - more confusing than helpful
    home=expanduser('~')
    if home:
        if isdir(join(home, 'Desktop')):
            fspath=join(home, 'Desktop')
        else:
            fspath=home
        if isdir(join(fspath, 'X-Plane', 'Custom Scenery')):
            xppath=join(fspath, 'X-Plane', 'Custom Scenery')


class MainWindow(wx.Frame):
    def __init__(self, parent, id, title):

        self.progress = None	# Current progress dialog (or None)
        self.logname = None
        
        wx.Frame.__init__(self,parent,id,title)

        panel0 = wx.Panel(self,-1)
        panel1 = wx.Panel(panel0,-1)
        panel2 = wx.Panel(panel0,-1)
        panel3 = wx.Panel(panel0,-1)

        # 1st panel
        self.fspath=wx.TextCtrl(panel1, -1, fspath)
        self.fsbrowse=wx.Button(panel1, FSBROWSE, browse)
        self.lbpath=wx.TextCtrl(panel1, -1, lbpath)
        self.lbbrowse=wx.Button(panel1, LBBROWSE, browse)
        self.xppath=wx.TextCtrl(panel1, -1, xppath)
        self.xpbrowse=wx.Button(panel1, XPBROWSE, browse)
        grid1 = wx.FlexGridSizer(2, 3, 7, 7)
        grid1.AddGrowableCol(1,proportion=1)
        grid1.SetFlexibleDirection(wx.HORIZONTAL)
        grid1.Add(wx.StaticText(panel1, -1, "MSFS scenery location:"), 0,
                  wx.ALIGN_CENTER_VERTICAL)
        grid1.Add(self.fspath,     1,
                  wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, pad)
        grid1.Add(self.fsbrowse,   0,
                  wx.ALIGN_CENTER_VERTICAL|wx.ALL, pad)
        grid1.Add(wx.StaticText(panel1, -1, "Additional MSFS libraries:"), 0,
                  wx.ALIGN_CENTER_VERTICAL)
        grid1.Add(self.lbpath,     1,
                  wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, pad)
        grid1.Add(self.lbbrowse,   0,
                  wx.ALIGN_CENTER_VERTICAL|wx.ALL, pad)
        grid1.Add(wx.StaticText(panel1, -1, "X-Plane scenery location:"), 0,
                  wx.ALIGN_CENTER_VERTICAL)
        grid1.Add(self.xppath,     1,
                  wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, pad)
        grid1.Add(self.xpbrowse,   0,
                  wx.ALIGN_CENTER_VERTICAL|wx.ALL, pad)
        panel1.SetSizer(grid1)

        wx.EVT_BUTTON(self, FSBROWSE, self.onFSbrowse)
        wx.EVT_BUTTON(self, LBBROWSE, self.onLBbrowse)
        wx.EVT_BUTTON(self, XPBROWSE, self.onXPbrowse)

        # 2nd panel
        self.season = wx.RadioBox(panel2,-1, "Season:",
                                  choices=["Spring", "Summer",
                                           "Autumn", "Winter"])
        self.dumplib= wx.CheckBox(panel2,-1, "Extract all library objects")
        # use panel and sizer so tab order works normally
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box2.Add(self.season, 1)
        box2.Add(self.dumplib, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND,10)
        panel2.SetSizer(box2)

        wx.EVT_CHECKBOX(self, self.dumplib.GetId(), self.onDump)

        
        # 3rd panel - adjust order of buttons per Windows or Mac conventions
        if platform=='win32':
            button31=wx.Button(panel3, wx.ID_HELP)
            button32=wx.Button(panel3, wx.ID_OK, "Convert")
            button33=wx.Button(panel3, wx.ID_EXIT)
            box3 = wx.BoxSizer(wx.HORIZONTAL)
            box3.Add(button31, 0, wx.ALL, pad)
            box3.Add([0,0], 1)	# push following buttons to right
            box3.Add(button32, 0, wx.ALL, pad)
            box3.Add([6,0], 0)	# cosmetic
            box3.Add(button33, 0, wx.ALL, pad)
        else:
            button33=wx.Button(panel3, wx.ID_EXIT)
            button32=wx.Button(panel3, wx.ID_OK, "Convert")
            button31=wx.Button(panel3, wx.ID_HELP)
            box3 = wx.BoxSizer(wx.HORIZONTAL)
            box3.Add([24,0], 0)	# cosmetic - balance button31
            box3.Add([0,0], 1)	# push following buttons to right
            box3.Add(button33, 0, wx.ALL, pad)
            box3.Add([6,0], 0)	# cosmetic
            box3.Add(button32, 0, wx.ALL, pad)
            box3.Add([0,0], 1)	# push following buttons to right
            box3.Add(button31, 0, wx.ALL, pad)
        button32.SetDefault()
        panel3.SetSizer(box3)
        
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
        if wx.VERSION<(2,6):
            # Hack - Can't get min size to work properly in 2.5
            height=sz.height+42
        else:
            height=sz.height            
        self.SetSize((sz.width+400, height))
        # +50 is a hack cos I can't work out how to change minsize of TextCtrl
        self.SetSizeHints(sz.width+50, height, -1, height)
        self.Show(True)

    def onDump(self, evt):
        if self.dumplib.GetValue():
            self.fspath.Disable()
            self.fsbrowse.Disable()
        else:
            self.fspath.Enable()
            self.fsbrowse.Enable()

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
        if platform=='darwin':
            viewer(join(curdir,'Resources',appname+'.html'))
        else:
            viewer(join(curdir,appname+'.html'))

    def onConvert(self, evt):
        dumplib=self.dumplib.GetValue()
        fspath=self.fspath.GetValue().strip()
        lbpath=self.lbpath.GetValue().strip()
        xppath=self.xppath.GetValue().strip()
        if not xppath:
            myMessageBox('You must specify an X-Plane scenery location',
                         appname, wx.ICON_ERROR|wx.CANCEL, self)
            return
        xppath=abspath(xppath)

        if not dumplib:
            if not fspath:
                myMessageBox('You must specify a MSFS scenery location',
                             appname, wx.ICON_ERROR|wx.CANCEL, self)
                return
            fspath=abspath(fspath)
            if not lbpath:
                lbpath=None
            else:
                lbpath=abspath(lbpath)
            if basename(xppath).lower()=='custom scenery':
                xppath=join(xppath, basename(fspath))
        else:
            fspath=None
            if not lbpath:
                myMessageBox('You must specify a MSFS library location',
                             appname, wx.ICON_ERROR|wx.CANCEL, self)
                return
            lbpath=abspath(lbpath)
            if basename(xppath).lower()=='custom scenery':
                xppath=join(xppath, basename(lbpath))
            
        self.logname=abspath(join(xppath, 'errors.txt'))
        season=self.season.GetSelection()	# zero-based

        try:
            output=Output(fspath,lbpath,xppath,season,status,log,dumplib,False)
            output.scanlibs()
            output.process()
            output.proclibs()
            output.export()
            if self.progress:
                self.progress.Destroy()
                self.progress=None
            if exists(self.logname):
                viewer(self.logname)
                myMessageBox('Done.\nDisplaying error log "%s"' %(
                    self.logname), appname, wx.ICON_INFORMATION|wx.OK, self)

        except FS2XError, e:
            myMessageBox(e.msg, appname, wx.ICON_ERROR|wx.CANCEL, self)

        except:
            if not isdir(dirname(self.logname)):
                mkdir(dirname(self.logname))
            logfile=file(self.logname, 'at')
            logfile.write('\nInternal error\n')
            print_exc(None, logfile)
            logfile.close()
            viewer(self.logname)
            myMessageBox('Internal error.\nPlease report error in log\n"%s"'%(
                self.logname), appname, wx.ICON_ERROR|wx.CANCEL, self)

        if self.progress:
            self.progress.Destroy()
            self.progress=None


# Custom MessageBox/MessageDialog to replace crappy wxMac icons
def myMessageBox(message, caption, style, parent=None):
    if platform!='darwin':
        wx.MessageBox(message, caption, style, parent)
    else:
        # Spacings from http://developer.apple.com/documentation/UserExperience/Conceptual/OSXHIGuidelines/XHIGLayout/chapter_19_section_2.html

        style=style&255
        assert (style in [wx.OK,wx.CANCEL])	# we ony handle one button
        txtwidth=362
        
        dlg=wx.Dialog(parent)

        panel0 = wx.Panel(dlg)
        panel1 = wx.Panel(panel0)
        panel2 = wx.Panel(panel0)

        bitmap=wx.StaticBitmap(panel1, -1, wx.Bitmap('Resources/FS2XPlane.png',
                                                     wx.BITMAP_TYPE_PNG))
        text=wx.StaticText(panel1, -1)
        font=text.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        text.SetFont(font)
        # Manually word-wrap
        words=message.split(' ')
        message=''
        startofline=0
        for word in words:
            if '\n' in word:
                firstword=word[:word.index('\n')]
            else:
                firstword=word
            (x,y)=text.GetTextExtent(message[startofline:]+firstword)
            if x>txtwidth:
                if startofline!=len(message):
                    message+='\n'
                    startofline=len(message)
                else:
                    txtwidth=x	# Grow dialog to fit long word
            message+=word+' '
            if '\n' in word:
                startofline=len(message)-len(word)+len(firstword)
        text.SetLabel(message)

        box1=wx.BoxSizer(wx.HORIZONTAL)
        box1.Add([24,0])
        box1.Add(bitmap)
        box1.Add([16,0])
        box1.Add(text, 1)
        box1.Add([24,0])
        panel1.SetSizer(box1)

        button2=wx.Button(panel2, wx.ID_OK)
        box2=wx.BoxSizer(wx.HORIZONTAL)
        box2.Add([0,0], 1)	# push following buttons to right
        box2.Add(button2, 0, wx.ALL, pad)
        box2.Add([22,0])
        button2.SetDefault()
        panel2.SetSizer(box2)

        box0=wx.BoxSizer(wx.VERTICAL)
        box0.Add([0,15])
        box0.Add(panel1, 0, wx.ALL|wx.EXPAND)
        box0.Add([0,10-pad])
        box0.Add(panel2, 0, wx.ALL|wx.EXPAND)
        box0.Add([0,20-pad])
        panel0.SetSizer(box0)

        # Manually resize since can't get dlg.GetBestSize to work correctly
        (x,y)=text.GetBestSize()
        dlg.SetClientSize((24+48+16+txtwidth+24, max(y,48)+15+10+20+20))
        dlg.CenterOnParent()
        dlg.ShowModal()
        dlg.Destroy()


# main
frame=MainWindow(None, wx.ID_ANY, appname)
if platform=='win32':
    frame.SetIcon(wx.Icon('win32/FS2XPlane.ico', wx.BITMAP_TYPE_ICO))
elif platform.lower().startswith('linux'):	# PNG supported by GTK
    frame.SetIcon(wx.Icon('Resources/FS2XPlane.png', wx.BITMAP_TYPE_PNG))
elif platform=='darwin':
    pass	# icon pulled from Resources via Info.plist
app.SetTopWindow(frame)
app.MainLoop()
