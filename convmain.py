from math import floor
from os import curdir, mkdir, pardir, sep, stat, unlink, walk
from os.path import basename, exists, isdir, join, normpath, splitext
from shutil import copyfile
from struct import unpack
from sys import exit, platform
from tempfile import gettempdir

from convutil import banner, helper, complexities, AptNav, Object, Point
import convbgl
import convxml

class Output:
    def __init__(self, mypath, xppath, fspath, status, log, fatal):

        self.debug=True
        self.dumplib=False
        self.overlays=True
        self.docomplexity=False
        
        self.xppath=xppath
        self.fspath=fspath
        self.status=status
        self.log=log
        self.fatal=fatal

        self.misc=[]
        self.apt={}
        self.nav=[]
        self.exc=[]	# Exclusion rectangles: (bottomleft, topright)
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
        else:
            self.bglexe=None	# Only available on Windows
            self.xmlexe=curdir+sep+platform+sep+'bglxml'
            self.pngexe=curdir+sep+platform+sep+'bmp2png'
            self.dsfexe=curdir+sep+'DSFTool'

        if not exists(fspath):
            fatal('"%s" does not exist' % fspath)
        if not isdir(fspath):
            fatal('"%s" is not a folder' % fspath)
        for path, dirs, files in walk(xppath):
            if dirs or files:
                fatal('"%s" is not empty' % xppath)
        path=normpath(join(xppath, pardir))
        if basename(path).lower()!='custom scenery' or not isdir(path):
            fatal('"%s" is not a sub-folder of "Custom Scenery"' % xppath)

        for exe in [self.bglexe, self.xmlexe, self.pngexe, self.dsfexe]:
            if exe and not exists(exe):
            	fatal("Can't find \"%s\"" % exe)
        
        path=join(mypath, 'objfile.txt')
        try:
            stock=file(path, 'rU')
        except IOError:
            fatal("Can't read \"%s\"." % path)
        for line in stock:
            if line[0]!=';':
                l=line.find(',')
                if l!=-1:
                    self.stock[line[:l].strip()]=line[l+1:].strip()
        stock.close()
        if exists('debug.txt'): unlink('debug.txt')

    def export(self):
        # Off we go
        self.status('Reading BGLs')
        for path, dirs, files in walk(self.fspath):
            #if 1:
            #(path, files)=("C:\Program Files\Microsoft Games\Flight Simulator 9\Addon Scenery\FlyTampa-SanFrancisco\scenery", ["tl1.bgl"])

            for filename in files:
                if filename[-4:].lower()=='.bgl':
                    bglname=join(path, filename)
                    if stat(bglname).st_size==0:
                        continue	# Sometimes seen 0-length files!
                    self.status(bglname[len(self.fspath)+1:])
                    tmp=None
                    try:
                        bgl=file(bglname, 'rb')
                    except IOError:
                        self.log("Can't read \"%s\"" % bglname)
                        continue
        
                    c=bgl.read(2)
                    if len(c)!=2:
                        self.log("Can't read \"%s\"" % bglname)
                        continue                
                    (c,)=unpack('<H', c)
                    if c==1:
                        bgl.seek(122)
                        (spare2,)=unpack('<I',bgl.read(4))
                        if spare2:
                            bgl.close()
                            if not self.bglexe:
                                self.log("Can't parse compressed file %s" % (
                                    filename))
                                continue
                            tmp=join(gettempdir(), filename)
                            helper('%s "%s" "%s"' %(self.bglexe, bglname, tmp))
                            if not exists(tmp):
                                self.log("Can't parse compressed file %s" % (
                                    filename))
                                continue
                            bgl=file(tmp, 'rb')
                        convbgl.Parse(bgl, filename, bglname, self, None, None)
                    elif c==0x201:
                        tmp=join(gettempdir(), filename[:-3]+'xml')
                        x=helper('%s -t "%s" "%s"' % (
                            self.xmlexe, bglname, tmp))
                        if not x and exists(tmp):
                            try:
                                xmlfile=file(tmp, 'rU')
                            except IOError:
                                self.log("Can't parse %s" % filename)
                            convxml.Parse(xmlfile, filename, bglname,
                                          self, None, None)
                            xmlfile.close()
                        else:
                            self.log("Can't parse %s (%s)" % (filename, x))
                    else:
                        self.log("Can't parse \"%s\". Is this a BGL file?" % (
                            filename))
                    bgl.close()
                    if tmp and exists(tmp): unlink(tmp)

        # Now export
        if self.apt or self.nav or self.objplc:
            if not isdir(self.xppath): mkdir(self.xppath)
        else:
            self.fatal('No data found!')

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
                name="Windsock"
            elif code==18:
                name="Beacon"
            elif code==10:
                name="Apron"
            else:
                continue	# wtf?
            if distance==16000:	# X-Plane limit is 10 miles
                self.log("Can't find an airport for %s at [%10.6f, %11.6f]" % (
                    name, loc.lat, loc.lon))
            elif code==10:
                self.apt[airport].append(AptNav(code, loc, data))
            else:
                self.apt[airport].append(AptNav(code, loc, "%6d %s %s" % (
                    data, airport, name)))

        if self.apt:
            path=join(self.xppath, 'Earth nav data')
            if not isdir(path): mkdir(path)
            filename=join(path, 'apt.dat')
            f=file(filename, 'wt')
            f.write("I\n810\t# %s\n" % banner)
            for k, v in self.apt.iteritems():
                doneheader=False
                v.sort()
                for l in v:
                    if l.code==1:
                        # Only write one header
                        if not doneheader:
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


        self.status('Writing OBJs')
        # make a list of requested objects and scales
        objdef={}
        for loc, heading, complexity, name, scale in self.objplc:
            if not name in objdef:
                objdef[name]=[scale]
            elif not scale in objdef[name]:
                objdef[name].append(scale)

        # Create placeholders for stock objects
        for name in objdef.keys():
            if not self.objdat.has_key(name) and self.stock.has_key(name):
                self.log('Object %s is a built-in object (%s)' % (
                    name, self.stock[name]))
                self.objdat[name]=[Object(name+'.obj',
                                          "Placeholder for built-in object %s (%s)" % (name, self.stock[name]),
                                          None, [], [], [], [], [])]
                
        # write out objects
        for name in sorted(objdef):
            if name in self.objdat:
                self.status(name)
                for scale in objdef[name]:
                    count=1
                    for obj in self.objdat[name]:
                        obj.export(scale, self)
            else:
                self.log('Object %s not found' % name)


        # copy readmes
        for path, dirs, files in walk(self.xppath):
            for filename in files:
                for f in ['readme', 'read me',
                          'leeeme', 'leee me',
                          'lisezmoi', 'lisez moi']:
                    if f in filename:
                        copyfile(join(path, filename),
                                 join(self.xppath, filename))
        
        self.status('Writing DSFs')
        # poly_os objects need to be drawn first to prevent them from
        # swallowing other objects.
        # X-Plane 8.20 and 8.30 draw in order of definition (not placement)
        # in the DSF file. We therefore need poly_os objects to be defined
        # first. This is incompatible with prioritisation, since lower
        # prority objects come last. So disable prioritisation.
        cmplx={}
        for loc, heading, complexity, name, scale in self.objplc:
            if self.dumplib and not loc: continue
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
            if self.dumplib and not loc: continue
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
        srcpath=normpath(join(join(self.xppath, pardir), pardir))
        srcpath=join(join(join(srcpath, "Resources"), "default scenery"),
                     "DSF 820 Earth")

        for tile in objdef.keys():
            (lat,lon)=tile
            sw=Point(lat,lon)
            ne=Point(sw.lat+1,sw.lon+1)
            defs=objdef[tile]
            plcs=objplc[tile]
            tilename="%+03d%+04d" % (lat,lon)
            tiledir=join("Earth nav data", "%+02d0%+03d0" % (
                int(lat/10), int(lon/10)))
            self.status(tilename+'.dsf')
    
            if self.overlays:
                objcount=0
            else:
                srcname=join(join(srcpath, tiledir), tilename+'.dsf')
                dsfname=join(gettempdir(), tilename+'.txt')
                if not exists(srcname):
                    self.fatal("Can't read source DSF %s.dsf"%(tilename))
                x=helper(self.dsfexe+' -dsf2text "'+srcname+'" "'+dsfname+'"')
                if x or not exists(dsfname):
                    self.fatal("Can't read source DSF %s.dsf (%s)" %
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
                            self.fatal("Can't read source DSF %s.dsf"%tilename)

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
                    (bl,tr)=exc
                    if bl.within(sw,ne) or tr.within(sw,ne):
                        dst.write('PROPERTY sim/exclude_objs\t%11.6f,%10.6f,%11.6f,%10.6f\n' % (bl.lon,bl.lat,tr.lon,tr.lat))
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
                        dst.write('OBJECT %3d %11.6f %10.6f %7.3f\n' % (
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
            print '%s -text2dsf "%s" "%s"' % (self.dsfexe, dstname, dsfname)
            x=helper('%s -text2dsf "%s" "%s"' %(self.dsfexe, dstname, dsfname))
            if (x or not exists(dsfname)):
                self.fatal("Can't write DSF %s.dsf (%s)" % (tilename, x))
