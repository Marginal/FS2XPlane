from math import floor, sin, cos, radians
from os import curdir, listdir, mkdir, pardir, sep, stat, unlink, walk
from os.path import basename, dirname, exists, isdir, join, normpath, splitext
from shutil import copyfile
from StringIO import StringIO
import struct	# for struct.error
from struct import pack, unpack
from sys import exit, platform, maxint
from traceback import print_exc
from tempfile import gettempdir

from convutil import asciify, banner, helper, complexities, AptNav, Object, Polygon, Point, FS2XError, sortfolded
from convobjs import makestock, ignorestock, friendlytxt, friendlyxml
from convbgl import ProcEx, maketexdict
from convphoto import ProcPhoto
import convbgl
import convmdl
import convxml

class Output:
    def __init__(self, fspath, lbpath, xppath, dumplib, season, xpver,
                 status, log, refresh, debug):

        self.dumplib=dumplib
        if dumplib:
            self.fspath=None
        else:
            self.fspath=fspath
        self.lbpath=lbpath
        self.xppath=xppath
        self.hemi=0	# 0=N, 1=S
        self.season=season

        # X-Plane features
        self.xpver=xpver
        self.dds=(xpver>=9)
        self.draped=(xpver>=10)
        self.doatc=(xpver>=10)
        self.doexcfac=False	# Apply exclusions to airport data?
        self.usesopensceneryx=False

        # Callbacks
        self.status=status
        self.log=log
        self.refresh=refresh

        self.apt={}	# (location, AptNav entries) by ICAO code
        self.aptfull={}	# version of the above with nothing excluded
        self.nav=[]
        self.misc=[]
        self.atc={}	# [(name, role, freq)] by ICAO code
        self.done={}	# BGL files that we've already processed
        self.exc=[]	# Exclusion rectangles: (type, bottomleft, topright)
        self.excfac=[]	# Exclusion rectangles for facility data
        self.doingexcfac=False	# Process exclusions?
        self.needfull=False	# Some apt.dat features are excluded?
        self.libobj={}	# Lib objects: (MDL, f, cmp, offset, size, name, scale) by uid
        self.objplc=[]	# Object placements:	(loc, hdg, cmplx, name, scale)
        self.objdat={}	# Objects by name
        self.polyplc=[]	# Poly placements: [(name, hdg, [loc, u, v])]
        self.polydat={}	# Polygons by name
        self.stock={}	# FSX stock objects - we don't have these
        self.friendly={}	# GUID->friendly name map
        self.subst={}	# Library substitutions for some stock objects
        self.names={}	# friendly names must be unique
        self.haze={}	# Textures that have palette-based transparency
        self.donetex={}	# Textures we have seen (avoid multiple convert/report)
        self.visrunways=False	# Runways on top of scenery - should be per apt
        
        if platform=='win32':
            self.bglexe=join(curdir,'win32','bglunzip.exe')
            self.xmlexe=join(curdir,'win32','bglxml.exe')
            self.pngexe=join(curdir,'win32','bmp2png.exe')
            self.ddsexe=join(curdir,'win32','bmp2dds.exe')
            self.dsfexe=join(curdir,'win32','DSFTool.exe')
        elif platform.lower().startswith('linux'):
            self.bglexe=join(curdir,'linux','bglunzip')
            self.xmlexe=join(curdir,'linux','bglxml')
            self.pngexe=join(curdir,'linux','bmp2png')
            self.ddsexe=join(curdir,'linux','bmp2dds')
            self.dsfexe=join(curdir,'linux','DSFTool')
        else:	# Mac
            self.bglexe=join(curdir,'MacOS','bglunzip')
            self.xmlexe=join(curdir,'MacOS','bglxml')
            self.pngexe=join(curdir,'MacOS','bmp2png')
            self.ddsexe=join(curdir,'MacOS','bmp2dds')
            self.dsfexe=join(curdir,'MacOS','DSFTool')

        for path in [fspath, lbpath]:
            if path and not exists(path):
                raise FS2XError('"%s" does not exist' % path)
            if path and not isdir(path):
                raise FS2XError('"%s" is not a folder' % path)

        if self.dds:
            self.palettetex='Resources/FS2X-palette.dds'
        else:
            self.palettetex='Resources/FS2X-palette.png'
        self.addtexdir=None
        try:
            for f in listdir(lbpath):
                if f.lower()=='texture':
                    self.addtexdir=maketexdict(join(lbpath, f))
                    break
        except:
            pass

        if not self.dumplib and (basename(dirname(xppath)).lower()!='custom scenery' or not isdir(dirname(xppath))):
            raise FS2XError('The "X-Plane scenery location" must be a sub-folder\nof X-Plane\'s Custom Scenery folder.')
        for path, dirs, files in walk(xppath):
            for f in dirs+files:
                if f!='summary.txt' and not f.startswith('.'):
                    raise FS2XError('"%s" already exists and is not empty' % (
                        xppath))

        for exe in [self.bglexe, self.xmlexe, self.pngexe, self.dsfexe]:
            if exe and not exists(exe):
            	raise FS2XError("Can't find \"%s\"" % exe)

        if platform.lower().startswith('linux'):
            # check for win32 executables under wine
            if not exists(join(curdir,'win32','bglunzip.exe')):
                raise FS2XError("Can't find \"%s\"" % exe)

        path=join('Resources', 'objects.txt')
        try:
            stock=file(path, 'rU')
        except IOError:
            raise FS2XError("Can't read \"%s\"." % path)
        for line in stock:
            line=line.split()
            if not line or line[0].startswith('#'): continue
            assert line[0] not in self.stock and len(line)==2, line[0]
            name=line[1]
            self.stock[line[0]]=name
            self.names[name]=True
        stock.close()

        # Standard Rwy12 mappings
        friendlyxml(join('Resources', 'Rwy12.xml'), self.friendly, self.names)

        # Library substitutions for stock objects
        # Assumed to be a strict subset of self.stock
        path=join('Resources', 'substitutions.txt')
        try:
            stock=file(path, 'rU')
        except IOError:
            raise FS2XError("Can't read \"%s\"." % path)
        for line in stock:
            line=line.split()
            if not line or line[0].startswith('#'): continue
            if len(line)==6:	# X-Plane library item only available in later versions
                if int(line[1])<=self.xpver:
                    line.pop(1)
                else:
                    continue
            else:
                assert line[0] not in self.subst and len(line)==5, line[0]
            assert line[0] in self.names, line[0]
            self.subst[line[0]]=(line[1],float(line[2]),float(line[3]),float(line[4]))
        stock.close()

        if debug:
            # note full debugging also requires non-optimised execution
            if not isdir(self.xppath): mkdir(self.xppath)
            self.debug=file(join(self.xppath,'debug.txt'),'at')
        else:
            self.debug=None

        # See if scenery package is registered eg by Addon Manager.
        # Otherwise try to emulate that the demo has expired.
        self.registered=False
        if platform=='win32':
            from _winreg import OpenKey, EnumKey, QueryValueEx, HKEY_CURRENT_USER
            handle=handle2=None
            try:
                c=self.fspath.split(sep)
                company=c[-2].lower()
                package=c[-1].replace(' ','').lower()[:-1]
                if company!='addon scenery':
                    handle=OpenKey(HKEY_CURRENT_USER, 'Software\\'+company)
                    i=0
                    while True:
                        v=EnumKey(handle, i)
                        if package in v.replace(' ','').lower():
                            handle2=OpenKey(handle,v)
                            if QueryValueEx(handle2, 'SerialNumber'):
                                self.registered=True
                                if self.debug: self.debug.write('Registered\n')
                                break
                            break
                        i+=1
                        # EnvironmentError raised when no more values
            except:
                pass
            if handle: handle.Close()
            if handle2: handle2.Close()


    # Fill out self.libobj
    def scanlibs(self):
        self.status(-1, 'Scanning libraries')
        if self.debug: self.debug.write('Library objects\n')

        for toppath in [self.fspath, self.lbpath]:	# do local first
            if not toppath:
                continue

            # read Rwy12 UID mappings
            for path, dirs, files in walk(toppath):
                for filename in files:
                    if filename[-4:].lower()=='.xml':
                        friendlyxml(join(path,filename), self.friendly, self.names)
                        
            for path, dirs, files in walk(toppath):
                if basename(path).lower()!='scenery':
                    continue	# Only look at BGLs in 'scenery' directory
                n = len(files)
                for i in range(n):
                    filename=files[i]
                    if filename[-4:].lower()!='.bgl':
                        continue
                    if exists(join(path,filename[:-4]+'.txt')):
                        # read EZ-Scenery UID mapping
                        friendlytxt(filename[:-4]+'.txt', self.friendly, self.names)
                    bglname=join(path, filename)
                    if stat(bglname).st_size==0:
                        self.done[bglname]=True
                        continue	# Sometimes seen 0-length files!
                    try:
                        bgl=file(bglname, 'rb')
                    except IOError:
                        self.log("Can't read \"%s\"" % filename)
                        self.done[bglname]=True
                        continue
                    c=bgl.read(2)
                    if len(c)!=2:
                        self.log("Can't read \"%s\"" % filename)
                        self.done[bglname]=True
                        continue
                    done=True
                    (c,)=unpack('<H', c)
                    if c&0xff00==0:
                        # Old-style
                        for section in [42,46,54,58,102]:
                            bgl.seek(section)
                            (secbase,)=unpack('<I',bgl.read(4))
                            if secbase: done=False	# Includes other data
                        bgl.seek(62)	# LIBRARY data
                        (libbase,)=unpack('<I',bgl.read(4))
                        if toppath==self.fspath:
                            bgl.seek(114)	# EXCLUSION data
                            (excbase,)=unpack('<I',bgl.read(4))
                        else:
                            excbase=0
                        if not (libbase or excbase): continue
                        self.status(i*100.0/n, bglname[len(toppath)+1:])
                        tmp=bglname
                        bgl.seek(122)
                        (spare2,)=unpack('<I',bgl.read(4))
                        if spare2:
                            # compressed
                            bgl.close()
                            tmp=join(gettempdir(), filename)
                            if platform!='win32':
                                compressed=bglname
                                # Wine can't handle non-ascii?
                                try:
                                    bglname[len(toppath):].encode("ascii")
                                except:
                                    compressed=join(gettempdir(), 'fs2xp1.bgl')
                                    copyfile(bglname, compressed)
                                    tmp=join(gettempdir(), 'fs2xp2.bgl')
                                helper(self.bglexe, compressed, tmp)
                                if compressed!=bglname: unlink(compressed)
                            else:
                                helper(self.bglexe, bglname, tmp)
                            if not exists(tmp):
                                # Check for uncompressed version
                                tmp=join('Resources',basename(bglname).lower())
                                if not exists(tmp):
                                    self.log("Can't parse compressed file %s"%(
                                        filename))
                                    continue	# don't mark as done
                            bgl=file(tmp, 'rb')
                        # Exclusions
                        if excbase:
                            bgl.seek(excbase)
                            if self.debug: self.debug.write('%s\n' % filename.encode("latin1", 'replace'))
                            try:
                                ProcEx(bgl, self)
                            except:
                                self.log("Can't parse Exclusion section in file %s" % filename)
                                if self.debug: print_exc(None, self.debug)
                        if not libbase: continue
                        bgl.seek(libbase)
                        try:
                            while True:
                                pos=bgl.tell()
                                (off,)=unpack('<I', bgl.read(4))
                                if off==0: break
                                (a,b,c,d)=unpack('<IIII',bgl.read(16))
                                uid = "%08x%08x%08x%08x" % (a,b,c,d)
                                bgl.seek(libbase+off)
                                (a,b,c,d,x)=unpack('<IIIIB',bgl.read(17))
                                if a==1 and b==2 and c==3 and d==4:	# fs98 library
                                    (rcsize,)=unpack('<H', bgl.read(2))
                                    hdsize=19
                                    scale=1.0
                                else:
                                    (hdsize,rcsize,radius,scale,typ,prop)=unpack('<6I',bgl.read(24))
                                    if scale:
                                        scale=65536.0/scale
                                    else:
                                        scale=1.0
                                name=None
                                if hdsize>42:
                                    # Use "friendly" name instead of id
                                    name=asciify(bgl.read(hdsize- 41).rstrip(' \0'))
                                if uid in self.friendly:
                                    name=self.friendly[uid]
                                elif not name and asciify(splitext(filename)[0]) not in self.names:
                                    name=asciify(splitext(filename)[0])
                                    self.friendly[uid]=name
                                    self.names[name]=True
                                elif name and name not in self.names:
                                    self.friendly[uid]=name
                                    self.names[name]=True
                                else:
                                    name=uid

                                if not uid in self.libobj:	# 1st wins
                                    if self.debug and toppath==self.fspath: self.debug.write("%s:\t%s\t%s\tFS8\n" % (uid, name, bglname[len(toppath)+1:]))
                                    self.libobj[uid]=(8, bglname, tmp, libbase+off+hdsize, rcsize, name, scale)
                                bgl.seek(pos+20)
                        except:
                            self.log("Error parsing FS8 library %s" % filename)
                            if self.debug: print_exc(None, self.debug)

                    elif c==0x201:
                        # FS9 or FSX
                        islib=False
                        bgl.seek(4)
                        (sectiontbl,)=unpack('<I',bgl.read(4))
                        bgl.seek(20)
                        (sections,)=unpack('<I',bgl.read(4))
                        for section in range(sections):
                            bgl.seek(sectiontbl+20*section)
                            (typ,x,subsections,subsectiontbl)=unpack('<IIIi', bgl.read(16))
                            #print "%x %x %d" % (typ,x,subsections)
                            if typ!=0x2b:	# 2b=MDL data
                                if typ==0x6e:	# Ortho and DEM BGLs seem to have a 6e section
                                    self.log('Skipping terrain data in file %s' % filename)
                                elif typ==0x65:
                                    self.log("Skipping traffic data in file %s" % filename)
                                else:
                                    done=False	# Something else - perhaps Facility data
                                continue
                            if not islib:
                                self.status(i*100.0/n,bglname[len(toppath)+1:])
                                islib=True
                            for subsection in range(subsections):
                                bgl.seek(subsectiontbl+16*subsection)
                                #print "  %x" % bgl.tell(),
                                (id,records,recordtbl)=unpack('<IIi',
                                                              bgl.read(12))
                                #print "%x %d" % (id,records)
                                for record in range(records):
                                    bgl.seek(recordtbl+record*24)
                                    (a,b,c,d,off,rcsize)=unpack('<IIIIiI',
                                                                bgl.read(24))
                                    uid = "%08x%08x%08x%08x" % (a,b,c,d)
                                    name=None

                                    # Check for FSX friendly name
                                    bgl.seek(recordtbl+off)
                                    if bgl.read(4)=='RIFF':
                                        (mdlsize,)=unpack('<I', bgl.read(4))
                                        if bgl.read(4)=='MDLX':
                                            mdlformat=10	# FSX format
                                            while bgl.tell()<recordtbl+off+mdlsize:
                                                c=bgl.read(4)
                                                (size,)=unpack('<I', bgl.read(4))
                                                if c=='MDLN':
                                                    name=asciify(bgl.read(size).strip('\0').strip())
                                                    break
                                                elif c=='MDLD':
                                                    break	# stop at data
                                                else:
                                                    bgl.seek(size,1)
                                        else:
                                            mdlformat=9	# FS9 format

                                    if uid in self.stock:
                                        name=self.stock[uid]
                                    elif uid in self.friendly:
                                        name=self.friendly[uid]
                                    elif not name and records==1 and asciify(splitext(filename)[0]) not in self.names:
                                        name=asciify(splitext(filename)[0])
                                        self.friendly[uid]=name
                                        self.names[name]=True
                                    elif name and name not in self.names:
                                        self.friendly[uid]=name
                                        self.names[name]=True
                                    else:
                                        name=uid

                                    if not uid in self.libobj:
                                        if self.debug and toppath==self.fspath: self.debug.write("%s:\t%s\t%s\tFS%d\n" % (uid, name, bglname[len(toppath)+1:], mdlformat))
                                        self.libobj[uid]=(mdlformat,
                                                          bglname, bglname,
                                                          recordtbl+off,rcsize,
                                                          name, 1.0)
                    else:
                        self.log("Can't parse file \"%s\". Is this a BGL file?" % filename)
                    bgl.close()
                    if done: self.done[bglname]=True


    # Fill out self.objplc, self.objdat, self.polyplc, self.polydat
    def procphotos(self):
        if self.dumplib: return
        self.status(-1, 'Reading Photoscenery')
        if self.debug: self.debug.write('Photoscenery\n')
        for path, dirs, files in walk(self.fspath):
            if basename(path).lower()=='texture':
                # Only look at BMPs in 'texture' directory
                try:
                    self.status(0, path[len(self.fspath)+1:])
                    ProcPhoto(path, self)
                except:
                    self.log("Can't parse this photoscenery")
                    if self.debug: print_exc(None, self.debug)


    # Fill out self.objplc, self.objdat, self.polyplc, self.polydat
    def process(self):
        if self.dumplib: return
        self.status(-1, 'Reading BGLs')
        if self.debug: self.debug.write('Procedural scenery\n')
        xmls=[]
        for path, dirs, files in walk(self.fspath):
            if basename(path).lower()!='scenery':
                continue	# Only look at BGLs in 'scenery' directory
            n = len(files)
            for i in range(n):
                self.gencount=0
                self.anchorcount=0
                filename=files[i]
                if filename[-4:].lower()!='.bgl':
                    continue
                bglname=join(path, filename)
                if bglname in self.done: continue
                self.done[bglname]=True
                self.status(i*100.0/n, bglname[len(self.fspath)+1:])
                try:
                    bgl=file(bglname, 'rb')
                except IOError:
                    self.log("Can't read \"%s\"" % bglname)
                    continue
                c=bgl.read(2)
                if len(c)!=2:
                    self.log("Can't read \"%s\"" % bglname)
                    continue                
                tmp=None
                (c,)=unpack('<H', c)
                if c&0xff00==0:
                    bgl.seek(122)
                    (spare2,)=unpack('<I',bgl.read(4))
                    if spare2:
                        # compressed
                        bgl.close()
                        tmp=join(gettempdir(), filename)
                        if platform!='win32':
                            compressed=bglname
                            # Wine can't handle non-ascii?
                            try:
                                bglname[len(self.fspath):].encode("ascii")
                            except:
                                compressed=join(gettempdir(), 'fs2xp1.bgl')
                                copyfile(bglname, compressed)
                                tmp=join(gettempdir(), 'fs2xp2.bgl')
                            helper(self.bglexe, compressed, tmp)
                            if compressed!=bglname: unlink(compressed)
                        else:
                            helper(self.bglexe, bglname, tmp)
                        if not exists(tmp):
                            self.log("Can't parse compressed file %s" % (
                                filename))
                            continue
                        bgl=file(tmp, 'rb')
                    try:
                        convbgl.Parse(bgl, bglname, self)
                    except:
                        self.log("Can't read \"%s\"" % filename)
                        if self.debug: print_exc(None, self.debug)
                elif c==0x201:
                    xmls.append(bglname)
                else:
                    self.log("Can't parse \"%s\". Is this a BGL file?" % (
                        filename))
                bgl.close()
                if tmp and exists(tmp) and not self.debug: unlink(tmp)

        # set up exclusions that affect facilities
        self.excfac=self.exc

        # Do airport facilities last so that exclusions have been set up
        for self.doingexcfac in [False, True]:
            n = len(xmls)
            for i in range(n):
                bglname=xmls[i]
                if not self.doingexcfac:
                    self.status(i*100.0/n, bglname[len(self.fspath)+1:])
                tmp=join(gettempdir(), basename(bglname[:-3])+'xml')
                x=helper(self.xmlexe, '-t', bglname, tmp)
                if exists(tmp):
                    try:
                        xmlfile=file(tmp, 'rU')
                        convxml.Parse(xmlfile, bglname, self)
                        xmlfile.close()
                        if not self.debug: unlink(tmp)
                    except FS2XError:
                        raise
                    except:
                        self.log("Can't parse file %s" % basename(bglname))
                        if self.debug: print_exc(None, self.debug)
                else:
                    self.log("Can't parse file %s" % basename(bglname))
                    if self.debug: self.debug.write("%s\nError: %s\n" % (bglname,x))
            if not self.doexcfac or self.doingexcfac or not self.needfull: break
            # Do them again, this time with exclusions
            self.aptfull=self.apt
            self.apt={}
            self.nav=[]


    # Process referenced library into self.objplc and self.objdat
    def proclibs(self):
        if self.dumplib:	# Fake up references
            for uid in self.libobj:
                self.objplc.append((None, 0, 1, uid, 1))

        if self.objplc:
            self.status(-1, 'Reading library objects')
            if self.debug: self.debug.write('Library objects\n')
        lasttexdir=None
        i=0
        while i<len(self.objplc):
            (loc, heading, complexity, uid, scale)=self.objplc[i]
            if uid in self.stock and not self.dumplib:
                name=self.stock[uid]
                if name in ignorestock:
                    self.objplc.pop(i)	# Silently drop ignored stock objects
                    continue
            elif not uid in self.libobj:
                i+=1
                continue	# Missing object error will be reported later
            else:
                (mdlformat, bglname, realfile, offset, size, name, libscale)=self.libobj[uid]
                
            # Replace uid with name
            self.objplc[i]=(loc, heading, complexity, name, scale)
            if name in self.objdat:
                i+=1
                continue	# Already got it

            # Substitue for stock objects
            if uid in self.stock and not (self.debug and self.dumplib):
                obj=makestock(name, self)
                if obj:
                    self.objdat[name]=[obj]
                # Missing object error will be reported later
                i+=1
                continue

            # Convert the library object
            filename=basename(bglname)
            if self.debug: self.debug.write('%s %s FS%s\n' % (bglname.encode("latin1", 'replace'), name, mdlformat))
            self.status(i*100.0/len(self.objplc), name)
            i+=1
            scen=None
            tran=None
            bgl=file(realfile, 'rb')
            bgl.seek(offset)
            if mdlformat==9:
                # New-style MDL file
                data=''
                bgldata=''
                tbldata=''
                try:
                    if bgl.read(4)!='RIFF': raise IOError
                    (mdlsize,)=unpack('<I', bgl.read(4))
                    if bgl.read(4)!='MDL9': raise IOError
                    while bgl.tell()<offset+mdlsize:
                        c=bgl.read(4)
                        (size,)=unpack('<I', bgl.read(4))
                        if c=='EXTE':
                            end=size+bgl.tell()
                            while bgl.tell()<end:
                                c=bgl.read(4)
                                (size,)=unpack('<I', bgl.read(4))
                                if c in ['TEXT','MATE','VERT']:
                                    data+=bgl.read(size-2)	# strip return
                                    if bgl.read(2)!='\x22\0':	raise IOError
                                elif c=='BGL ':
                                    bgldata+=bgl.read(size)
                                    bgldata+='\0\0'		# add EOF
                                elif c in ['TRAN', 'ANIP', 'ANIC', 'SCEN']:
                                    # Maintain offsets between ANIC and SCEN
                                    if c=='TRAN':
                                        tran=len(tbldata)+8
                                    elif c=='SCEN':
                                        scen=len(tbldata)+8
                                    tbldata+=pack('<I',size)+c+bgl.read(size)
                                else:
                                    bgl.seek(size,1)
                        else:
                            bgl.seek(size,1)
                    data+=bgldata
                    if not data:
                        if self.debug: self.debug.write('!No data\n')
                        continue
                    if scen: scen+=len(data)	# Offset from first instruction
                    if tran: tran+=len(data)	# Offset from first instruction
                    data+=tbldata	# Table data must be last
                except:
                    self.log("Can't parse object %s in file %s" % (
                        name, filename))
                    bgl.close()
                    if self.debug: print_exc(None, self.debug)
                    continue
                # Write a flat BGL section
                bgl.close()
                bgl=StringIO()
                bgl.write(data)
                bgl.seek(0)
                offset=0
                size=len(data)

            try:
                # Add library object to self.objdat
                texdir=normpath(join(dirname(bglname), pardir))
                # For case-sensitive filesystems
                for d in listdir(texdir):
                    if d.lower()=='texture':
                        if not lasttexdir or lasttexdir[0]!=texdir:
                            lasttexdir=maketexdict(join(texdir, d))
                        break
                else:
                    lasttexdir=None
                if mdlformat==10:
                    p=convmdl.ProcScen(bgl, offset+size, libscale, name, bglname, lasttexdir, self)
                else:
                    p=convbgl.ProcScen(bgl, offset+size, name, bglname, lasttexdir, self, scen, tran)
                if p.anim:
                    self.log("Skipping animation in object %s in file %s" % (name, filename))
                    if self.debug: self.debug.write("Animation\n")
                if p.old:
                    self.log("Skipping pre-FS2002 scenery in object %s in file %s" % (name, filename))

                    if self.debug: self.debug.write("Pre-FS2002\n")
                if p.rrt:
                    self.log("Skipping pre-FS2004 runways and/or roads in object %s in file %s" % (name, filename))
                    if self.debug: self.debug.write("Old-style rr\n")
            except:
                self.log("Can't parse object %s in file %s" % (name, filename))
                if self.debug: print_exc(None, self.debug)
            bgl.close()


    def export(self):
        divisions=32
        resolution=divisions*65535
        minres=1.0/resolution
        maxres=1-minres
        minhdg=360.0/65535

        if self.apt or self.nav or self.objplc or self.polyplc:
            if not isdir(self.xppath): mkdir(self.xppath)
        else:
            raise FS2XError('No data found!')
        
        # Check that apt entries contain runways - X-Plane crashes on stubs
        for i in self.apt.keys():
            for l in self.apt[i][1]:
                if l.code in range(100,103):
                    break		# ok
            else:
                self.apt.pop(i)		# No runway. Bye
            
        if not self.apt:
            if not self.dumplib:
                self.log("No airport definition found!")
        else:
            # attach beacons, windsocks and taxiways to corresponding airport
            for (code, loc, data) in self.misc:
                airport=None
                distance=16000
                # find airport with closest runway
                for k, (airloc, v) in self.apt.iteritems():
                    d=loc.distanceto(airloc)
                    if d<distance:
                        airport=k
                        distance=d
                if code==19:
                    name="windsock"
                elif code==18:
                    name="beacon"
                elif code==100:
                    name="runway"
                elif code==130:
                    name="boundary"
                else:
                    name="taxiway"
                if distance>=16000:	# X-Plane limit is 10 miles
                    self.log("Can't find an airport for %s at (%12.8f, %13.8f)" % (name, loc.lat, loc.lon))
                elif code==100:		# runway
                    # Find and update matching XML-defined runway
                    # Presence of a BGL-defined duplicate runway implies that
                    # the XML runway is at least partially hidden, so use BGL
                    # markings.
                    # Lighting can come from either XML (if not excluded) or
                    # BGL. If both, BGL takes precedence (arbitrarily).
                    d=data[0].text.split()
                    dheading=Point(float(d[8]),float(d[9])).headingto(Point(float(d[17]),float(d[18])))
                    lines=self.apt[airport][1]
                    #print loc, data
                    for i in range(len(lines)):
                        if not lines[i].code==100: continue
                        c=lines[i].text.split()
                        start=Point(float(c[8]),float(c[9]))
                        endpt=Point(float(c[17]),float(c[18]))
                        heading=start.headingto(endpt)
                        length=start.distanceto(endpt)
                        clen=(float(c[10])+length-float(c[19]))/2
                        cloc=start.biased(sin(radians(heading))*clen,
                                          cos(radians(heading))*clen)
                        #print cloc, lines[i], loc.distanceto(cloc)
                        # ignore designators, as often missing
                        if abs(dheading-heading)<1:
                            reverse=False
                        elif abs(dheading-(heading+180)%360)<1:
                            reverse=True
                        else:
                            continue
                        if (loc.distanceto(cloc)>float(c[0]) and
                            abs(dheading-Point(float(d[8]),float(d[9])).headingto(cloc))>1 or loc.distanceto(cloc)>length/5):
                            continue	# arbitrary - use len & width for fudge
                        # Just use BGL data if not transparent
                        if int(d[1])!=15:
                            self.visrunways=True	# Runways on top
                            lines[i]=data[0]
                            break
                        # If BGL data is transparent then assume XML is hidden
                        centrelights=int(d[4]) or int(c[4])
                        txt="%5.2f %02d %02d %4.2f %d %d %d" % (float(c[0]), 15, int(c[2]), float(c[3]), int(d[4]) or int(c[4]), int(d[5]) or int(c[5]), int(d[6]) or int(c[6]))
                        for end in [0,9]:
                            if reverse:
                                base=(9-end)
                            else:
                                base=end
                            # Dimensions from XML.
                            # Lights from either, BGL takes precedence
                            txt += " %-3s %12.8f %13.8f %5.1f %5.1f %02d %02d %d %d" % (
                            c[end + 7], float(c[end + 8]), float(c[end + 9]), float(c[end + 10]), float(c[end + 11]),
                            int(d[base + 12]), int(d[base + 13]) or int(c[end + 13]),
                            int(d[base + 14]) or int(c[end + 14]), int(d[base + 15]) or int(c[end + 15]))
                        lines[i].text=txt
                        break
                    else:
                        # If real surface, add new runway (after header)
                        if int(d[1])!=15:
                            self.visrunways=True	# Runways on top
                            self.apt[airport][1].insert(1,data[0])
                            if self.aptfull: self.aptfull[airport][1].insert(1,data[0])
                        else:
                            self.log("Can't find an airport for %s at (%12.8f, %13.8f)" % (name, loc.lat, loc.lon))
                            if self.debug: self.debug.write('Can\'t place runway "%s"\n' % data[0])
                elif code==110:
                    # Add taxiways and roads before aprons so overlay them
                    for i in range(len(self.apt[airport][1])):
                        if self.apt[airport][1][i].code>=110:
                            self.apt[airport]=(self.apt[airport][0],self.apt[airport][1][:i]+data+self.apt[airport][1][i:])
                            break
                    else:
                        self.apt[airport][1].extend(data)
                    if self.aptfull:
                        for i in range(len(self.aptfull[airport][1])):
                            if self.aptfull[airport][1][i].code>=110:
                                self.aptfull[airport]=(self.aptfull[airport][0],self.aptfull[airport][1][:i]+data+self.aptfull[airport][1][i:])
                                break
                        else:
                            self.aptfull[airport][1].extend(data)
                else:
                    # Add taxiways and roads before aprons so overlay them
                    for i in range(len(self.apt[airport][1])):
                        if self.apt[airport][1][i].code>code and self.apt[airport][1][i].code not in [21,100,101,102]:
                            self.apt[airport]=(self.apt[airport][0],self.apt[airport][1][:i]+data+self.apt[airport][1][i:])
                            break
                    else:
                        self.apt[airport][1].extend(data)
                    if self.aptfull:
                        for i in range(len(self.aptfull[airport][1])):
                            if self.aptfull[airport][1][i].code>code and self.aptfull[airport][1][i].code not in [21,100,101,102]:
                                self.aptfull[airport]=(self.aptfull[airport][0],self.aptfull[airport][1][:i]+data+self.aptfull[airport][1][i:])
                                break
                        else:
                            self.aptfull[airport][1].extend(data)

            # Export apt.dat
            path=join(self.xppath, 'Earth nav data')
            if not isdir(path): mkdir(path)
            for (filename, apt) in [(join(path, 'apt.dat'), self.apt), (join(path, 'fullapt.dat'), self.aptfull)]:
                if not apt: continue
                f=file(filename, 'wt')
                f.write("I\n%d\t# %s\n\n" % (self.doatc and 1000 or 850, banner))
                keys=apt.keys()
                keys.sort()
                for k in keys:
                    v=apt[k][1]
                    seabase=True
                    helibase=True
                    for l in v:
                        if l.code==100:
                            helibase=False
                            seabase=False
                        elif l.code==101:
                            helibase=False
                        elif l.code==102:
                            seabase=False
                    doneheader=False
                    last=0
                    for l in v:
                        if l.code==1:
                            # Only write one header
                            if not doneheader:
                                if seabase:
                                    l.code=16
                                elif helibase:
                                    l.code=17
                                f.write("%s\n" % l)
                            doneheader=True
                        elif l.code in [110,120,130,1000,1200,1300] or (l.code<110 <= last):
                            f.write("\n%s\n" % l)	# Hack - insert CR
                        elif l.code in [14,15] and last>=110:
                            f.write("\n%s\n" % l)	# Hack - insert CR
                        else:
                            f.write("%s\n" % l)
                        last=l.code
                    f.write("\n\n")
                f.write("99\n")	# eof marker
                f.close()
                    
        if self.nav:
            path=join(self.xppath, 'Earth nav data')
            if not isdir(path): mkdir(path)
            filename=join(path, 'nav.dat')
            f=file(filename, 'wt')
            f.write("I\n810\t# %s\n" % banner)
            self.nav.sort()
            for l in self.nav:
                f.write("%s\n" % l)
            f.close()

        if self.atc and self.doatc:
            path=join(self.xppath, 'Earth nav data')
            if not isdir(path): mkdir(path)
            filename=join(path, 'atc.dat')
            f=file(filename, 'wt')
            f.write("I\n1000\t# %sATCFILE\n\n" % banner)
            for icao, roles in self.atc.iteritems():
                for (name, role, freq) in roles:
                    f.write('CONTROLLER\nNAME %s\nFACILITY_ID %s\nICAO %s\nROLE %s\nFREQ %5d\nVOICE_DEF lib/atc/voices/default.voc\nCONTROLLER_END\n\n' %
                            (name, icao, icao, role, float(freq)*100))
                f.write('\n')
            f.close()

        self.status(-1, 'Writing OBJs')
        # make a list of requested objects and scales
        objdef={}
        for loc, heading, complexity, name, scale in self.objplc:
            if not name in objdef:
                objdef[name]=[scale]
            elif not scale in objdef[name]:
                objdef[name].append(scale)
        polydef={}
        for (name, param, points) in self.polyplc:
            if not name in polydef:
                polydef[name]=True

        # do layer mapping
        # In FSX any layer overwrites runways and taxiways. layer>=16 also overwrites markings and lights.
        # We have to map these to 8 X-Plane layers below markings and 8 above.
        # In X-Plane 9, polygons with surface at layer airports+1 or later also suppresses lights. But not in X-Plane 10.
        # Note: In X-Plane 10.20, airports layer doesn't work for draped objs
        fslayers={}
        for name in objdef:
            if name in self.objdat:
                for obj in self.objdat[name]:
                    if obj.layer: fslayers[obj.layer]=None
        for name in polydef:
            if name in self.polydat:
                poly=self.polydat[name]
                if poly.layer: fslayers[poly.layer]=None
        lokeys=sorted([key for key in fslayers.keys() if 4<=key<16])
        hikeys=sorted([key for key in fslayers.keys() if key>=16])
        for (keys, mapping) in [(lokeys, ['runways +1', 'runways +2', 'runways +3', 'runways +4', 'runways +5', 'markings -5', 'markings -4', 'markings -3', 'markings -2', 'markings -1']),
                                (hikeys, ['roads +1', 'roads +2', 'roads +3', 'roads +4', 'roads +5', 'objects -5', 'objects -4', 'objects -3', 'objects -2', 'objects -1'])]:
            divisor=(len(keys)+7)/8	# have to map to 8 values
            for i in range(len(keys)):
                fslayers[keys[i]]=mapping[i/divisor]
            fslayers[0]='terrain +1'	# for FS2004 photoscenery
            fslayers[1]='terrain +2'	# for Blue Sky photoscenery
            fslayers[2]='terrain +3'	#  "
            fslayers[3]='terrain +4'	#  "
        if __debug__:
            if fslayers and self.debug:
                self.debug.write("\nLayer mapping:\n")
                for key in sorted(fslayers.keys()):
                    self.debug.write("%02d -> %s\n" % (key, fslayers[key]))
                self.debug.write("\n")

        # write out objects
        keys=objdef.keys()
        sortfolded(keys)
        n = len(keys)+len(self.polydat)
        i = 0
        for name in keys:
            if name in self.objdat:
                self.status(i*100.0/n, name)
                for scale in objdef[name]:
                    for obj in self.objdat[name]:
                        obj.export(scale, self, fslayers)
            elif name in self.stock.values():
                self.log('Object %s is a built-in object' % name)
            elif '/' not in name:	# Not substituted library object
                self.log('Object %s not found' % name)
            elif name.startswith('opensceneryx/'):
                self.usesopensceneryx=True
            i+=1
        keys=self.polydat.keys()
        sortfolded(keys)
        for name in keys:
            self.status(i*100.0/n, name)
            self.polydat[name].export(self, fslayers)
            i+=1

        if self.dumplib:
            return

        if self.usesopensceneryx:
            self.log('Using objects from the OpenSceneryX library')
            copyfile(join('Resources','opensceneryx_library.txt'), join(self.xppath, 'library.txt'))
            mkdir(join(self.xppath,'opensceneryx'))
            for filename in listdir('Resources'):
                if splitext(filename)[0]=='placeholder':
                    copyfile(join('Resources',filename), join(self.xppath,'opensceneryx',filename))

        # copy readmes
        for path, dirs, files in walk(self.fspath):
            for filename in files:
                (s,e)=splitext(filename)
                if e.lower() in ['.htm', '.html', '.rtf', '.doc', '.pdf', '.jpg', '.jpeg']:
                    copyfile(join(path, filename),
                             join(self.xppath, filename))
                else:
                    for f in ['readme', 'read me',	# en
                              'leggime', 'leggi me'	# it
                              'leeeme', 'leee me',	# sp
                              'lisezmoi', 'lisez moi']:	# fr
                        if f in filename.lower():
                            copyfile(join(path, filename),
                                     join(self.xppath, filename))
                        
        
        self.status(-1, 'Writing DSFs')
        cmplx={}
        for loc, heading, complexity, name, scale in self.objplc:
            tile=(int(floor(loc.lat)), int(floor(loc.lon)))
            key=(name,scale)
            if not cmplx.has_key(tile):
                cmplx[tile]={}
            if not cmplx[tile].has_key(key) or cmplx[tile][key]>complexity:
                cmplx[tile][key]=complexity

        #expand names & create indices & create per-complexity placements
        objdef={}	# filenames (maybe more than one per Object)
        objplc={}	# number and location
        objlookup={}	# lists of indices into objdef
        polydef={}	# filename
        polyplc={}	# number and data
        polylookup={}	# lists of indices into polydef
        for loc, heading, c, name, scale in self.objplc:
            tile=(int(floor(loc.lat)), int(floor(loc.lon)))
            key=(name,scale)
            complexity=cmplx[tile][(name,scale)]
            if not tile in objdef:
                objdef[tile]=[[] for i in range(complexities)]
                objplc[tile]=[[] for i in range(complexities)]
                objlookup[tile]={}
                polydef[tile]=[]
                polyplc[tile]=[]

            if not key in objlookup[tile]:
                # Object not in objdef yet
                thisobjdef=objdef[tile][complexity]
                if '/' in name:		# Substituted library object
                    objlookup[tile][key]=[len(thisobjdef)]
                    thisobjdef.append(name)
                elif name in self.objdat:
                    # Must only add objs that exist
                    idx=[]
                    for obj in self.objdat[name]:
                        idx.append(len(thisobjdef))
                        thisobjdef.append("objects/" + obj.filename(scale))
                    objlookup[tile][key]=idx
                else:
                    continue

            base=objlookup[tile][key][0]
            for i in objlookup[tile][key]:
                objplc[tile][complexity].append((i,loc.lon,loc.lat,heading))

        for (name, heading, points) in self.polyplc:
            tile=(int(floor(points[0][0][0].lat)), int(floor(points[0][0][0].lon)))
            if not tile in polydef:
                objdef[tile]=[[] for i in range(complexities)]
                objplc[tile]=[[] for i in range(complexities)]
                polydef[tile]=[]
                polyplc[tile]=[]

            if '/' in name:		# Substituted library object
                fname=name
            else:
                fname="objects/"+self.polydat[name].filename()
            if not fname in polydef[tile]:
                polyplc[tile].append((len(polydef[tile]),heading,points))
                polydef[tile].append(fname)
            else:
                polyplc[tile].append((polydef[tile].index(fname),heading,points))

        tiles=objdef.keys()
        n = len(tiles)
        t = 0
        for tile in tiles:
            (lat,lon)=tile
            sw=Point(lat,lon)
            ne=Point(sw.lat+1,sw.lon+1)
            objdefs=objdef[tile]
            objplcs=objplc[tile]
            polydefs=polydef[tile]
            polyplcs=polyplc[tile]
            tilename="%+03d%+04d" % (lat,lon)
            tiledir=join("Earth nav data", "%+02d0%+03d0" % (
                int(lat/10), int(lon/10)))
            self.status(t*100.0/n, tilename+'.dsf')
            t+=1
            objcount=0

            # Caculate base index for each complexity. Highest are first.
            base=[[] for i in range(complexities)]
            for i in range(complexities-1,-1,-1):
                number=objcount
                for j in range(i+1, complexities):
                    number+=len(objdefs[j])
                base[i]=number

            path=join(self.xppath, 'Earth nav data')
            if not isdir(path): mkdir(path)
            path=join(self.xppath, tiledir)
            if not isdir(path): mkdir(path)
            dstname=join(path, tilename+'.txt')
            dst=file(dstname, 'wt')

            dst.write('I\n800\nDSF2TEXT\n\n')
            dst.write('PROPERTY sim/planet\tearth\n')
            dst.write('PROPERTY sim/overlay\t1\n')
            if self.docomplexity:
                for i in range(complexities):
                    if len(objdefs[i]):
                        dst.write('PROPERTY sim/require_object\t%d/%d\n'% (
                            i+1, base[i]))
                dst.write('PROPERTY sim/require_polygon\t1/0\n')
            else:
                dst.write('PROPERTY sim/require_object\t1/0\n')
                dst.write('PROPERTY sim/require_polygon\t1/0\n')
            for exc in self.exc:
                (typ, bl,tr)=exc
                if bl.within(sw,ne) or tr.within(sw,ne):
                    dst.write('PROPERTY sim/exclude_%s\t%13.8f/%12.8f/%13.8f/%12.8f\n' % (typ, bl.lon,bl.lat, tr.lon,tr.lat))
            dst.write('PROPERTY sim/creation_agent\t%s' % banner)
            # Following must be the last properties
            dst.write('PROPERTY sim/west\t%d\n' %  sw.lon)
            dst.write('PROPERTY sim/east\t%d\n' %  ne.lon)
            dst.write('PROPERTY sim/north\t%d\n' %  ne.lat)
            dst.write('PROPERTY sim/south\t%d\n' %  sw.lat)
            dst.write('\n')
            dst.write('DIVISIONS\t%d\n' % divisions)
            dst.write('\n')

            for i in range(complexities-1,-1,-1):
                for name in objdefs[i]:
                    dst.write('OBJECT_DEF %s\n' % name)
            dst.write('\n')

            for name in polydefs:
                dst.write('POLYGON_DEF %s\n' % name)
            if polydefs: dst.write('\n')

            for i in range(complexities-1,-1,-1):
                for plc in objplcs[i]:
                    (idx,lon,lat,heading)=plc
                    # DSFTool<=2.0 rounds down rather than to nearest encodable value, so round up here first
                    dst.write('OBJECT %3d %14.9f %14.9f %6.2f\n' % (base[i]+idx, min(ne.lon, lon+minres/4), min(ne.lat, lat+minres/4), (heading+minhdg/4)%360))
            dst.write('\n')

            for (idx,heading,poly) in polyplcs:
                dst.write('BEGIN_POLYGON %d %d %d\n' % (idx, heading, heading==65535 and 4 or 2))
                for w in poly:
                    dst.write('BEGIN_WINDING\n')
                    for p in w:
                        if heading==65535:	# have UVs
                            dst.write('POLYGON_POINT %14.9f %14.9f %8.4f %8.4f\n' % (min(ne.lon, p[0].lon+minres/4), min(ne.lat, p[0].lat+minres/4), p[1], p[2]))
                        else:
                            dst.write('POLYGON_POINT %14.9f %14.9f\n' % (min(ne.lon, p[0].lon+minres/4), min(ne.lat, p[0].lat+minres/4)))
                    dst.write('END_WINDING\n')
                dst.write('END_POLYGON\n')
            if polyplcs: dst.write('\n')

            dst.close()
            dsfname=join(path, tilename+'.dsf')
            x=helper(self.dsfexe, '-text2dsf', dstname, dsfname)
            if not exists(dsfname):
                raise FS2XError("Can't write DSF %s.dsf\n%s" % (tilename, x))
            if not self.debug: unlink(dstname)


    # Should taxiway node be suppressed?
    def excluded(self, p):
        for (typ, sw, ne) in self.excfac:
            if sw.lat <= p.lat <= ne.lat and sw.lon <= p.lon <= ne.lon:
                self.needfull=True
                if self.debug: self.debug.write("Excluded: %s\n" % p)
                return self.doexcfac
        return False

