#!/usr/bin/python

#
# Copyright (c) 2006-2012 Jonathan Harris
# 
# Mail: <x-plane@marginal.org.uk>
# Web:  http://marginal.org.uk/x-planescenery/
#
# See FS2XPlane.html for usage.
#
# This software is licensed under a Creative Commons License
#   Attribution-Noncommercial-Share Alike 3.0:
#
#   You are free:
#    * to Share - to copy, distribute and transmit the work
#    * to Remix - to adapt the work
#
#   Under the following conditions:
#    * Attribution. You must attribute the work in the manner specified
#      by the author or licensor (but not in any way that suggests that
#      they endorse you or your use of the work).
#    * Noncommercial. You may not use this work for commercial purposes.
#    * Share Alike. If you alter, transform, or build upon this work,
#      you may distribute the resulting work only under the same or
#      similar license to this one.
#
#   For any reuse or distribution, you must make clear to others the
#   license terms of this work.
#
# This is a human-readable summary of the Legal Code (the full license):
#   http://creativecommons.org/licenses/by-nc-sa/3.0/
#

import os	# for startfile
from os import chdir, getenv, listdir, mkdir, makedirs, getcwd
from os.path import abspath, basename, curdir, dirname, expanduser, exists, isdir, join, normpath, pardir, sep
import sys	# for path
from sys import argv, executable, exit, platform, version_info
from traceback import print_exc

if platform.lower().startswith('linux') and not getenv("DISPLAY"):
    print "Can't run: DISPLAY is not set"
    exit(1)

try:
    import wx
except:
    import Tkinter, tkMessageBox
    Tkinter.Tk().withdraw()
    tkMessageBox.showerror("Error", "wxPython is not installed.\nThis application requires wxPython 2.5.3 or later.")
    exit(1)

try:
    import OpenGL
except:
    import Tkinter, tkMessageBox
    Tkinter.Tk().withdraw()
    tkMessageBox.showerror("Error", "PyOpenGL is not installed.\nThis application\nrequires PyOpenGL 3.0.1 or later.")
    exit(1)

if not __debug__:
    import warnings
    warnings.simplefilter('ignore', DeprecationWarning)
    if hasattr(wx,'wxPyDeprecationWarning'):
        warnings.simplefilter('ignore', wx.wxPyDeprecationWarning)

from convmain import Output
from convutil import FS2XError, asciify, unicodeify, sortfolded, viewer, helper
from MessageBox import myMessageBox, AboutBox
from version import appname, appversion

sysdesc="%s %.2f\n" % (appname, appversion)


if platform=='darwin':
    # Hack: wxMac 2.5 requires the following to get shadows to look OK:
    # ... wx.ALIGN_CENTER_VERTICAL|wx.TOP|wx.BOTTOM, 2)
    pad=2
    browse="Choose..."
else:
    pad=0
    browse="Browse..."

# Path validation
mypath = sys.path[0]
if platform=='win32' and mypath.lower().endswith('.exe'):
    mypath = dirname(mypath)		# py2exe
elif platform=='darwin' and basename(mypath)=='MacOS':
    mypath = dirname(mypath)		# App starts in MacOS folder
    sys.path.insert(0, join(mypath, 'MacOS', '%d%d' % version_info[:2]))
    argv[0]=basename(argv[0])		# wx doesn't like non-ascii chars in argv[0]
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
            # Too narrow for long paths
            (x,y)=frame.progress.GetClientSize()
            if platform=='darwin':
                frame.progress.SetClientSize((x+x,y))
            elif platform=='win32':
                frame.progress.SetClientSize((x+x/2,y))                
            frame.progress.CenterOnParent()
    else:
        if not frame.progress.Update(percent, msg):
            raise FS2XError('Stopped')

def log(msg):
    logfile=file(frame.logname, 'at')
    logfile.write('%s\n' % msg.encode("latin1",'replace'))
    logfile.close()

def refresh():
    app.Yield()


