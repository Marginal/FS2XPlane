from os import chdir, mkdir, startfile
from os.path import abspath, dirname, exists, isdir, join
from sys import exit, argv

from convmain import Output


def status(msg):
    print msg

def log(msg):
    if not isdir(dirname(logname)):
        mkdir(dirname(logname))
    logfile=file(logname, 'at')
    logfile.write('%s\n' % msg)
    logfile.close()
    
def fatal(msg):
    exit('Error:\t%s\n' % msg)
    

# Path validation
if len(argv)!=3:
    exit("Usage:\tfs2x.py path_to_MSFS_scenery path_to_X-Plane_scenery\n")
mypath=dirname(abspath(argv[0]))
if not isdir(mypath):
    fatal('"%s" is not a folder' % path)
chdir(mypath)

fspath=abspath(argv[1])
xppath=abspath(argv[2])
logname=abspath(join(xppath, 'errors.txt'))

output=Output(mypath,xppath,fspath,status,log,fatal)
output.export()

if exists(logname):
    status('Displaying error log "%s"' % logname)
    startfile(logname)
else:
    status('Done')
