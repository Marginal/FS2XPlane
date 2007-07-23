#!/usr/bin/pythonw

#
# Copyright (c) 2006,2007 Jonathan Harris
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
from os import chdir, getenv, listdir, mkdir, makedirs
from os.path import abspath, basename, curdir, dirname, expanduser, exists, isdir, join, normpath, pardir, sep
from sys import argv, exit, platform, version
from traceback import print_exc

from convutil import asciify, unicodeify, sortfolded

if platform.lower().startswith('linux') and not getenv("DISPLAY"):
    print "Can't run: DISPLAY is not set"
    exit(1)
    
if platform=='win32':
    import wx
else:
    try:
        import wx
    except:
        import Tkinter
        import tkMessageBox
        Tkinter.Tk().withdraw()	# make and suppress top-level window
        if platform=='darwin':
            tkMessageBox._show("Error", "wxPython is not installed.\nThis application requires\nwxPython2.5.3-py%s or later." % version[:3], icon="question", type="ok")
        else:	# linux
            tkMessageBox._show("Error", "wxPython is not installed.\nThis application requires\npython wxgtk2.5.3 or later.", icon="error", type="ok")
        exit(1)
    try:
        import OpenGL
    except:
        import Tkinter
        import tkMessageBox
        Tkinter.Tk().withdraw()	# make and suppress top-level window
        tkMessageBox._show("Error", "PyOpenGL is not installed.\nThis application requires\nPyOpenGL2 or later.", icon="error", type="ok")
        exit(1)

from convmain import Output
from convutil import FS2XError, viewer, helper
from MessageBox import myMessageBox, AboutBox
from version import appname, appversion

if platform=='darwin':
    from Carbon import Menu
    # Hack: wxMac 2.5 requires the following to get shadows to look OK:
    # ... wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM, 2)
    pad=2
    browse="Choose..."
else:
    pad=0
    browse="Browse..."


mypath=dirname(abspath(argv[0]))
if not isdir(mypath):
    myMessageBox('"%s" is not a folder' % mypath,
                  "Can't run", wx.ICON_ERROR|wx.CANCEL)
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
    logfile.write('%s\n' % msg.encode("utf-8"))
    logfile.close()
    

