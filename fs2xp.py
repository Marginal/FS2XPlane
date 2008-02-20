#!/usr/bin/python

#
# Copyright (c) 2006,2007 Jonathan Harris
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

from getopt import getopt, GetoptError
from os import chdir, mkdir
from os.path import abspath, normpath, basename, dirname, pardir, exists, isdir, join
from sys import exit, argv
from traceback import print_exc

from convmain import Output
from convutil import FS2XError, viewer

# callbacks
def status(percent, msg):
    if percent<0: print
    print msg.encode("latin1",'replace')

def log(msg):
    if not isdir(dirname(logname)):
        mkdir(dirname(logname))
    logfile=file(logname, 'at')
    logfile.write('%s\n' % msg.encode("latin1",'replace'))
    logfile.close()

def refresh():
    pass

def usage():
    exit('\nUsage:\tfs2xp [options] "MSFS scenery location" "X-Plane scenery location"\noptions:\t-l "Additional MSFS library location"\n\t\t-s Spring|Summer|Autumn|Winter\n\t\t-x\n\t\t-9\n')


# Path validation
mypath=dirname(abspath(argv[0]))
if not isdir(mypath):
    exit('"%s" is not a folder' % mypath)
if basename(mypath)=='MacOS':
    chdir(normpath(join(mypath,pardir)))	# Starts in MacOS folder
else:
    chdir(mypath)


# Arg validation
lbpath=None
season=0
debug=False
dds=False
dumplib=False
prof=False
try:
    (opts, args) = getopt(argv[1:], 'l:s:d9px?h')
except GetoptError, e:
    print '\nError:\t'+e.msg
    usage()
for (opt, arg) in opts:
    if opt in ['-?' or '-h']:
        usage()
    elif opt=='-l':
        lbpath=abspath(unicode(arg))
    elif opt=='-d':
        debug=True
    elif opt=='-9':
        dds=True
    elif opt=='-p':
        prof=True
    elif opt=='-x':
        dumplib=True
    elif opt=='-s':
        seasons=['spring','summer','autumn','winter']
        if arg.lower() not in seasons:
            print '\nError:\tSeason %s not recognized' % arg
            usage()
        season=seasons.index(arg.lower())
if len(args)!=2:
    usage()
if dumplib:
    if lbpath:
        exit("\nError:\tSpecify only one of -l and -x\n")
    else:
        fspath=None
        lbpath=abspath(unicode(args[0]))
else:
    fspath=abspath(unicode(args[0]))
xppath=abspath(unicode(args[1]))
logname=abspath(join(xppath, 'summary.txt'))
        

# Main
try:
    output=Output(fspath, lbpath, xppath, dumplib, season, dds,
                  status, log, refresh, debug and not prof)
    output.scanlibs()
    output.procphotos()
    if prof:
        from profile import run
        run('output.process()', join(xppath,'profile.dmp'))
    else:
        output.process()
        output.proclibs()
        output.export()
        if output.debug: output.debug.close()
    if exists(logname):
        status(-1, 'Displaying summary "%s"' % logname)
        viewer(logname)
    status(-1, 'Done.')

except FS2XError, e:
    exit('Error:\t%s\n' % e.msg)

except:
    status(-1, 'Internal error')
    print_exc()
    if not debug:
        if not isdir(dirname(logname)):
            mkdir(dirname(logname))
        logfile=file(logname, 'at')
        logfile.write('\nInternal error\n')
        print_exc(None, logfile)
        logfile.close()
        status(-1, 'Displaying error log "%s"' % logname)
        viewer(logname)
    else:
        print
    exit(1)