# Set up paths
newfsroot=None
if platform=='win32':
    from sys import getwindowsversion
    sysdesc+="System:\tWindows %s.%s %s\n" % (getwindowsversion()[0], getwindowsversion()[1], getwindowsversion()[4])
    from _winreg import OpenKey, QueryValueEx, HKEY_LOCAL_MACHINE, HKEY_CURRENT_USER, REG_SZ, REG_EXPAND_SZ
    progs=getenv("PROGRAMFILES", '\\').decode('mbcs')
    for i in listdir(progs):
        if i.lower().startswith("x-plane") and isdir(join(progs, i, "Custom Scenery")):
            xppath=join(progs, i, "Custom Scenery")
            break
    else:
        xppath=getenv("USERPROFILE", 'C:\\').decode('mbcs')	# fallback
        try:
            handle=OpenKey(HKEY_CURRENT_USER, 'Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\User Shell Folders')
            (v,t)=QueryValueEx(handle, 'Desktop')
            handle.Close()
            if t==REG_EXPAND_SZ:
                dirs=v.rstrip('\0').decode('mbcs').strip().split('\\')
                for i in range(len(dirs)):
                    if dirs[i][0]==dirs[i][-1]=='%':
                        dirs[i]=getenv(dirs[i][1:-1],dirs[i]).decode('mbcs')
                v='\\'.join(dirs)
            if t in [REG_SZ,REG_EXPAND_SZ] and isdir(v):
                xppath=desktop=v
                for i in listdir(desktop):
                    if i.lower().startswith("x-plane") and isdir(join(desktop, i, "Custom Scenery")):
                        xppath=join(desktop, i, "Custom Scenery")
                        break
        except:
            pass
    fspath=lbpath=join(getenv("ProgramFiles").decode('mbcs') or "C:\\Program Files","Microsoft Games","Microsoft Flight Simulator X","Addon Scenery")	# fallback
    try:
        handle=OpenKey(HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\Microsoft Games\\Flight Simulator\\10.0')
        (v,t)=QueryValueEx(handle, 'SetupPath')
        handle.Close()
        if t==REG_EXPAND_SZ:
            dirs=v.rstrip('\0').strip().split('\\')
            for i in range(len(dirs)):
                if dirs[i][0]==dirs[i][-1]=='%':
                    dirs[i]=getenv(dirs[i][1:-1],dirs[i]).decode('mbcs')
            v='\\'.join(dirs)
        if t in [REG_SZ,REG_EXPAND_SZ] and isdir(v):
            v=join(v.rstrip('\0').strip(), 'Addon Scenery')
            dirs=[i for i in listdir(v) if isdir(join(v,i)) and i.lower() not in ['scenery','texture']]
            sortfolded(dirs)
            if dirs:
                fspath=join(v, dirs[0])
            else:
                fspath=v
            lbpath=v
    except:
        pass

else:	# Mac & linux
    if platform=='darwin':
        from platform import mac_ver
        sysdesc+="System:\tMacOS %s %s\n" % (mac_ver()[0], mac_ver()[2])
    else:
        from os import uname	# not defined in win32 builds
        sysdesc+="System:\t%s %s %s\n" % (uname()[0], uname()[2], uname()[4])
    try:
        home=expanduser('~').decode(sys.getfilesystemencoding() or 'utf-8')	# Unicode so paths listed as unicode
        desktop=join(home, "Desktop")
    except:
        home=desktop=u'/'
    for i in listdir(desktop):
        if i.lower().startswith("x-plane") and isdir(join(desktop, i, "Custom Scenery")):
            xppath=join(desktop, i, "Custom Scenery")
            break
    else:
        for i in listdir(home):
            if i.lower().startswith("x-plane") and isdir(join(home, i, "Custom Scenery")):
                xppath=join(home, i, "Custom Scenery")
                break
        else:
            xppath=home
    fsroot=join(home, "FS2004")
    try:
        if platform.lower().startswith('linux'):
            sysdesc+="Wine:\t%s\n" % helper(join(curdir,'linux','winever'))
            helper(join(curdir,'linux','fake2004'))
        else:
            sysdesc+="Wine:\t%s\n" % helper(join(curdir,'MacOS','winever'))
            helper(join(curdir,'MacOS','fake2004'))
    except:
        pass
    v=join(fsroot, "Addon Scenery")
    if isdir(v):
        dirs=[i for i in listdir(v) if isdir(join(v,i)) and i.lower() not in ['scenery','texture']]
        sortfolded(dirs)
        if dirs:
            fspath=join(v, dirs[0])
        else:
            fspath=v
        lbpath=v
    else:
        # Create fake FS2004 installation if no Addon Scenery folder
        newfsroot=fsroot
        fspath=lbpath=join(newfsroot,"Addon Scenery")
        try:
            if not isdir(newfsroot): makedirs(newfsroot)
            mkdir(fspath)
            mkdir(join(fspath,"scenery"))
            mkdir(join(fspath,"texture"))
            mkdir(join(newfsroot,"Effects"))
            mkdir(join(newfsroot,"Flights"))
            mkdir(join(newfsroot,"SimObjects"))
            mkdir(join(newfsroot,"Scenery"))
            mkdir(join(newfsroot,"Texture"))
            open(join(newfsroot,"fs2002.exe"), 'ab').close()
            open(join(newfsroot,"fs9.exe"), 'ab').close()
            open(join(newfsroot,"fsx.exe"), 'ab').close()
            cfg=open(join(newfsroot,"scenery.cfg"), 'at')
            cfg.write("[General]\nTitle=FS9 World Scenery\nDescription=FS9 Scenery Data\n\n[Area.001]\nTitle=Addon Scenery\nLocal=Addon Scenery\nRemote=\nActive=TRUE\nRequired=FALSE\nLayer=1\n\n")
            cfg.close()
        except:
            pass


class MainWindow(wx.Frame):
    def __init__(self, parent, id, title):

        self.progress = None	# Current progress dialog (or None)
        self.logname = None
        
        wx.Frame.__init__(self,parent,id,title)

        if platform=='win32':
            self.SetIcon(wx.Icon(executable, wx.BITMAP_TYPE_ICO))
        elif platform.lower().startswith('linux'):	# PNG supported by GTK
            icons=wx.IconBundle()
            icons.AddIconFromFile('Resources/%s.png' % appname, wx.BITMAP_TYPE_PNG)
            icons.AddIconFromFile('Resources/%s-128.png'% appname, wx.BITMAP_TYPE_PNG)
            self.SetIcons(icons)
        elif platform=='darwin':
            # icon pulled from Resources via Info.plist (except for MessageBox icon). Need minimal menu
            menubar = wx.MenuBar()
            helpmenu = wx.Menu()
            helpmenu.Append(wx.ID_HELP, '%s Help\tCtrl-?'  % appname)
            wx.EVT_MENU(self, wx.ID_HELP, self.onHelp)
            helpmenu.Append(wx.ID_ABOUT, 'About %s'  % appname)
            wx.EVT_MENU(self, wx.ID_ABOUT, self.onAbout)
            # ID_EXIT moved to application menu
            helpmenu.Append(wx.ID_EXIT, u'Quit %s\tCtrl-Q' % appname)
            wx.EVT_MENU(self, wx.ID_EXIT, self.onClose)
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
        grid1 = wx.FlexGridSizer(3, 3, 7, 7)
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
        self.xpver  = wx.RadioBox(panel2,-1, "Minimum X-Plane version:",
                                  choices=["v8", "v9", "v10"])
        self.xpver.SetSelection(2)	# v10 default
        self.season = wx.RadioBox(panel2,-1, "Season:",
                                  choices=["Spring", "Summer",
                                           "Autumn", "Winter"])
        self.dumplib= wx.CheckBox(panel2,-1, "Just extract library objects")
        # use panel and sizer so tab order works normally
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        box2.Add(self.xpver, 0)
        box2.Add(self.season, 0, wx.LEFT, 10)
        box2.Add([0,0], 1, wx.LEFT, 10)	# push following buttons to right
        box2.Add(self.dumplib, 0, wx.TOP|wx.EXPAND, 8)
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
        self.SetSize((800, height))
        # +50 is a hack cos I can't work out how to change minsize of TextCtrl
        self.SetSizeHints(sz.width, height, -1, height)
        self.Show(True)

        if platform=='darwin':
            # Change name on application menu. Can't do this in wx.
            try:	# Carbon
                from Carbon import Menu
                Menu.GetMenuHandle(1).SetMenuTitleWithCFString(appname)		# wxMac always uses id 1.
            except:
                try:	# Cocoa
                    import AppKit
                    # doesn't work: AppKit.NSApp.mainMenu().itemAtIndex_(0).submenu().setTitle_(appname)	 http://www.mail-archive.com/cocoa-dev@lists.apple.com/msg43196.html
                    AppKit.NSBundle.mainBundle().infoDictionary()['CFBundleName']=appname
                except:
                    if __debug__: print_exc()

        if newfsroot: myMessageBox('Install MSFS sceneries under: \n%s ' % newfsroot, 'Created a fake MSFS installation.', wx.ICON_INFORMATION|wx.OK, self)


    def onDump(self):
        if self.dumplib.GetValue():
            self.fspath.Disable()
            self.fsbrowse.Disable()
        else:
            self.fspath.Enable()
            self.fsbrowse.Enable()

    def onFSbrowse(self):
        style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
        if 'DD_DIR_MUST_EXIST' in dir(wx): style|=wx.DD_DIR_MUST_EXIST
        dlg=wx.DirDialog(self, "Location of MSFS scenery package:",
                         self.fspath.GetValue(), style)
        dlg.ShowModal()
        self.fspath.SetValue(dlg.GetPath())
        dlg.Destroy()

    def onLBbrowse(self):
        style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER
        if 'DD_DIR_MUST_EXIST' in dir(wx): style|=wx.DD_DIR_MUST_EXIST
        dlg=wx.DirDialog(self,"Location of additional MSFS scenery libraries:",
                         self.lbpath.GetValue(), style)
        dlg.ShowModal()
        self.lbpath.SetValue(dlg.GetPath())
        dlg.Destroy()

    def onXPbrowse(self):
        dlg=wx.DirDialog(self, "Location for new X-Plane scenery package:",
                         self.xppath.GetValue(), wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)
        dlg.ShowModal()
        self.xppath.SetValue(dlg.GetPath())
        dlg.Destroy()

    def onClose(self):
        self.Close()

    def onHelp(self, evt):
        viewer(join(curdir,'Resources',appname+'.html'))

    def onAbout(self):
        AboutBox(self)

    def onConvert(self):
        dumplib=self.dumplib.GetValue()
        fspath=self.fspath.GetValue().strip()
        lbpath=self.lbpath.GetValue().strip()
        xppath=self.xppath.GetValue().strip()
        if not xppath:
            myMessageBox('You must specify an X-Plane scenery location',
                         "Can't convert.", wx.ICON_ERROR|wx.OK, self)
            return
        xppath=abspath(xppath)

        if not dumplib:
            if not fspath:
                myMessageBox('You must specify a MSFS scenery location',
                             "Can't convert.", wx.ICON_ERROR|wx.OK, self)
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
                             "Can't convert.", wx.ICON_ERROR|wx.OK, self)
                return
            lbpath=abspath(lbpath)
            if basename(xppath).lower()=='custom scenery':
                xppath=join(xppath, asciify(basename(lbpath)))
            
        season=self.season.GetSelection()	# zero-based
        xpver=self.xpver.GetSelection()+8	# zero-based

        try:
            self.logname=abspath(join(xppath, 'summary.txt'))
            if not isdir(dirname(self.logname)):
                mkdir(dirname(self.logname))
            logfile=file(self.logname, 'wt')
            logfile.write("%sTarget:\tX-Plane %d\n\n" % (sysdesc,xpver))
            logfile.close()
        except IOError, e:
            myMessageBox('Can\'t write to folder\n"%s"' % xppath,
                         e.strerror, wx.ICON_ERROR|wx.OK, self)
            return
        except WindowsError, e:
            myMessageBox('Can\'t write to folder\n"%s"' % xppath,
                         e.strerror, wx.ICON_ERROR|wx.OK, self)
            return

        try:
            output=Output(fspath, lbpath, xppath, dumplib, season, xpver,
                          status,log,refresh, False)
            output.scanlibs()
            output.process()
            output.proclibs()
            output.procphotos()
            output.export()
            if self.progress:
                self.progress.Destroy()
                self.progress=None
            if output.debug: output.debug.close()
            if exists(self.logname):
                viewer(self.logname)
                myMessageBox('Displaying summary\n"%s"' %(
                    self.logname), 'Done.', wx.ICON_INFORMATION|wx.OK, self)
            else:
                myMessageBox('', 'Done.', wx.ICON_INFORMATION|wx.OK, self)

        except FS2XError, e:
            if exists(self.logname):
                logfile=file(self.logname, 'at')
                logfile.write('%s\n' % e.msg.encode("latin1",'replace'))
                logfile.close()
            myMessageBox(e.msg, 'Error during conversion.', wx.ICON_ERROR|wx.OK, self)

        except:
            logfile=file(self.logname, 'at')
            logfile.write('\nInternal error\n')
            print_exc(None, logfile)
            logfile.close()
            viewer(self.logname)
            myMessageBox('Please report error in log\n"%s"'% self.logname,
                         'Internal error.', wx.ICON_ERROR|wx.OK, self)

        if self.progress:
            self.progress.Destroy()
            self.progress=None


# main
app=wx.App(redirect=not __debug__)
app.SetAppName(appname)
if platform=='win32':
    if app.GetComCtl32Version()>=600 and wx.DisplayDepth()>=32:
        wx.SystemOptions.SetOptionInt('msw.remap', 2)
    else:
        wx.SystemOptions.SetOptionInt('msw.remap', 0)

frame=MainWindow(None, wx.ID_ANY, appname)
app.SetTopWindow(frame)
app.MainLoop()
