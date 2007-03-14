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

from math import floor
from os import curdir, mkdir, pardir, sep, stat, unlink, walk
from os.path import basename, exists, isdir, join, normpath, splitext
from shutil import copyfile
from StringIO import StringIO
import struct	# for struct.error
from struct import pack, unpack
from sys import exit, platform
from tempfile import gettempdir

from convutil import banner, helper, complexities, AptNav, Object, Point, FS2XError
from convobjs import makestock
import convbgl
import convxml

class Output:
    def __init__(self, mypath, fspath, lbpath, xppath, season, status, log,
                 dumplib, debug):

        self.dumplib=dumplib
        self.debug=debug
        self.overlays=True
        self.docomplexity=False

        if dumplib:
            self.fspath=None
            self.lbpath=fspath
        else:
            self.fspath=fspath
            self.lbpath=lbpath
        self.xppath=xppath
        self.hemi=0	# 0=N, 1=S
        self.season=season

        # Callbacks
        self.status=status
        self.log=log

        self.apt={}
        self.nav=[]
        self.misc=[]
        self.done={}	# BGL files that we've already processed
        self.exc=[]	# Exclusion rectangles: (type, bottomleft, topright)
        self.libobj={}	# Lib objects: (MDL, f, cmp, offset, size, name) by uid
        self.objplc=[]	# Object placements:	(loc, hdg, cmplx, name, scale)
        self.objdat={}	# Objects by name
        self.stock={}	# FS2004 stock objects - we don't have these
        self.haze={}	# Textures that have palette-based transparency
        self.dufftex={}	# Textures we couldn't convert (avoid multiple reports)
        
        if platform=='win32':
            self.bglexe=curdir+sep+platform+sep+'bglunzip.exe'
            self.xmlexe=curdir+sep+platform+sep+'bglxml.exe'
            self.pngexe=curdir+sep+platform+sep+'bmp2png.exe'
            self.dsfexe=curdir+sep+'DSFTool.exe'
        elif platform.lower().startswith('linux'):
            self.bglexe=curdir+sep+'linux'+sep+'bglunzip'
            self.xmlexe=curdir+sep+'linux'+sep+'bglxml'
            self.pngexe=curdir+sep+'linux'+sep+'bmp2png'
            self.dsfexe=curdir+sep+'linux'+sep+'DSFTool'
        else:	# Mac
            self.bglexe=None	# Not available on Mac
            self.xmlexe=curdir+sep+'mac'+sep+'bglxml'
            self.pngexe=curdir+sep+'mac'+sep+'bmp2png'
            self.dsfexe=curdir+sep+'DSFTool'

        for path in [fspath, lbpath]:
            if path and not exists(path):
                raise FS2XError('"%s" does not exist' % path)
            if path and not isdir(path):
                raise FS2XError('"%s" is not a folder' % path)
        path=normpath(join(xppath, pardir))
        if basename(path).lower()!='custom scenery' or not isdir(path):
            raise FS2XError('"%s" is not a sub-folder of "Custom Scenery"' % (
                xppath))
        for path, dirs, files in walk(xppath):
            if (dirs or files) and files!=['errors.txt']:
                raise FS2XError('"%s" is not empty' % xppath)

        for exe in [self.bglexe, self.xmlexe, self.pngexe, self.dsfexe]:
            if exe and not exists(exe):
            	raise FS2XError("Can't find \"%s\"" % exe)

        if platform.lower().startswith('linux'):
            # check for win32 executables under wine
            for exe in [curdir+sep+'DSFTool.exe',
                        curdir+sep+'win32'+sep+'bglunzip.exe']:
                if not exists(exe):
                    raise FS2XError("Can't find \"%s\"" % exe)

        path=join(mypath, 'objfile.txt')
        try:
            stock=file(path, 'rU')
        except IOError:
            raise FS2XError("Can't read \"%s\"." % path)
        for line in stock:
            if line[0]!=';':
                l=line.find(',')
                if l!=-1:
                    self.stock[line[:l].strip()]=line[l+1:].strip()
        stock.close()
        if self.debug and not isdir(self.xppath): mkdir(self.xppath)


    # Fill out self.libobj
    def scanlibs(self):
        self.status(-1, 'Scanning libraries')
        for toppath in [self.lbpath, self.fspath]:
            if not toppath:
                continue
            for path, dirs, files in walk(toppath):
                if basename(path).lower()!='scenery':
                    continue	# Only look at BGLs in 'scenery' directory
                n = len(files)
                for i in range(n):
                    filename=files[i]
                    if filename[-4:].lower()!='.bgl':
                        continue
                    bglname=join(path, filename)
                    if stat(bglname).st_size==0:
                        self.done[bglname]=True
                        continue	# Sometimes seen 0-length files!
                    try:
                        bgl=file(bglname, 'rb')
                    except IOError:
                        self.log("Can't read \"%s\"" % bglname)
                        self.done[bglname]=True
                        continue
                    c=bgl.read(2)
                    if len(c)!=2:
                        self.log("Can't read \"%s\"" % bglname)
                        self.done[bglname]=True
                        continue
                    done=True
                    (c,)=unpack('<H', c)
                    if c&0xff00==0:
                        for section in [42,54,58,102,114]:
                            bgl.seek(section)
                            (secbase,)=unpack('<I',bgl.read(4))
                            if secbase:
                                done=False
                        bgl.seek(62)	# LIBRARY data
                        (secbase,)=unpack('<I',bgl.read(4))
                        if not secbase:
                            continue
                        self.status(i*100.0/n, bglname[len(toppath)+1:])
                        tmp=bglname
                        bgl.seek(122)
                        (spare2,)=unpack('<I',bgl.read(4))
                        if spare2:
                            bgl.close()
                            if not self.bglexe:
                                self.log("Can't parse compressed file %s" % (
                                    filename))
                                # don't mark as done
                                continue
                            tmp=join(gettempdir(), filename)
                            helper('%s "%s" "%s"' %(self.bglexe, bglname, tmp))
                            if not exists(tmp):
                                self.log("Can't parse compressed file %s" % (
                                    filename))
                                continue
                            bgl=file(tmp, 'rb')
                        bgl.seek(secbase)
                        while 1:
                            pos=bgl.tell()
                            (off,)=unpack('<I', bgl.read(4))
                            if off==0:
                                break
                            bgl.seek(secbase+off)
                            (a,b,c,d,x,hdsize,size)=unpack('<IIIIBII',
                                                           bgl.read(25))
                            uid = "%08x%08x%08x%08x" % (a,b,c,d)
                            if hdsize>42:
                                # Use "friendly" name instead of id
                                bgl.seek(16,1)
                                name=bgl.read(hdsize-(41)).rstrip(' \0')
                            else:
                                name=uid
                            if not uid in self.libobj:	# 1st wins
                                self.libobj[uid]=(False, bglname, tmp,
                                                  secbase+off+hdsize, size,
                                                  name)
                            bgl.seek(pos+20)

                    elif c==0x201:
                        islib=False
                        bgl.seek(4)
                        (sectiontbl,)=unpack('<I',bgl.read(4))
                        bgl.seek(20)
                        (sections,)=unpack('<I',bgl.read(4))
                        for section in range(sections):
                            bgl.seek(sectiontbl+20*section)
                            (typ,x,subsections,subsectiontbl)=unpack('<IIIi', bgl.read(16))
                            if typ!=0x2b:	# 2b=MDL data
                                done=False
                                continue
                            if not islib:
                                self.status(i*100.0/n,bglname[len(toppath)+1:])
                                islib=True
                            for subsection in range(subsections):
                                bgl.seek(subsectiontbl+16*subsection)
                                (id,records,recordtbl)=unpack('<IIi',
                                                              bgl.read(12))
                                bgl.seek(recordtbl)
                                for record in range(records):
                                    (a,b,c,d,off,size)=unpack('<IIIIiI',
                                                              bgl.read(24))
                                    uid = "%08x%08x%08x%08x" % (a,b,c,d)
                                    if uid in self.stock:
                                        name=self.stock[uid]
                                    else:
                                        # No friendly name - always use id
                                        name=uid
                                    if not uid in self.libobj:
                                        self.libobj[uid]=(True,
                                                          bglname, bglname,
                                                          recordtbl+off, size,
                                                          name)
                    else:
                        self.log("Can't parse file \"%s\". Is this a BGL file?" % filename)
                    bgl.close()
                    if done:
                        self.done[bglname]=True


    # Fill out self.objplc and self.objdat
    def process(self):
        if self.dumplib: return
        
        self.status(-1, 'Reading BGLs')
        for path, dirs, files in walk(self.fspath):
            if basename(path).lower()!='scenery':
                continue	# Only look at BGLs in 'scenery' directory
            n = len(files)
            for i in range(n):
                filename=files[i]
                if filename[-4:].lower()!='.bgl':
                    continue
                bglname=join(path, filename)
                if bglname in self.done:
                    continue
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
                        bgl.close()
                        if not self.bglexe:
                            self.log("Can't parse compressed file %s" % (
                                filename))
                            continue
                        tmp=join(gettempdir(), filename)
                        helper('%s "%s" "%s"' % (self.bglexe, bglname, tmp))
                        if not exists(tmp):
                            self.log("Can't parse compressed file %s" % (
                                filename))
                            continue
                        bgl=file(tmp, 'rb')
                    convbgl.Parse(bgl, bglname, self)
                elif c==0x201:
                    tmp=join(gettempdir(), filename[:-3]+'xml')
                    x=helper('%s -t "%s" "%s"' % (self.xmlexe, bglname, tmp))
                    if not x and exists(tmp):
                        try:
                            xmlfile=file(tmp, 'rU')
                        except IOError:
                            self.log("Can't parse file %s" % filename)
                        convxml.Parse(xmlfile, bglname, self)
                        xmlfile.close()
                    else:
                        self.log("Can't parse file %s (%s)" % (filename, x))
                else:
                    self.log("Can't parse \"%s\". Is this a BGL file?" % (
                        filename))
                bgl.close()
                if tmp and exists(tmp): unlink(tmp)


    # Process referenced library into self.objplc and self.objdat
    def proclibs(self):
        if self.dumplib:	# Fake up references
            for uid in self.libobj:
                self.objplc.append((None, 0, 1, uid, 1))
        
        self.status(-1, 'Reading library objects')
        n=len(self.objplc)
        i=0
        for i in range(n):
            (loc, heading, complexity, uid, scale)=self.objplc[i]
            if uid in self.objdat: continue	# Already got it
            if uid in self.stock:
                name=self.stock[uid]
                # Replace uid with name
                self.objplc[i]=(loc, heading, complexity, name, scale)
                if name in self.objdat: continue	# Already got it
                # Ensure that the user doesn't inadvertantly convert MS objects
                if not self.dumplib:
                    self.log('Object %s is a built-in object (%s)' %(uid,name))
                    self.objdat[name]=[makestock(self, uid, name)]
                    continue

            if not uid in self.libobj:
                continue	# Missing object error will be reported later
            (mdl, bglname, realfile, offset, size, name)=self.libobj[uid]
            # Replace uid with name
            self.objplc[i]=(loc, heading, complexity, name, scale)
            if name in self.objdat: continue	# Already got it

            filename=basename(bglname)
            self.status(i*100.0/n, name)
            scen=None
            tran=None
            bgl=file(realfile, 'rb')
            bgl.seek(offset)
            if mdl:
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
                    if not data: raise IOError
                    if scen: scen+=len(data)	# Offset from first instruction
                    if tran: tran+=len(data)	# Offset from first instruction
                    data+=tbldata	# Table data must be last
                except (IOError, struct.error):
                    self.log("Can't parse object %s in file %s" % (
                        name, filename))
                    bgl.close()
                    continue
                # Write a flat BGL section
                bgl.close()
                bgl=StringIO()
                bgl.write(data)
                bgl.seek(0)
                offset=0
                size=len(data)

            if self.debug:
                debug=file(join(self.xppath,'debug.txt'),'at')
                debug.write('%s\n' % bglname)
            else:
                debug=None

            try:
                # Add library object to self.objdat
                p=convbgl.ProcScen(bgl, offset+size, name, bglname,
                                   self, scen, tran, debug)
                if p.anim:
                    self.log("Skipping animation in object %s in file %s" % (
                        name, filename))
                    if debug: debug.write("Animation\n")
                if p.old:
                    self.log("Skipping pre-FS2002 scenery in object %s in file %s" % (name, filename))

                    if debug: debug.write("Pre-FS2002\n")
                if p.rrt:
                    self.log("Skipping pre-FS2004 runways and/or roads in object %s in file %s" % (name, filename))
                    if debug: debug.write("Old-style rr\n")
            except struct.error:
                self.log("Can't parse object %s in file %s" % (name, filename))
                if debug: debug.write("!Parse error")
            bgl.close()


    def export(self):
        if self.apt or self.nav or self.objplc:
            if not isdir(self.xppath): mkdir(self.xppath)
        else:
            raise FS2XError('No data found!')

        # Check that apt entries contain runways - X-Plane crashes on stubs
        for k in sorted(self.apt):
            v=self.apt[k]
            for l in v:
                if l.code==10 and (l.text[0].isdigit() or l.text[0]=='H'):
                    break	# ok
            else:
                self.apt.pop(k)	# No runway. Bye
            
        if not self.apt:
            if not self.dumplib:
                self.log("No airport definition found!")
        else:
            # attach beacons and windsocks to corresponding airport
            for (code, loc, data) in self.misc:
                airport=None
                distance=16000
                # find airport with closest runway
                for k, v in self.apt.iteritems():
                    for l in v:
                        if l.code==10:
                            d=loc.distanceto(l.loc)
                            if d<distance:
                                airport=k
                                distance=d
                if code==19:
                    name="windsock"
                elif code==18:
                    name="beacon"
                elif code==10:
                    name="taxiway"
                else:
                    continue	# wtf?
                if distance==16000:	# X-Plane limit is 10 miles
                    self.log("Can't find an airport for %s at (%10.6f, %11.6f)" % (name, loc.lat, loc.lon))
                elif code==10:
                    self.apt[airport].append(AptNav(code, loc, data))
                else:
                    self.apt[airport].append(AptNav(code, loc, "%6d %s %s" % (
                        data, airport, name)))

            # Export apt.dat
            path=join(self.xppath, 'Earth nav data')
            if not isdir(path): mkdir(path)
            filename=join(path, 'apt.dat')
            f=file(filename, 'wt')
            f.write("I\n810\t# %s\n" % banner)
            for k in sorted(self.apt):
                v=self.apt[k]
                v.sort()
                helibase=True	# Should do the same for seaplane bases
                for l in v:
                    if l.code==10 and l.text[0].isdigit():
                        helibase=False
                        break
                doneheader=False
                for l in v:
                    if l.code==1:
                        # Only write one header
                        if not doneheader:
                            if helibase: l.code=17
                            f.write("%s\n" % l)
                        doneheader=True
                    else:
                        f.write("%s\n" % l)
                f.write("\n")
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


        self.status(-1, 'Writing OBJs')
        # make a list of requested objects and scales
        objdef={}
        for loc, heading, complexity, name, scale in self.objplc:
            if not name in objdef:
                objdef[name]=[scale]
            elif not scale in objdef[name]:
                objdef[name].append(scale)
                
        # write out objects
        n = len(objdef)
        i = 0
        for name in sorted(objdef):
            if name in self.objdat:
                self.status(i*100.0/n, name)
                for scale in objdef[name]:
                    count=1
                    for obj in self.objdat[name]:
                        obj.export(scale, self)
            else:
                self.log('Object %s not found' % name)
            i+=1

        if self.dumplib:
            return

        # copy readmes
        for path, dirs, files in walk(self.fspath):
            for filename in files:
                (s,e)=splitext(filename)
                if e.lower() in ['.htm', '.html', '.rtf', '.doc', '.pdf']:
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
        # poly_os objects need to be drawn first to prevent them from
        # swallowing other objects.
        # X-Plane 8.20 and 8.30 draw in order of definition (not placement)
        # in the DSF file. We therefore need poly_os objects to be defined
        # first. This is incompatible with prioritisation, since lower
        # priority objects come last. So disable prioritisation.
        cmplx={}
        for loc, heading, complexity, name, scale in self.objplc:
            tile=(int(floor(loc.lat)), int(floor(loc.lon)))
            key=(name,scale)
            if self.docomplexity:
                newc=complexity
            else:
                newc=1				# Disable prioritisation
                if name in self.objdat:
                    for obj in self.objdat[name]:
                        if obj.poly:
                            newc=complexities-1	# ... apart from for poly_os
            if not cmplx.has_key(tile):
                cmplx[tile]={}
            if (not cmplx[tile].has_key(key) or
                cmplx[tile][key]>newc):
                cmplx[tile][key]=newc

        #expand names & create indices & create per-complexity placements
        objdef={}	# filenames (maybe more than one per Object)
        objplc={}	# number and location
        lookup={}	# lists of indices into objdef
        for loc, head, c, name, scale in self.objplc:
            tile=(int(floor(loc.lat)), int(floor(loc.lon)))
            key=(name,scale)
            complexity=cmplx[tile][(name,scale)]
            if not objdef.has_key(tile):
                objdef[tile]=[[] for i in range(complexities)]
                objplc[tile]=[[] for i in range(complexities)]
                lookup[tile]={}

            if not key in lookup[tile]:
                # Object not in objdef yet
                thisobjdef=objdef[tile][complexity]
                idx=[]
                if self.objdat.has_key(name):
                    # Must only add objs that exist
                    for obj in self.objdat[name]:
                        idx.append(len(thisobjdef))
                        if scale!=1.0:
                            thisobjdef.append("%s_%02d%02d.obj" % (obj.filename[:-4], int(scale), round(scale*100,0)%100))
                        else:
                            thisobjdef.append(obj.filename)
                    lookup[tile][key]=idx
                else:
                    continue

            base=lookup[tile][key][0]
            for i in lookup[tile][key]:
                objplc[tile][complexity].append((i,loc.lon,loc.lat,head))

        # Translate DSF
        srcpath=normpath(join(self.xppath, pardir, pardir,
                              "Resources", "default scenery", "DSF 820 Earth"))

        n = len(objdef.keys())
        t = 0
        for tile in objdef.keys():
            (lat,lon)=tile
            sw=Point(lat,lon)
            ne=Point(sw.lat+1,sw.lon+1)
            defs=objdef[tile]
            plcs=objplc[tile]
            tilename="%+03d%+04d" % (lat,lon)
            tiledir=join("Earth nav data", "%+02d0%+03d0" % (
                int(lat/10), int(lon/10)))
            self.status(t*100.0/n, tilename+'.dsf')
            t+=1
    
            if self.overlays:
                objcount=0
            else:
                srcname=join(srcpath, tiledir, tilename+'.dsf')
                dsfname=join(gettempdir(), tilename+'.txt')
                if not exists(srcname):
                    raise FS2XError("Can't read source DSF %s.dsf"%(tilename))
                x=helper(self.dsfexe+' -dsf2text "'+srcname+'" "'+dsfname+'"')
                if x or not exists(dsfname):
                    raise FS2XError("Can't read source DSF %s.dsf (%s)" %
                                    (tilename, x))
                dsf=file(dsfname, 'rU')
                objcount=0
                for line in dsf:
                    if line.find("PROPERTY sim/require_object")==0:
                        pass
                    elif line.find("OBJECT_DEF ")==0:
                        objcount+=1
                    elif line.find("# Result code: ")==0:
                        if int(line[15:])!=0:
                            raise FS2XError("Can't read source DSF %s.dsf" % (
                                tilename))

            # Caculate base index for each complexity. Highest are first.
            base=[[] for i in range(complexities)]
            for i in range(complexities-1,-1,-1):
                number=objcount
                for j in range(i+1, complexities):
                    number+=len(defs[j])
                base[i]=number

            path=join(self.xppath, 'Earth nav data')
            if not isdir(path): mkdir(path)
            path=join(self.xppath, tiledir)
            if not isdir(path): mkdir(path)
            dstname=join(path, tilename+'.txt')
            dst=file(dstname, 'wt')

            if self.overlays:
                dst.write('I\n800\nDSF2TEXT\n\n')
                dst.write('PROPERTY sim/overlay\t1\n')
                dst.write('PROPERTY sim/planet\tearth\n')
                if self.docomplexity:
                    for i in range(complexities-1,-1,-1):
                        if len(defs[i]):
                            dst.write('PROPERTY sim/require_object\t%d/%d\n'% (
                                i+1, base[i]))
                else:
                    dst.write('PROPERTY sim/require_object\t1/0\n')
                for exc in self.exc:
                    (typ, bl,tr)=exc
                    if bl.within(sw,ne) or tr.within(sw,ne):
                        dst.write('PROPERTY sim/exclude_%s\t%11.6f,%10.6f,%11.6f,%10.6f\n' % (typ, bl.lon,bl.lat, tr.lon,tr.lat))
                # XXX flattening?
                dst.write('PROPERTY sim/creation_agent\t%s' % banner)
                # Following must be the last properties
                dst.write('PROPERTY sim/west\t%d\n' %  sw.lon)
                dst.write('PROPERTY sim/east\t%d\n' %  ne.lon)
                dst.write('PROPERTY sim/north\t%d\n' %  ne.lat)
                dst.write('PROPERTY sim/south\t%d\n' %  sw.lat)
                dst.write('\n')

                for i in range(complexities-1,-1,-1):
                    for name in defs[i]:
                        dst.write('OBJECT_DEF objects/%s\n' % name)
                dst.write('\n')

                for i in range(complexities-1,-1,-1):
                    for plc in plcs[i]:
                        (idx,lon,lat,heading)=plc
                        dst.write('OBJECT %3d %11.6f %10.6f %6.2f\n' % (
                            base[i]+idx, lon, lat, heading))
                dst.write('\n')
                
            else:	# !overlays
                state=0
                dsf.seek(0)
                for line in dsf:
                    if state==0:	# waiting for PROPERTY
                        if line.find('PROPERTY ')==0:
                            dst.write('# Added by FS2XPlane:\n')
                            for i in range(complexities-1,-1,-1):
                                if len(defs[i]):
                                    dst.write('PROPERTY sim/require_object %d/%d\n' % (i+1, base[i]))
                            state=1
                        else:
                            dst.write(line)
                    if state==1:	# waiting for non-PROPERTY
                        if line.find('PROPERTY ')!=0:
                            if objcount:
                                state=2
                            else:
                                state=3
                        elif line.find('PROPERTY sim/require_object')!=0:
                            dst.write(line)

                    if state==2:	# waiting for OBJECT_DEF
                        if line.find('OBJECT_DEF ')==0:
                            state=3
                        else:
                            dst.write(line)
                    if state==3:	# waiting for non-OBJECT_DEF
                        if line.find('OBJECT_DEF ')!=0:
                            dst.write('# Added by FS2XPlane:\n')
                            for i in range(complexities-1,-1,-1):
                                for name in defs[i]:
                                    dst.write('OBJECT_DEF objects/%s\n' % name)
                            if objcount:
                                state=4
                            else:
                                state=5
                        else:
                            dst.write(line)

                    if state==4:	# waiting for OBJECT
                        if line.find('OBJECT ')==0:
                            state=5
                        else:
                            dst.write(line)

                    if state==5:	# waiting for non-OBJECT
                        if line.find('OBJECT ')!=0:
                            dst.write('# Added by FS2XPlane:\n')
                            for i in range(complexities-1,-1,-1):
                                for plc in plcs[i]:
                                    (idx,lon,lat,heading)=plc
                                    dst.write('OBJECT %3d %11.6f %10.6f %7.3f\n'%(base[i]+idx, lon, lat, heading))
                            state=6
                        else:
                            args=line[7:].split()
                            loc=Point(float(args[2]), float(args[1]))
                            for exc in self.exc:
                                (bl,tr)=exc
                                if loc.within(bl,tr):
                                    dst.write('# Excluded by FS2XPlane: '+line)
                                    break
                                else:
                                    dst.write(line)

                    if state==6:	# copy to end
                        if line.find('# Result code: ')!=0:
                            dst.write(line)
                dsf.close()
                unlink(dsfname)
                    
            dst.close()
            dsfname=join(path, tilename+'.dsf')
            x=helper('%s -text2dsf "%s" "%s"' %(self.dsfexe, dstname, dsfname))
            if (x or not exists(dsfname)):
                raise FS2XError("Can't write DSF %s.dsf (%s)" % (tilename, x))
