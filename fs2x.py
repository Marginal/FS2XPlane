#!python

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

from getopt import getopt, GetoptError
import os	# for startfile
from os import chdir, mkdir
from os.path import abspath, dirname, exists, isdir, join
from sys import exit, argv

from convmain import Output
from convutil import FS2XError

# callbacks
def status(percent, msg):
    if percent<0: print
    print msg

def log(msg):
    if not isdir(dirname(logname)):
        mkdir(dirname(logname))
    logfile=file(logname, 'at')
    logfile.write('%s\n' % msg)
    logfile.close()

def usage():
    exit("\nUsage:\tfs2x.py [options] <MSFS scenery location> <X-Plane scenery location>\noptions:\t-l <Additional MSFS library location>\n\t\t-s Spring|Summer|Autumn|Winter\n")


# Path validation
mypath=dirname(abspath(argv[0]))
if not isdir(mypath):
    exit('"%s" is not a folder' % mypath)
chdir(mypath)


# Arg validation
lbpath=None
season=0
debug=False
dumplib=False
try:
    (opts, args) = getopt(argv[1:], 'l:s:d?hx')
except GetoptError, e:
    print '\nError:\t'+e.msg
    usage()
for (opt, arg) in opts:
    if opt in ['-?' or '-h']:
        usage()
    elif opt=='-l':
        lbpath=abspath(arg)
    elif opt=='-d':
        debug=True
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


fspath=abspath(args[0])
xppath=abspath(args[1])
logname=abspath(join(xppath, 'errors.txt'))


# Main
try:
    output=Output(mypath,fspath,lbpath,xppath,season,status,log,
                  dumplib, debug)
    output.scanlibs()
    output.process()
    output.proclibs()
    output.export()
    if exists(logname):
        if 'startfile' in dir(os):
            status(-1, 'Displaying error log "%s"' % logname)
            os.startfile(logname)
        else:
            status(-1, 'Errors found; see log "%s"' % logname)
    status(-1, 'Done.')
except FS2XError, e:
    exit('Error:\t%s\n' % e.msg)