# Set up paths
newfsroot=None
if platform=='win32':
    from _winreg import OpenKey, CreateKey, QueryValueEx, SetValueEx, HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, REG_SZ, REG_EXPAND_SZ
    if isdir('C:\\X-Plane\\Custom Scenery'):
        xppath='C:\\X-Plane\\Custom Scenery'
    elif isdir(join(getenv("USERPROFILE", ""), "Desktop", "X-Plane", "Custom Scenery")):
        xppath=join(getenv("USERPROFILE", ""), "Desktop", "X-Plane", "Custom Scenery")

    for (ver,value) in [('10.0', 'AppPath'), ('10.0', 'SetupPath'), ('9.0', 'EXE Path')]:
        for key in [HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE]:
            try:
                handle=OpenKey(key, join('SOFTWARE\\Microsoft\\Microsoft Games\\Flight Simulator', ver))
                (v,t)=QueryValueEx(handle, value)
                handle.Close()
                if t==REG_EXPAND_SZ:
                    dirs=v.rstrip('\0').strip().split('\\')
                    for i in range(len(dirs)):
                        if dirs[i][0]==dirs[i][-1]=='%':
                            dirs[i]=getenv(dirs[i][1:-1],dirs[i])
                    v='\\'.join(dirs)
                if t in [REG_SZ,REG_EXPAND_SZ] and isdir(v):
                    v=join(v.rstrip('\0').strip(), 'Addon Scenery')
                    dirs=[i for i in listdir(v) if isdir(join(v,i))]
                    sortfolded(dirs)
                    if dirs:
                        fspath=join(v, dirs[0])
                    else:
                        fspath=v
                    lbpath=v	#join(v, 'Scenery')
                    break
            except:
                pass
        else:
            continue
        break
    else:
        if getenv("ProgramFiles"):
            fsroot=join(getenv("ProgramFiles"),"Microsoft Games","Flight Simulator 9")
            try:
                handle=CreateKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Microsoft Games\\Flight Simulator\\9.0')
                SetValueEx(handle, 'EXE Path', 0, REG_SZ, fsroot)
                handle.Close()
                handle=CreateKey(HKEY_LOCAL_MACHINE, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Flight Simulator 9.0")
                #SetValueEx(handle, 'DisplayName', 0, REG_SZ, 'Fake FS2004')
                SetValueEx(handle, 'InstallLocation', 0, REG_SZ, fsroot)
                handle.Close()
            except:
                pass
            v=join(fsroot, "Addon Scenery")
            if isdir(v):
                dirs=[i for i in listdir(v) if isdir(join(v,i))]
                sortfolded(dirs)
                if dirs:
                    fspath=join(v, dirs[0])
                else:
                    fspath=v
                lbpath=v
            else:
                newfsroot=fsroot

else:
    home=unicodeify(expanduser('~'))	# Unicode so paths listed as unicode
    for xppath in [join(home, 'Desktop', 'X-Plane', 'Custom Scenery'),
                   join(home, 'X-Plane', 'Custom Scenery')]:
        if isdir(xppath): break
    else:
        xppath=''
    fsroot=join(home, "FS2004")
    try:
        if platform.lower().startswith('linux'):
            helper(join(curdir,'linux','fake2004'))
        else:
            helper(join(curdir,'MacOS','fake2004'))
        newfsroot=fsroot
    except:
        pass
    v=join(fsroot, "Addon Scenery")
    if isdir(v):
        dirs=[i for i in listdir(v) if isdir(join(v,i))]
        sortfolded(dirs)
        if dirs:
            fspath=join(v, dirs[0])
        else:
            fspath=v
        lbpath=v
    else:
        newfsroot=fsroot

# Create fake FS2004 installation
if newfsroot:
    try:
        makedirs(newfsroot)
        v=join(newfsroot,"Addon Scenery")
        mkdir(v)
        mkdir(join(v,"scenery"))
        mkdir(join(v,"texture"))
        mkdir(join(newfsroot,"Effects"))
        mkdir(join(newfsroot,"Flights"))
        mkdir(join(newfsroot,"Scenery"))
        mkdir(join(newfsroot,"Texture"))
        open(join(newfsroot,"fs9.exe"), 'ab').close()
        open(join(newfsroot,"fs2002.exe"), 'ab').close()
        cfg=open(join(newfsroot,"scenery.cfg"), 'at')
        cfg.write("[General]\nTitle=FS9 World Scenery\nDescription=FS9 Scenery Data\n\n[Area.001]\nTitle=Addon Scenery\nLocal=Addon Scenery\nRemote=\nActive=TRUE\nRequired=FALSE\nLayer=1\n\n")
        cfg.close()
        fspath=lbpath=v
    except:
        newfsroot=None


class MainWindow(wx.Frame):
    def __init__(self, parent, id, title):

        self.progress = None	# Current progress dialog (or None)
        self.logname = None
        
        wx.Frame.__init__(self,parent,id,title)

        if platform=='win32':
            self.SetIcon(wx.Icon('win32/%s.ico' % appname, wx.BITMAP_TYPE_ICO))
        elif platform.lower().startswith('linux'):	# PNG supported by GTK
            self.SetIcon(wx.Icon('Resources/%s.png' % appname,
                                 wx.BITMAP_TYPE_PNG))
        elif platform=='darwin':
            # icon pulled from Resources via Info.plist. Need minimal menu
            menubar = wx.MenuBar()
            helpmenu = wx.Menu()
            helpmenu.Append(wx.ID_HELP, '%s Help\tCtrl-?'  % appname)
            wx.EVT_MENU(self, wx.ID_HELP, self.onHelp)
            helpmenu.Append(wx.ID_ABOUT, 'About %s'  % appname)
            wx.EVT_MENU(self, wx.ID_ABOUT, self.onAbout)
            menubar.Append(helpmenu, '&Help')
            self.SetMenuBar(menubar)

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
        grid1.Add(wx.StaticText(panel1, -1, "MSFS scenery location: "), 0,
                  wx.ALIGN_CENTER_VERTICAL)
        grid1.Add(self.fspath,     1,
                  wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, pad)
        grid1.Add(self.fsbrowse,   0,
                  wx.ALIGN_CENTER_VERTICAL|wx.ALL, pad)
        grid1.Add(wx.StaticText(panel1, -1, "Additional MSFS libraries: "), 0,
                  wx.ALIGN_CENTER_VERTICAL)
        grid1.Add(self.lbpath,     1,
                  wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, pad)
        grid1.Add(self.lbbrowse,   0,
                  wx.ALIGN_CENTER_VERTICAL|wx.ALL, pad)
        grid1.Add(wx.StaticText(panel1, -1, "X-Plane scenery location: "), 0,
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
        self.dumplib= wx.CheckBox(panel2,-1, "Just extract library objects")
        # use panel and sizer so tab order works normally
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box2.Add(self.season, 1)
        box2.Add(self.dumplib, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND,10)
        panel2.SetSizer(box2)

        wx.EVT_CHECKBOX(self, self.dumplib.GetId(), self.onDump)

        
        # 3rd panel - adjust order of buttons per Windows or Mac conventions
        if platform=='darwin':
            button31=wx.Button(panel3, wx.ID_EXIT)
            button32=wx.Button(panel3, wx.ID_APPLY, "Convert")
            button33=wx.Button(panel3, wx.ID_HELP)
            box3 = wx.BoxSizer(wx.HORIZONTAL)
            box3.Add([24,0], 0)	# cosmetic - balance button31
            box3.Add([0,0], 1)	# push following buttons to right
            box3.Add(button31, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, pad)
            box3.Add([6,0], 0)	# cosmetic
            box3.Add(button32, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, pad)
            box3.Add([0,0], 1)	# push following buttons to right
            box3.Add(button33, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, pad)
            button32.SetDefault()
        else:
            button31=wx.Button(panel3, wx.ID_HELP)
            if platform=='win32':
                button32=wx.Button(panel3, wx.ID_EXIT)
            else:
                button32=wx.Button(panel3, wx.ID_CLOSE)
            button33=wx.Button(panel3, wx.ID_APPLY, "Convert")
            box3 = wx.BoxSizer(wx.HORIZONTAL)
            box3.Add(button31, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, pad)
            box3.Add([0,0], 1)	# push following buttons to right
            box3.Add(button32, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, pad)
            box3.Add([6,0], 0)	# cosmetic
            box3.Add(button33, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, pad)
            button33.SetDefault()
        panel3.SetSizer(box3)
        
        wx.EVT_BUTTON(self, wx.ID_HELP, self.onHelp)
        wx.EVT_BUTTON(self, wx.ID_APPLY, self.onConvert)
        wx.EVT_BUTTON(self, wx.ID_CLOSE, self.onClose)
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

        if platform=='darwin':
            # Hack! Change name on application menu. wxMac always uses id 1.
            try:
                Menu.GetMenuHandle(1).SetMenuTitleWithCFString(appname)
            except:
                pass

        if newfsroot:
            myMessageBox('Install your MSFS sceneries under\n%s' % fspath, 'Created a fake FS2004 installation.', wx.ICON_INFORMATION|wx.OK, None)


    def onDump(self, evt):
        if self.dumplib.GetValue():
            self.fspath.Disable()
            self.fsbrowse.Disable()
        else:
            self.fspath.Enable()
            self.fsbrowse.Enable()

    def onFSbrowse(self, evt):
        style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
        if 'DD_DIR_MUST_EXIST' in dir(wx): style|=wx.DD_DIR_MUST_EXIST
        dlg=wx.DirDialog(self, "Location of MSFS scenery package:",
                         self.fspath.GetValue(), style)
        dlg.ShowModal()
        self.fspath.SetValue(dlg.GetPath())
        dlg.Destroy()

    def onLBbrowse(self, evt):
        style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
        if 'DD_DIR_MUST_EXIST' in dir(wx): style|=wx.DD_DIR_MUST_EXIST
        dlg=wx.DirDialog(self,"Location of additional MSFS scenery libraries:",
                         self.lbpath.GetValue(), style)
        dlg.ShowModal()
        self.lbpath.SetValue(dlg.GetPath())
        dlg.Destroy()

    def onXPbrowse(self, evt):
        dlg=wx.DirDialog(self, "Location for new X-Plane scenery package:",
                         self.xppath.GetValue(), wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        dlg.ShowModal()
        self.xppath.SetValue(dlg.GetPath())
        dlg.Destroy()

    def onClose(self, evt):
        self.Close()

    def onHelp(self, evt):
        viewer(join(curdir,appname+'.html'))

    def onAbout(self, evt):
        AboutBox(self)

    def onConvert(self, evt):
        dumplib=self.dumplib.GetValue()
        fspath=self.fspath.GetValue().strip()
        lbpath=self.lbpath.GetValue().strip()
        xppath=self.xppath.GetValue().strip()
        if not xppath:
            myMessageBox('You must specify an X-Plane scenery location',
                         "Can't convert.", wx.ICON_ERROR|wx.CANCEL, self)
            return
        xppath=abspath(xppath)

        if not dumplib:
            if not fspath:
                myMessageBox('You must specify a MSFS scenery location',
                             "Can't convert.", wx.ICON_ERROR|wx.CANCEL, self)
                return
            fspath=abspath(fspath)
            if not lbpath:
                lbpath=None
            else:
                lbpath=abspath(lbpath)
            if basename(xppath).lower()=='custom scenery':
                xppath=join(xppath, asciify(basename(fspath)))
        else:
            fspath=None
            if not lbpath:
                myMessageBox('You must specify a MSFS library location',
                             "Can't convert.", wx.ICON_ERROR|wx.CANCEL, self)
                return
            lbpath=abspath(lbpath)
            if basename(xppath).lower()=='custom scenery':
                xppath=join(xppath, asciify(basename(lbpath)))
            
        self.logname=abspath(join(xppath, 'summary.txt'))
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
                myMessageBox('Displaying summary "%s"' %(
                    self.logname), 'Done.', wx.ICON_INFORMATION|wx.OK, self)
            else:
                myMessageBox('', 'Done.', wx.ICON_INFORMATION|wx.OK, self)

        except FS2XError, e:
            myMessageBox(e.msg, 'Error during conversion.', wx.ICON_ERROR|wx.CANCEL, self)

        except:
            if not isdir(dirname(self.logname)):
                mkdir(dirname(self.logname))
            logfile=file(self.logname, 'at')
            logfile.write('\nInternal error\n')
            print_exc(None, logfile)
            logfile.close()
            viewer(self.logname)
            myMessageBox('Please report error in log\n"%s"'%(self.logname),
                         'Internal error.', wx.ICON_ERROR|wx.CANCEL, self)

        if self.progress:
            self.progress.Destroy()
            self.progress=None


# main
app=wx.PySimpleApp()
if platform=='win32':
    if app.GetComCtl32Version()>=600 and wx.DisplayDepth()>=32:
        wx.SystemOptions.SetOptionInt('msw.remap', 2)
    else:
        wx.SystemOptions.SetOptionInt('msw.remap', 0)

frame=MainWindow(None, wx.ID_ANY, appname)
app.SetTopWindow(frame)
app.MainLoop()
