from os import chdir, mkdir, system
from os.path import abspath, dirname, exists, isdir, join
from sys import exit, argv

from convmain import Output


def status(msg):
    print msg

def log(msg):
    if not isdir(dirname(logname)):
        mkdir(dirname(logname))
    logfile=file(logname, 'at')
    logfile.write("%s\n" % msg)
    logfile.close()
    
def fatal(msg):
    exit("Error:\t%s" % msg)
    

# Path validation
if len(argv)!=3:
    exit("Usage:\tfs2x.py path_to_MSFS_scenery path_to_X-Plane_scenery\n")
mypath=dirname(abspath(argv[0]))
if not isdir(mypath):
    fatal('"%s" is not a directory' % path)
chdir(mypath)

fspath=abspath(argv[1])
xppath=abspath(argv[2])
logname=abspath(join(xppath, 'errors.txt'))

output=Output(xppath,fspath,status,log,logname,fatal)
output.export()

if exists(logname):
    status('Displaying error log "%s"' % logname)
    system('"%s"' % logname)
else:
    status('Done')
