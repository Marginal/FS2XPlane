from math import acos, atan, atan2, cos, fmod, floor, hypot, pow, sin, pi, radians, degrees
from numpy import array, array_equal
from os import listdir
from os.path import basename, dirname, exists, join, normpath, pardir, splitext
import struct
from struct import unpack
from sys import maxint
from traceback import print_exc
import types

from OpenGL.GL import GL_LINE_LOOP, GL_TRUE, GLfloat
from OpenGL.GLU import *
try:
    # apparently older PyOpenGL version didn't define gluTessVertex
    gluTessVertex
except NameError:
    from OpenGL import GLU
    gluTessVertex = GLU._gluTessVertex

from convutil import cirp, m2f, complexity, asciify, unicodeify, normalize, rgb2uv, cross, dot, AptNav, Object, Material, Texture, Point, Matrix, FS2XError, unique, groundfudge, effects
from convobjs import makegenquad, makegenmulti
from convtaxi import taxilayout, Node, Link
from convphoto import blueskyre


# Subset of XML TaxiwayPoint
class TaxiwayPoint:
    def __init__(self, loc):
        self.type='NORMAL'
        self.lat=loc.lat
        self.lon=loc.lon

# Subset of XML TaxiwayPath
class TaxiwayPath:
    # width<0 -> no lights. -1<=width<=1 -> centreline only
    def __init__(self, type, width, centerline, start, end):
        self.type=type	# TAXI or VEHICLE
        if width>0:
            self.width=width
        else:
            self.width=-width
        self.surface='ASPHALT'
        if -1<=self.width<=1:
            # Centreline only
            self.width=2	# reasonable number for curves
            self.centerline='TRUE'
            if width>0:
                self.centerLineLighted='TRUE'
            else:
                self.centerLineLighted='FALSE'
            self.rightEdge=self.leftEdge='NONE'
            self.rightEdgeLighted=self.leftEdgeLighted='NONE'
            self.drawSurface=self.drawDetail='FALSE'
        else:
            self.drawSurface=self.drawDetail='TRUE'
            if type=='VEHICLE':
                self.centerLine=centerline
                if centerline and width>0:
                    self.centerLineLighted='TRUE'
                else:
                    self.centerLineLighted='FALSE'
                self.rightEdge=self.leftEdge='SOLID'
                self.rightEdgeLighted=self.leftEdgeLighted='FALSE'
            else:
                self.centerline=self.centerLineLighted='FALSE'
                self.rightEdge=self.leftEdge='SOLID'
                if width>0:
                    self.rightEdgeLighted=self.leftEdgeLighted='TRUE'
                else:
                    self.rightEdgeLighted=self.leftEdgeLighted='FALSE'
        self.start=start
        self.end=end
        self.name=0	# no name

# Subset of XML TaxiwayName
class TaxiwayName:
    def __init__(self, name):
        self.name=name
        
                 
# Read BGL header
class Parse:
    def __init__(self, bgl, srcfile, output):
        if output.debug: output.debug.write('\nFile: %s\n' % srcfile.encode("latin1",'replace'))
        name=basename(srcfile)
        texdir=None
        for section in [42,46,54,58,102,114]:
            bgl.seek(section)
            (secbase,)=unpack('<I',bgl.read(4))
            if (secbase):
                bgl.seek(secbase)
                if section==42 or section==46:
                    output.log('Skipping traffic data in file %s' % name)
                elif section==54:
                    try:
                        ProcTerrain(bgl, srcfile, output)
                    except:
                        output.log("Can't parse Terrain section in file %s" % name)
                elif section==58:	# OBJECT
                    # Per-BGL counts
                    old=False
                    rrt=False
                    anim=False
                    first=True
                    gencache={}	# cache of generic building names, by args
                    objcache=[]	# objects generated in this BGL, for dupe detection
                    if not texdir:
                        texdir=normpath(join(dirname(srcfile), pardir))
                        # For case-sensitive filesystems
                        for d in listdir(texdir):
                            if d.lower()=='texture':
                                texdir=maketexdict(join(texdir, d))
                                break
                        else:
                            texdir=None
                    while True:
                        # LatBand
                        posl=bgl.tell()
                        (c,)=unpack('<B', bgl.read(1))
                        if not c in [0, 21]:
                            if output.debug: output.debug.write("!Bogus LatBand %2x\n" % c)
                            raise struct.error	# wtf?
                        if c==0:
                            break
                        (foo,off)=unpack('<Ii', bgl.read(8))
                        bgl.seek(secbase+off)
                        while True:
                            # Header
                            posa=bgl.tell()
                            if __debug__:
                                if output.debug: output.debug.write("----\nArea %x\n" % posa)
                            (c,)=unpack('<B', bgl.read(1))
                            bgl.read(9)
                            if c==0:
                                break
                            elif c in [6,9,12,14]:
                                (l,)=unpack('<I',bgl.read(4))
                            elif c in [5,8,11,13]:
                                (l,)=unpack('<H',bgl.read(2))
                            elif c in [4,7,10]:
                                (l,)=unpack('<B',bgl.read(1))
                            else:
                                if output.debug: output.debug.write("!Bogus area type %x\n"%c)
                                raise struct.error	# wtf?
                            try:
                                output.refresh()
                                p=ProcScen(bgl, posa+l, 1.0, None, srcfile, texdir, output, firstarea=first, gencache=gencache, objcache=objcache)
                                if p.old:
                                    old=True
                                    if __debug__:
                                        if output.debug: output.debug.write("Pre-FS2002\n")
                                if p.rrt:
                                    rrt=True
                                    if __debug__:
                                        if output.debug: output.debug.write("Old-style rr\n")
                                if p.anim:
                                    anim=True
                                    if __debug__:
                                        if output.debug: output.debug.write("Animation\n")
                                first=False
                            except:
                                output.log("Can't parse area %x in file %s" % (posa, name))
                                if output.debug: print_exc(None, output.debug)
                                    
                            bgl.seek(posa+l)
                        bgl.seek(posl+9)
                    if anim:
                        output.log("Skipping animation in file %s" % name)
                    if old:
                        output.log("Skipping pre-FS2002 scenery in file %s" % name)
                    if rrt:
                        output.log("Skipping pre-FS2004 runways and/or roads in file %s" % name)
                elif section==102:
                    # Miscellaneous
                    while True:
                        # LatBand
                        posl=bgl.tell()
                        (c,)=unpack('<B', bgl.read(1))
                        if not c in [0, 21]:
                            if output.debug: output.debug.write("!Bogus LatBand %2x\n" % c)
                            raise struct.error	# wtf?
                        if c==0:
                            break
                        (foo,off)=unpack('<Ii', bgl.read(8))
                        bgl.seek(secbase+off)
                        try:
                            ProcMisc(bgl, srcfile, output)
                        except:
                            output.log("Can't parse Miscellaneous section in file %s" % name)
                        bgl.seek(posl+9)


# handle section 9 area and 10 library. libname!=None if this is a library
class ProcScen:
    def __init__(self, bgl, enda, scale, libname, srcfile, texdir, output, scen=None, tran=None, firstarea=True, gencache=None, objcache=None):

        self.old=False	# Old style scenery found and skipped
        self.rrt=False	# Old style runways/roads found and skipped
        self.anim=False	# Animations found and skipped
        self.debug=output.debug
        self.cmd=0

        self.bgl=bgl
        self.enda=enda
        self.libname=libname
        self.name=libname	# base name for generated objects
        self.srcfile=srcfile
        self.texdir=texdir
        if libname:
            self.comment="object %s in file %s" % (
                libname,asciify(basename(self.srcfile),False))
        else:
            self.comment="file %s" % asciify(basename(self.srcfile),False)	# Used for reporting
        self.output=output
        self.firstarea=firstarea
        self.gencache=gencache
        self.objcache=objcache

        self.start=bgl.tell()
        if tran: self.tran=self.start+tran	# Location of TRAN table
        if scen:
            # Decode SCEN table
            bgl.seek(self.start+scen)
            (count,)=unpack('<H', bgl.read(2))
            scen=self.start+scen+2
            self.scen=[None for i in range(count)]
            for i in range(count):
                bgl.seek(scen+i*12)
                (out,child,peer,size,offset)=unpack('<hhhhi', bgl.read(12))
                # Child and Peer are offsets; convert to scene nos
                if child!=-1:
                    bgl.seek(scen+child*12)
                    (child,)=unpack('<h',bgl.read(2))
                if peer!=-1:
                    bgl.seek(scen+peer*12)
                    (peer,)=unpack('<h',bgl.read(2))
                # Convert offsets to file positions
                self.scen[out]=(child, peer, size, scen+i*12+offset, -1)
            # Invert Child/Peer pointers to get parents
            for i in range(count):
                (child, peer, size, posa, parent)=self.scen[i]
                if child!=-1:	# child's parent is me
                    (xchild, xpeer, xsize, xposa, xparent)=self.scen[child]
                    self.scen[child]=(xchild, xpeer, xsize, xposa, i)
                if peer!=-1:	# peer's parent is my parent
                    (xchild, xpeer, xsize, xposa, xparent)=self.scen[peer]
                    self.scen[peer]=(xchild, xpeer, xsize, xposa, parent)
            if self.debug:
                # Dump SCEN table
                self.debug.write("SCEN: %-2d        ANIC\n" % count)
                maxt=-1
                for i in range(count):
                    (child,peer,size,posa,parent)=self.scen[i]
                    bgl.seek(posa)
                    (cmd,src,dst)=unpack('<3H', bgl.read(6))
                    c="%2d: %2d %2d %2d -> %2x " %(i, child, peer, parent, cmd)
                    if cmd==0xc6 and size==6:
                        c+="%2d %2d\n" % (src, dst)
                        maxt=max(maxt,src)
                    else:
                        c+="size=%d\n" % size
                    self.debug.write(c)
                # Dump TRAN table
                count=maxt+1
                self.debug.write("TRAN: %d\n" % count)
                bgl.seek(self.tran)
                for i in range(count):
                    m=[]
                    for j in range(4):
                        (a,b,c,d)=unpack('<4f', bgl.read(16))
                        m.append([a,b,c,d])
                    self.debug.write("%s = %d\n" % (Matrix(m), i))
            bgl.seek(self.start)
        
        # State
        self.complexity=1
        self.loc=None
        self.alt=0
        self.altmsl=0
        self.layer=None
        self.matrix=[None]
        self.scale=1.0		# don't know what to do with scale value in FS8 libs
        self.basescale=self.scale
        self.stack=[]		# (return address, layer, billboard, pop matrix?)
        self.tex=[]
        self.mat=[]
        self.vtx=[None] * 2048	# DefRes/ResList limit
        self.idx=[]		# Indices into vtx
        self.m=None		# Index into mat
        self.t=None		# Index into tex
        self.lightcol=(1,1,1)
        self.billboard=None	# Emulating billboarding

        self.nodes=[]
        self.links=[]
        self.linktype=None	# Last road/river/taxiway (type, width, centerline)
        self.haze=0		# Whether palette-based transparency. 0=none
        self.zbias=0		# Polygon offsetting
        self.surface=False	# StrRes/CntRes does lines not surface by default
        self.concave=False
        
        self.objdat={}		# (mat, vtx[], idx[]) by (name, loc, layer, alt, altmsl, matrix, scale, Texture)
        self.lightdat={}	# ((x,y,z), (r,g,b)) by (name, loc, layer, alt, altmsl, matrix, scale, None)
        self.effectdat={}	# ((x,y,z), (effect, s)) by (name, loc, layer, alt, altmsl, matrix, scale, None)
        self.keys=[]		# ordered list of keys for indexing the above
        self.polydat=[]		# ((points, layer, heading, scale, Texture))

        self.neednight=False
        self.dayloc=None
        self.dayobjdat={}        
        self.daylightdat={}        
        self.dayeffectdat={}
        self.daypolydat=[]

        self.vars={
            # Vars not listed are assumed to be 0
            0: 0,	# dummy
            0x02: 2,	# No idea, but used by Aerosoft to control lighting
            0x10: 50,	# No idea, but used by Aerosoft to control lighting
            0x5c: 255,	# Local variable used by Aerosoft in EDDF
            #0x07e: 0,	# FS5_CG_TO_GROUND_X: ???
            0x280: 0,	# altmsl (presumably of airplane?)
            0x282: 1,	# beacon: rotating bitmap shifted 1 bit/3 sec
            0x28c: 1,	# tod: 2|4 indicates night?
            0x30A: 6,	# beacon_2: 16-bit bitmap with 0x0506 add/3 sec
            0x30C: 8,	# beacon_3: 16-bit bitmap with 0x0708 add/3 sec 
            0x30E: 0xa,	# beacon_4: 16-bit bitmap with 0x090A add/3 sec 
            0x310: 0xc,	# beacon_5: 16-bit bitmap with 0x0B0C add/3 sec
            #0x312-31a	# usrvar-usrvar5
            #0x338, 1,	# SHADOW_FLAG: 0=do crash detection???
            0x33a: 0,	# rbias: eye to object distance in meters II.FF
            0x33b: 0,	# rbias_1: eye to object distance in meters IIII
            0x340: 255,	# ground_texture
            0x342: 255,	# building_texture
            0x344: 255,	# aircraft_texture
            0x346: 5,	# image_complex: complexity of the scenery 0-5
            0x37e: 1,	# xv: rotated X-axis eye to object distance
            0x382: 67,	# yv: rotated Y-axis eye to object distance - must be >66 for UK2000
            0x386: 1,	# zv: rotated Z-axis eye to object distance
            0x389: 12,	# zulu hours in the day - Midday
            0x390: 0,	# water_texture
            0xc72: 5,	# ground wind velocity [kts?]
            0xc74: 0,	# ground wind direction [units?]
            0xc76: 0,	# ground wind turbulence [units?]
            }
        self.setseason()

        cmds={0x02:self.NOP,
              0x05:self.Surface,
              0x06:self.SPnt,
              0x07:self.CPnt,
              0x08:self.Closure,
              0x0d:self.Jump,
              0x0e:self.DefRes,
              0x0f:self.StrRes,
              0x10:self.CntRes,    
              0x14:self.SColor,
              0x17:self.TextureEnable,
              0x18:self.Texture,
              0x1a:self.ResList,
              0x1b:self.Jump,
              0x1c:self.IfIn2,
              0x1d:self.FaceT,
              0x1e:self.Haze,
              0x1f:self.TaxiMarkings,
              0x20:self.FaceTTMap,
              0x21:self.IfIn3,
              0x22:self.Return,
              0x23:self.Call,
              0x24:self.IfIn1,
              0x25:self.SeparationPlane,
              0x26:self.SetWrd,
              0x29:self.GResList,
              0x2a:self.FaceT,
              0x2b:self.Call32,
              0x2d:self.SColor24,
              0x2e:self.LColor24,
              0x2f:self.Scale,
              0x30:self.NOPh,
              0x32:self.Call,
              0x33:self.Instance,
              0x34:self.SuperScale,
              0x35:self.PntRow,
              0x37:self.Point,
              0x38:self.Concave,
              0x39:self.IfMsk,
              0x3b:self.VInstance,
              0x3c:self.Position,
              0x3e:self.FaceT,
              0x40:self.ShadowVPosition,
              0x42:self.TextureRunway,
              0x43:self.Texture2,
              0x44:self.TextureRunway,
              0x4c:self.VScale,
              0x4d:self.MoveL2G,
              0x4e:self.MoveL2G,
              0x46:self.PointVICall,
              0x49:self.Building,
              0x3f:self.NOPh,
              0x50:self.SColor,
              0x51:self.LColor,
              0x52:self.SColor,
              0x55:self.SurfaceType,
              0x5d:self.TextureRepeat,
              0x5f:self.IfSizeV,
              0x62:self.IfVis,
              0x63:self.LibraryCall,
              0x69:self.RoadStart,
              0x6a:self.RoadCont,
              0x6b:self.RiverStart,
              0x6c:self.RiverCont,
              0x6d:self.IfSizeV,
              0x6e:self.TaxiwayStart,
              0x6f:self.RoadCont,
              0x70:self.AreaSense,
              0x73:self.Jump,
              0x74:self.AddCat,
              0x75:self.Call,
              0x76:self.NOP,
              0x77:self.ScaleAGL,
              0x7a:self.FaceTTMap,
              0x7d:self.NOP,
              0x80:self.ResPnt,
              0x81:self.NOPh,
              0x83:self.ReScale,
              0x88:self.Jump32,
              0x89:self.NOPi,
              0x8a:self.Call32,
              0x8b:self.AddCat32,
              0x8f:self.NOPi,
              0x93:self.NOPh,
              0x95:self.CrashIndirect,
              0x96:self.CrashStart,
              0x9e:self.Interpolate,
              0x9f:self.NOPi,
              0xa0:self.Object,
              0xa4:self.NOPh,
              0xa6:self.TargetIndicator,
              0xa7:self.SpriteVICall,
              0xa8:self.TextureRoadStart,
              0xaa:self.NewRunway,
              0xad:self.Animate,
              0xae:self.TransformEnd,
              0xac:self.ZBias,
              0xaf:self.TransformMatrix,
              0xb1:self.Tag,
              0xb2:self.Light,
              0xb3:self.IfInF1,
              0xb4:self.NOPi,
              0xb5:self.VertexList,
              0xb6:self.MaterialList,
              0xb7:self.TextureList,
              0xb8:self.SetMaterial,
              0xb9:self.DrawTriList,
              0xba:self.DrawLineList,
              0xbc:self.NOPi,
              0xbd:self.NOP,
              0xc4:self.SetMatrixIndirect,
              }

        while True:
            pos=bgl.tell()
            if pos>=self.enda:
                self.cmd=0
                if pos>self.enda and self.debug: self.debug.write("!Overrun at %x enda=%x\n" % (pos, self.enda))
            elif pos<self.start:
                # Underrun - just return if in a call eg ESGJ2K2
                self.cmd=0x22
                if self.debug: self.debug.write("!Underrun at %x start=%x\n" % (pos, self.start))
            else:
                (self.cmd,)=unpack('<H',bgl.read(2))
            if self.cmd==0 or (self.cmd==0x22 and not self.stack):
                if self.donight():
                    bgl.seek(self.start)
                    continue
                self.makeobjs()
                if self.debug:
                    if __debug__:
                        self.debug.write("%x: cmd %02x\n" % (pos, self.cmd))
                    for i in range(1, len(self.matrix)):
                        self.debug.write("!Unbalanced matrix:\n%s\n" % (
                            self.matrix[i]))
                return
            elif self.cmd in cmds:
                if __debug__:
                    if self.debug: self.debug.write("%x: cmd %02x %s\n" % (
                        pos, self.cmd, cmds[self.cmd].__name__))
                cmds[self.cmd]()
            elif self.donight():
                bgl.seek(self.start)
                continue
            else:
                self.makeobjs()	# Try to go with what we've got so far
                if self.debug: self.debug.write("!Unknown cmd %x at %x\n" % (self.cmd, pos))
                raise struct.error


    def donight(self):
        if self.neednight and self.vars[0x28c]==1:
            if __debug__:
                if self.debug: self.debug.write("Night\n")
            self.vars[0x28c]=4
            self.dayloc=self.loc
            self.dayobjdat=self.objdat
            self.daylightdat=self.lightdat
            self.dayeffectdat=self.effectdat
            self.daypolydat=self.polydat
            self.objdat={}
            self.lightdat={}
            self.effectdat={}
            #self.keys=[]	# Don't reset keys - needed to catch day-only objs
            self.polydat=[]
            self.complexity=1
            self.loc=None
            self.alt=0
            self.altmsl=0
            self.layer=None
            self.matrix=[None]
            self.scale=self.basescale
            self.stack=[]	# (return address, layer, billboard, pop matrix?)
            self.tex=[]
            self.mat=[]
            self.vtx=[None] * 2048	# DefRes limit
            self.idx=[]		# Indices into vtx
            self.m=None		# Index into mat
            self.t=None		# Index into tex
            self.lightcol=(1,1,1)
            self.billboard=None	# Emulating billboarding
            self.nodes=[]
            self.links=[]
            self.linktype=None	# Last road/river/taxiway (type, width, centerline)
            self.haze=0		# Whether palette-based transparency. 0=none
            self.zbias=0	# Polygon offsetting
            self.concave=False
            return True
        return False

    def makekey(self, dotex=True):
        # Return a key suitable for indexing self.objdat
        if self.t==None:
            tex=None
            if __debug__:
                if self.debug and not tex: self.debug.write("No texture\n")
        else:
            tex=self.tex[self.t]
            if self.haze and tex.d: self.output.haze[tex.d]=self.haze
            if self.haze and tex.e: self.output.haze[tex.e]=self.haze

        if self.m==None:
            mat=Material(self.output.xpver, (0,0,0))
            if __debug__:
                if self.debug and not mat: self.debug.write("No material\n")
        else:
            mat=self.mat[self.m].clone()
        mat.dblsided=bool(self.billboard)

        return ((self.name,self.loc,self.layer,self.alt,self.altmsl,self.matrix[-1],self.scale,tex), mat)

    def makename(self):
        # make a unique base filename
        assert not self.libname	# Shouldn't be called in library objects
        if self.firstarea:
            self.name=asciify(splitext(basename(self.srcfile))[0])
        else:
            self.name="%s@%X" % (asciify(splitext(basename(self.srcfile))[0]), self.bgl.tell()-2)
        self.firstarea=False

    def Surface(self):		# 05
        self.surface=True	# StrRes/CntRes does surface not lines

    def SPnt(self):		# 06
        (sx,sy,sz)=unpack('<hhh', self.bgl.read(6))
        self.old=True

    def CPnt(self):		# 07
        (cx,cy,cz)=unpack('<hhh', self.bgl.read(6))
        self.old=True

    def Closure(self):		# 08
        if not self.surface:
            self.old=True
            return
        count=len(self.idx)
        if count<=4: self.concave=False	# Don't bother
        vtx=[]
        for i in range(count):
            (x,y,z,nx,ny,nz,c,c)=self.vtx[self.idx[i]]
            vtx.append((x,y,z, nx,ny,nz, x*self.scale/256, z*self.scale/256))
        self.idx=[]
        self.surface=False
        (key,mat)=self.makekey()
        if not key in self.objdat and self.makepoly(False, vtx):	# don't generate poly if there's already geometry here
            return
        if self.concave:
            (vtx,idx)=subdivide(vtx)
            self.concave=False
        else:
            idx=[]
            for i in range(1,len(vtx)-1):
                idx.extend([0,i,i+1])	# make a fan
        # Change order if necessary to face in direction of normal
        (x0,y0,z0,c,c,c,c,c)=vtx[idx[0]]
        (x1,y1,z1,c,c,c,c,c)=vtx[idx[1]]
        (x2,y2,z2,c,c,c,c,c)=vtx[idx[2]]
        (x,y,z)=cross((x1-x0,y1-y0,z1-z0), (x2-x0,y2-y0,z2-z0))
        if dot((x,y,z), (nx,ny,nz))>0:	# arbitrary normal from last point
            idx.reverse()
        mat.poly=True	# This command sort-of implies ground-level
        if not key in self.objdat:
            self.objdat[key]=[]
            self.keys.append(key)
        self.objdat[key].append((mat, vtx, idx))
        self.checkmsl()
        
    def Jump(self):		# 0d, 1b: IfInBoxRawPlane, 73: IfInBoxP
        (off,)=unpack('<h', self.bgl.read(2))
        if not off: raise struct.error	# infloop
        self.bgl.seek(off-4,1)

    def DefRes(self):		# 0e
        (i)=unpack('<H',self.bgl.read(2))
        self.vtx[i]=unpack('<3h', self.bgl.read(6))+(0,1,0,0,0)

    def StrRes(self):		# 0f
        (i,)=unpack('<H',self.bgl.read(2))
        self.idx=[i]

    def CntRes(self):		# 10
        (i,)=unpack('<H',self.bgl.read(2))
        self.idx.append(i)	# wait for closure
        
    def SColor(self):	# 14:Scolor, 50:GColor, 52:NewSColor
        (c,)=unpack('H', self.bgl.read(2))
        self.mat=[Material(self.output.xpver, self.unicol(c))]
        self.m=0
        
    def TextureEnable(self):	# 17
        (c,)=unpack('<H', self.bgl.read(2))
        if not c: self.t=None

    def Texture(self):		# 18
        self.surface=True	# StrRes/CntRes does surface not lines
        (c,x,c,y)=unpack('<4h', self.bgl.read(8))
        tex=self.bgl.read(14).rstrip(' \0')
        l=tex.find('.')
        if l!=-1:	# Sometimes formatted as 8.3 with spaces
            tex=tex[:l].rstrip(' \0')+tex[l:]
        tex=findtex(tex, self.texdir, self.output.addtexdir)
        self.tex=[tex and Texture(self.output.xpver, tex, None) or None]
        self.t=0
        if __debug__:
            if self.debug:
                self.debug.write("%s\n" % self.tex[0])
                if x or y: self.debug.write("!Tex offsets %d,%d\n" % (x,y))
        
    def ResList(self):		# 1a
        (index,count)=unpack('<2H', self.bgl.read(4))
        for i in range(index,index+count):
            self.vtx[i]=unpack('<3h', self.bgl.read(6))+(0,1,0,0,0)

    def IfInBoxRawPlane(self):	# 1b
        # Skip
        (off,)=unpack('<h', self.bgl.read(2))
        if not off: raise struct.error	# infloop
        self.bgl.seek(off-4,1)
        
    def IfIn2(self):		# 1c
        var=[0,0]
        mins=[0,0]
        maxs=[0,0]
        (off, var[0], mins[0], maxs[0],
         var[1], mins[1], maxs[1])=unpack('<7h', self.bgl.read(14))
        for i in range(2):
            if var[i]==0x346:
                self.complexity=complexity(mins[i])
                if maxs[i]==4: maxs[i]=5	# bug in eg EGNT
            val=self.getvar(var[i])
            if val<mins[i] or val>maxs[i]:
                if not off: raise struct.error	# infloop
                self.bgl.seek(off-22,1)
                break

    def Haze(self):		# 1e:Haze
        (self.haze,)=unpack('<H', self.bgl.read(2))
        
    def TaxiMarkings(self):	# 1f
        # ignored - info should now be in FS2004-style BGL
        self.rrt=True
        (size,)=unpack('<H', self.bgl.read(2))
        self.bgl.seek(size-4,1)
        
    def FaceTTMap(self):	# 20:FaceTTMap, 7a:GFaceTTMap
        (count,fnx,fny,fnz,)=unpack('<H3h', self.bgl.read(8))
        if count<=4: self.concave=False	# Don't bother
        fnx=fnx/32767.0
        fny=fny/32767.0
        fnz=fnz/32767.0
        self.bgl.read(4)
        vtx=[]
        maxy=-maxint
        for i in range(count):
            (idx,tu,tv)=unpack('<H2h', self.bgl.read(6))
            (x,y,z,nx,ny,nz,c,c)=self.vtx[idx]
            maxy=max(maxy,y)
            if self.billboard:
                vtx.append((x,y,z, 0,1,0, x*self.scale/256, z*self.scale/256))
            elif self.cmd==0x7a:
                vtx.append((x,y,z, nx,ny,nz, tu/255.0,tv/255.0))
            else:
                vtx.append((x,y,z, fnx,fny,fnz, tu/255.0,tv/255.0))
        if not self.objdat and blueskyre.match(basename(self.tex[self.t].d)):
            if __debug__:
                if self.debug: self.debug.write("Photoscenery\n")
            return	# handled in ProcPhoto
        (key,mat)=self.makekey()
        if not key in self.objdat and self.makepoly(True, vtx):	# don't generate poly if there's already geometry here
            return
        if self.concave:
            (vtx,idx)=subdivide(vtx)
            self.concave=False
        else:
            idx=[]
            for i in range(1,len(vtx)-1):
                idx.extend([0,i,i+1])
        # Change order if necessary to face in direction of normal
        (x0,y0,z0,c,c,c,c,c)=vtx[idx[0]]
        (x1,y1,z1,c,c,c,c,c)=vtx[idx[1]]
        (x2,y2,z2,c,c,c,c,c)=vtx[idx[2]]
        (x,y,z)=cross((x1-x0,y1-y0,z1-z0), (x2-x0,y2-y0,z2-z0))
        if dot((x,y,z), (fnx,fny,fnz))>0:
            idx.reverse()
        if maxy+self.alt <= groundfudge:
            mat.poly=True
        if not key in self.objdat:
            self.objdat[key]=[]
            self.keys.append(key)
        self.objdat[key].append((mat, vtx, idx))
        self.checkmsl()
        
    def IfIn3(self):		# 21
        var=[0,0,0]
        mins=[0,0,0]
        maxs=[0,0,0]
        (off, var[0], mins[0], maxs[0],
         var[1], mins[1], maxs[1],
         var[2], mins[2], maxs[2])=unpack('<10h', self.bgl.read(20))
        for i in range(3):
            if var[i]==0x346:
                self.complexity=complexity(mins[i])
                if maxs[i]==4: maxs[i]=5	# bug in eg EGNT
            val=self.getvar(var[i])
            if val<mins[i] or val>maxs[i]:
                if not off: raise struct.error	# infloop
                self.bgl.seek(off-22,1)
                break

    def Return(self):		# 22
        (off,self.layer,self.billboard,pop)=self.stack.pop()
        if pop:
            self.matrix.pop()
            if __debug__:
                if self.debug: self.debug.write("Now\n%s\n" % self.matrix[-1])
        self.bgl.seek(off)

    def Call(self):		# 23:Call, 32:PerspectiveCall/AddObj, 75:AddMnt
        (off,)=unpack('<h', self.bgl.read(2))
        if not off: raise struct.error	# infloop
        self.precall(False)
        self.bgl.seek(off-4,1)

    def IfIn1(self):		# 24
        (off, var, vmin, vmax)=unpack('<4h', self.bgl.read(8))
        if vmin>vmax:	# Sigh. Seen in TFFR
            foo=vmax
            vmax=vmin
            vmin=foo
        if var==0x346:
            self.complexity=complexity(vmin)
            if vmax==4: vmax=5	# bug in eg EGNT
        val=self.getvar(var)
        if __debug__:
            if self.debug:
                self.debug.write("%x: %d<=%d<=%d\n" % (var, vmin, val, vmax))
        if (self.output.registered and var==0) or var in [0x312,0x314,0x316,0x318,0x31a]:
            return	# user-defined - assume True
        if val<vmin or val>vmax:
            if not off: raise struct.error	# infloop
            self.bgl.seek(off-10,1)

    def SeparationPlane(self):	# 25
        # Used for animating distance. Skip
        (off,nx,ny,nz,dist)=unpack('<4hi', self.bgl.read(12))
        #self.precall(self.matrix[-1])
        #self.bgl.seek(off-14,1)

    def SetWrd(self):		# 26
        (var,val)=unpack('<2h',self.bgl.read(4))
        self.vars[var]=val

    def GResList(self):		# 29
        (index,count)=unpack('<2H', self.bgl.read(4))
        for i in range(index,index+count):
            (x,y,z,nx,ny,nz)=unpack('<6h', self.bgl.read(12))
            self.vtx[i]=(x,y,z, nx/32767.0,ny/32767.0,nz/32767.0, 0,0)

    def FaceT(self):		# 1d:Face, 2a:GFaceT, 3e:FaceT
        (count,)=unpack('<H', self.bgl.read(2))
        if self.cmd==0x1d: self.bgl.read(6)	# point
        (fnx,fny,fnz)=unpack('<3h', self.bgl.read(6))
        if count<=4: self.concave=False	# Don't bother
        fnx=fnx/32767.0
        fny=fny/32767.0
        fnz=fnz/32767.0
        if self.cmd!=0x1d: self.bgl.read(4)	# dot_ref
        vtx=[]
        maxy=-maxint
        for i in range(count):
            (idx,)=unpack('<H', self.bgl.read(2))
            (x,y,z,nx,ny,nz,c,c)=self.vtx[idx]
            maxy=max(maxy,y)
            if self.billboard:
                vtx.append((x,y,z, 0,1,0, x*self.scale/256, z*self.scale/256))
            elif self.cmd==0x2a:
                vtx.append((x,y,z, nx,ny,nz, x*self.scale/256, z*self.scale/256))
            else:
                vtx.append((x,y,z, fnx,fny,fnz, x*self.scale/256, z*self.scale/256))
        if count<3: return	# wtf?
        (key,mat)=self.makekey(self.cmd!=0x1d)
        if not key in self.objdat and self.makepoly(False, vtx):	# don't generate poly if there's already geometry here
            return
        if self.concave:
            self.concave=False
            (vtx,idx)=subdivide(vtx)
            if not vtx:
                if self.debug: self.debug.write("!Subdivision failed\n")
                return
        else:
            idx=[]
            for i in range(1,len(vtx)-1):
                idx.extend([0,i,i+1])
        # Change order if necessary to face in direction of normal
        (x0,y0,z0,c,c,c,c,c)=vtx[idx[0]]
        (x1,y1,z1,c,c,c,c,c)=vtx[idx[1]]
        (x2,y2,z2,c,c,c,c,c)=vtx[idx[2]]
        (x,y,z)=cross((x1-x0,y1-y0,z1-z0), (x2-x0,y2-y0,z2-z0))
        if dot((x,y,z), (fnx,fny,fnz))>0:
            idx.reverse()
        if maxy+self.alt <= groundfudge:
            mat.poly=True
        if not key in self.objdat:
            self.objdat[key]=[]
            self.keys.append(key)
        self.objdat[key].append((mat, vtx, idx))
        self.checkmsl()
        
    def SColor24(self):		# 2d: SColor24
        (r,a,g,b)=unpack('4B', self.bgl.read(4))
        if a==0xf0:	# unicol
            self.mat=[Material(self.output.xpver, self.unicol(0xf000+r))]
            self.m=0
        elif (a>=0xb0 and a<=0xb7) or (a>=0xe0 and a<=0xe7):
            # E0 = transparent ... EF=opaque. Same for B?
            # Treat semi-transparent as fully transparent
            self.mat=[]
            self.m=None
        else:
            self.mat=[Material(self.output.xpver, (r/255.0,g/255.0,b/255.0))]
            self.m=0
        
    def LColor24(self):		# 2e: SColor24
        (r,a,g,b)=unpack('4B', self.bgl.read(4))
        if a==0xf0:	# unicol
            self.lightcol=self.unicol(0xf000+r)
        elif (a>=0xb0 and a<=0xb7) or (a>=0xe0 and a<=0xe7):
            # E0 = transparent ... EF=opaque. Same for B?
            # Treat semi-transparent as fully transparent
            self.lightcol=None
        else:
            self.lightcol=(r/255.0,g/255.0,b/255.0)

    def Scale(self):		# 2f
        self.makename()
        self.bgl.read(8)	# jump,range (LOD) (may be 0),size,reserved
        (scale,)=unpack('<I', self.bgl.read(4))
        self.scale=65536.0/scale
        (lat,lon,self.altmsl)=self.LLA()
        self.alt=0
        if __debug__:
            if self.debug: self.debug.write("AltMSL %.3f\n" % self.altmsl)
        if lat>=-90 and lat<=90 and lon>=-180 and lon<=180:
            self.loc=Point(lat,lon)
            if lat<0 and not self.output.hemi:
                self.output.hemi=1
                self.setseason()
        else:	# bogus
            if __debug__:
                if self.debug: self.debug.write("!Bogus Location %s\n" % Point(lat,lon))
            self.loc=None

    def Instance(self):		# 33
        (off,p,b,h)=unpack('<h3H', self.bgl.read(8))
        if not off: raise struct.error	# infloop
        self.precall(True)
        p=p*360/65536.0
        b=b*360/65536.0
        h=h*360/65536.0
        newmatrix=Matrix()
        newmatrix=newmatrix.headed(h)
        newmatrix=newmatrix.pitched(p)
        newmatrix=newmatrix.banked(b)
        if __debug__:
            if self.debug:
                self.debug.write("Instance\n")
                if self.matrix[-1]:
                    self.debug.write("Old\n%s\n" % self.matrix[-1])
                    self.debug.write("New\n%s\n" % newmatrix)
        if self.matrix[-1]:
            newmatrix=newmatrix*self.matrix[-1]
        self.matrix.append(newmatrix)
        if __debug__:
            if self.debug: self.debug.write("Now\n%s\n" % self.matrix[-1])
        self.bgl.seek(off-10,1)

    def SuperScale(self):	# 34
        self.bgl.read(6)	# jump,range (LOD) (may be 0),size
        (scale,)=unpack('<H', self.bgl.read(2))
        if scale>31:
            self.scale=65536.0/self.getvar(scale)
        else:
            self.scale=1.0/pow(2,16-scale)
        
    def PntRow(self):		# 35
        (sx,sy,sz,ex,ey,ez,count)=unpack('<6hH', self.bgl.read(14))
        if count>1:
            dx=(ex-sx)/(count-1.0)
            dy=(ey-sy)/(count-1.0)
            dz=(ez-sz)/(count-1.0)
        else:
            dx=dy=dz=0
        (key,mat)=self.makekey(False)
        if not key in self.lightdat:
            self.lightdat[key]=[]
            self.keys.append(key)
        for i in range(count):
            self.lightdat[key].append(((sx+i*dx,sy+i*dy,sz+i*dz), self.lightcol))
        self.checkmsl()
        
    def Point(self):		# 37
        (x,y,z)=unpack('<3h', self.bgl.read(6))
        (key,mat)=self.makekey(False)
        if not key in self.lightdat:
            self.lightdat[key]=[]
            self.keys.append(key)
        self.lightdat[key].append(((x,y,z), self.lightcol))
        if __debug__:
            if self.debug: self.debug.write("%s %s\n" % ((x,y,z), self.lightcol))
        self.checkmsl()

    def Concave(self):		# 38
        self.concave=True

    def IfMsk(self):		# 39
        (off, var)=unpack('<2h', self.bgl.read(4))
        (mask,)=unpack('<H', self.bgl.read(2))
        val=self.getvar(var)
        if val&mask==0:
            if not off: raise struct.error	# infloop
            self.bgl.seek(off-8,1)

    def VInstance(self):	# 3b
        (off,var)=unpack('<hH', self.bgl.read(4))
        if not off: raise struct.error	# infloop
        self.precall(True)
        p=self.getvar(var)
        p=self.getvar(var)*360/65536.0
        b=self.getvar(var+2)*360/65536.0
        h=self.getvar(var+4)*360/65536.0
        newmatrix=Matrix()
        newmatrix=newmatrix.headed(h)
        newmatrix=newmatrix.pitched(p)
        newmatrix=newmatrix.banked(b)
        if self.debug:
            self.debug.write("VInstance\n")
            if self.matrix[-1]:
                self.debug.write("Old\n%s\n" % self.matrix[-1])
                self.debug.write("New\n%s\n" % newmatrix)
        if self.matrix[-1]:
            newmatrix=newmatrix*self.matrix[-1]
        if __debug__:
            if self.debug: self.debug.write("Now\n%s\n" % self.matrix[-1])
        self.matrix.append(newmatrix)
        self.bgl.seek(off-6,1)

    def Position(self):		# 3c
        self.makename()
        self.bgl.read(8)	# jump,range (LOD) (may be 0),size,reserved
        (lat,lon,self.altmsl)=self.LLA()
        self.alt=0
        if __debug__:
            if self.debug: self.debug.write("Position %s\n" % self.altmsl)
        if lat>=-90 and lat<=90 and lon>=-180 and lon<=180:
            pt=Point(lat,lon)
            if self.loc:
                (x,y,z)=Matrix().headed(self.loc.headingto(pt)).rotate(0,0,self.loc.distanceto(pt))
                if self.matrix[-1]:
                    if __debug__:
                        if self.debug: self.debug.write("Old\n%s\n" % self.matrix[-1])
                    self.matrix[-1]=self.matrix[-1].offset(x,0,z)
                else:
                    self.matrix[-1]=Matrix().offset(x,0,z)
                if __debug__:
                    if self.debug:
                        self.debug.write("New\n%s\n" % self.matrix[-1])
                        self.debug.write("Now\n%s\n" % Matrix().offset(x,0,z))
            else:
                self.loc=pt
        elif __debug__:
            if self.debug: self.debug.write("!Bogus Location %s\n" % Point(lat,lon))
        self.checkmsl()

    def ShadowVPosition(self):	# 40
        self.bgl.read(10)	# ignore
        
    def TextureRunway(self):	# 42: PolygonRunway, 44:TextureRunway
        # ignored - info should now be in FS2004-style BGL
        #self.old=True
        #self.bgl.seek(62,1)	# SDK lies
        
        # runways should now be in FS2004-style BGL. But this command is
        # sometimes used to put back lights on an excluded runway
        (lat,lon,alt)=self.LLA()
        cloc=Point(lat,lon)
        if not (lat>=-90 and lat<=90 and lon>=-180 and lon<=180):
            if __debug__:
                if self.debug: self.debug.write("!Bogus Runway location %s\n"%cloc)
            raise struct.error
        (heading, length, width, markers, identifiers, surface_lights, specials, surface_type, threshold_flags, base_threshold, base_blast_pad, recip_threshold, recip_blast_pad)=unpack('<HHHBBBBBBHHHH', self.bgl.read(20))
        heading=heading*(360.0/65536)
        length=length/m2f	# includes displaced threshold
        width=width/m2f
        displaced=[base_threshold/m2f, recip_threshold/m2f]
        overrun=[base_blast_pad/m2f, recip_blast_pad/m2f]
        if surface_type==255:	# Transparent
            surface=15
        elif surface_type>8:
            surface=1
        else:
            surface=[4,2,1,3,5,5,1,2,14][surface_type]
        if markers&0x80 and surface<=2:
            shoulder=surface
        else:
            shoulder=0
        smoothing=0.25
        if surface_lights&3:
            edgelights=2	# LOW and HIGH not supported in 8.50
        else:
            edgelights=0
        if surface_lights&0xC:
            centrelights=1
        else:
            centrelights=0
        distance=0
        loc=[cloc.biased(-sin(radians(heading))*length/2,
                         -cos(radians(heading))*length/2),
             cloc.biased( sin(radians(heading))*length/2,
                          cos(radians(heading))*length/2)]
        number=["%02d" % (identifiers&63), "%02d" % (((identifiers&63)+18)%36)]
        if number[0]=='00': number[0]='36'
        if number[1]=='00': number[1]='36'
        number[0]=number[0]+[' ','L','R','C'][identifiers/64]
        number[1]=number[1]+[' ','R','L','C'][identifiers/64]
        angle=[3,3]
        if markers&0x44:	# precision or touchdown
            markings=[3,3]
        elif markers&2:		# threshold
            markings=[2,2]
        elif markers&0x30:	# ident or dashes
            markings=[1,1]
        else:
            markings=[0,0]
        if specials&0x08: markings[1]=0		# single end - no markings
        #if specials&0x10: markings[0]=7	# not supported in 8.50
        if specials&0x10: markings[0]=0		# base  closed - no markings
        #if specials&0x20: markings[1]=7	# not supported in 8.50
        if specials&0x2000: markings[1]=0	# recip closed - no markings
        lights=[0,0]
        tdzl=[0,0]
        reil=[0,0]
        for end in [0,1]:
            (flags, system, strobes, vasi_system, vasi_angle, vasi_x, vasi_z, vasi_spacing)=unpack('<BBBBHHHH', self.bgl.read(12))
            # ignore vasi - hope it's specified in XML
            if flags&5:
                reil[end]=1
            if flags&40:
                tdzl[end]=1
            if system>10:
                lights[end]=0
            else:
                lights[end]=[0,11,9,8,6,5,1,1,12,3,4][system]
            # UK-style markings if Calvert approach lights
            if lights[end] in [3,4] and markings[end] in [2,3]:
                markings[end]=markings[end]+2

        # Recalculate centre ignoring displaced thresholds
        clen=(displaced[0]+length-displaced[1])/2
        cloc=loc[0].biased(sin(radians(heading))*clen,
                           cos(radians(heading))*clen)
        txt="%5.2f %02d %02d %4.2f %d %d %d" % (width, surface, shoulder, smoothing, centrelights, edgelights, distance)
        for end in [0,1]:
            txt=txt+(" %-3s %12.8f %13.8f %5.1f %5.1f %02d %02d %d %d" % (number[end], loc[end].lat, loc[end].lon, displaced[end], overrun[end], markings[end], lights[end], tdzl[end], reil[end]))
        self.output.misc.append((100, cloc, [AptNav(100, txt)]))

    def Texture2(self):		# 43
        self.surface=True	# StrRes/CntRes does surface not lines
        (size,dummy,flags,dummy,dummy)=unpack('<HHBBI', self.bgl.read(10))
        tex=self.bgl.read(size-12)
        # This is often incorrectly implemented - texture name can overrun. So read on up to first non-null.
        while '\0' not in tex:
            # Hope we're not at end of area - cos this will overrun.
            tex=tex+self.bgl.read(1)
        tex=findtex(tex.split('\0')[0].rstrip(), self.texdir, self.output.addtexdir)
        if tex and flags&128:
            (lit,ext)=splitext(tex)
            lit=findtex(lit+'_lm', self.texdir, self.output.addtexdir)
        else:
            lit=None
        self.tex=[tex and Texture(self.output.xpver, tex, lit) or None]
        self.t=0
        if __debug__:
            if self.debug: self.debug.write("%s\n" % self.tex[0])
        
    def PointVICall(self):	# 46
        (off,x,y,z,p,vp,b,vb,h,vh)=unpack('<4h6H', self.bgl.read(20))
        if not off: raise struct.error	# infloop
        #if __debug__:
        #    if self.debug: self.debug.write("PointVICall %d %d %d %d %d %d %d %d %d\n" % (x,y,z,p,vp,b,vb,h,vh))
        self.precall(True)
        p=p*360/65536.0
        b=b*360/65536.0
        h=h*360/65536.0
        newmatrix=Matrix()
        newmatrix=newmatrix.offset(x,y,z)
        newmatrix=newmatrix.headed(h+self.getvar(vh))
        newmatrix=newmatrix.pitched(p+self.getvar(vp))
        newmatrix=newmatrix.banked(b+self.getvar(vb))
        if __debug__:
            if self.debug:
                self.debug.write("PointVICall\n")
                if self.matrix[-1]:
                    self.debug.write("Old\n%s\n" % self.matrix[-1])
                    self.debug.write("New\n%s\n" % newmatrix)
        if self.matrix[-1]:
            newmatrix=newmatrix*self.matrix[-1]
        self.matrix.append(newmatrix)
        if __debug__:
            if self.debug: self.debug.write("Now\n%s\n" % self.matrix[-1])
        self.bgl.seek(off-22,1)

    def Building(self):		# 49
        (info,codes,x,y,z,stories,
         size_x,size_z)=unpack('<8h', self.bgl.read(16))
        incx=incz=0
        heights=[stories*4,0,0,4]
        texs=[0,0,0,0]
        if info>=0:
            typ=(info>>3)&3
            texs=[[62,66,38,46,54,66,62,54][info&7],0,0,
                  [ 7,28, 8,26,30,28, 7,30][info&7],
                  [ 7,28, 8,26,30,28, 7,30][info&7],
                  [ 7,28, 8,26,30,28, 7,30][info&7]]
        else:
            # Custom texture - how does that work?
            typ=info&3
        if typ==1:
            roof=3	# slanty
        elif typ==2:
            roof=0
            incx=incz=pi*22.5/180
        else:
            roof=0
        newobj=None
        name="%s-generic-%d" % (asciify(basename(self.srcfile)[:-4]), len(self.gencount)+1)
        if typ==3:
            foo=(8,size_x, size_z, tuple(heights), tuple(texs))
            if foo in self.gencache:
                name=self.gencache[foo]
            else:
                newobj=makegenmulti(name, self.output, *foo)
        else:
            foo=(size_x, size_z, incx, incz, tuple(heights), tuple(texs), roof)
            if foo in self.gencache:
                name=self.gencache[foo]
            else:
                newobj=makegenquad(name, self.output, *foo)
        if newobj:
            self.output.objdat[name]=[newobj]
            self.gencache[foo]=name
        if self.matrix[-1]:
            heading=self.matrix[-1].heading()	# not really
            # handle translation
            loc=self.loc.biased(self.matrix[-1].m[3][0]*self.scale,
                                -self.matrix[-1].m[3][2]*self.scale)
        else:
            heading=0
            loc=self.loc
        self.output.objplc.append((loc, heading, self.complexity, name, 1))
            
    def VScale(self):		# 4c
        # ignore and hope another command sets location
        self.bgl.read(8)	# jump,range (LOD) (may be 0),size,reserved
        (scale,var)=unpack('<Ih', self.bgl.read(6))
        self.scale=65536.0/scale
        self.loc=None

    def MoveL2G(self):		# 4d:MoveL2G, 4e:MoveG2L
        (to, fr)=unpack('<2H', self.bgl.read(4))
        val=self.getvar(fr)
        self.vars[to]=val
        if __debug__:
            if self.debug: self.debug.write("%x<-%x = %d\n" % (to, fr, val))
        
    def LColor(self):		# 51
        (c,)=unpack('H', self.bgl.read(2))
        self.lightcol=self.unicol(c)

    def SurfaceType(self):	# 55
        (sfc, x, z, alt)=unpack('<Hhhh', self.bgl.read(8))
        if sfc!=0: return
        # Smooth surface
        if self.matrix[-1]:
            heading=self.matrix[-1].heading()	# not really
        else:
            heading=0
        length=m2f*x*self.scale
        width=m2f*z*self.scale
        if __debug__:
            if self.debug: self.debug.write("SurfaceType %d (%dx%d) %d\n" % (
                sfc, length, width, alt))

    def TextureRepeat(self):	# 5d
        (x,c,y)=unpack('<3h', self.bgl.read(6))
        self.t=0
        if __debug__:
            if self.debug and (x or y): self.debug.write("!Tex offsets %d,%d\n" % (x,y))
        
    def IfSizeV(self):		# 5f:IfSizeV, 6d:IfSizeH
        # Go for max detail and let X-Plane remove based on it's own heuristics
        (off, a, b)=unpack('<3h', self.bgl.read(6))

    def IfVis(self):		# 62
        # Go for max detail and let X-Plane remove based on it's own heuristics
        (off, count)=unpack('<hH', self.bgl.read(4))
        self.bgl.seek(2*count,1)

    def LibraryCall(self):	# 63
        (off,a,b,c,d)=unpack('<hIIII', self.bgl.read(18))
        name="%08x%08x%08x%08x" % (a,b,c,d)
        if name in self.output.friendly:
            friendly=self.output.friendly[name]
        elif name in self.output.stock:
            friendly=self.output.stock[name]
        else:
            friendly=name
        if self.matrix[-1]:
            heading=self.matrix[-1].heading()	# not really
            scale=self.matrix[-1].scale()*self.scale
            # handle translation
            loc=self.loc.biased(self.matrix[-1].m[3][0]*scale,
                                -self.matrix[-1].m[3][2]*scale)
        else:
            heading=0
            scale=self.scale
            loc=self.loc
        if __debug__:
            if self.debug: self.debug.write("LibraryCall %s %s %.2f %.2f\n%s\n" % (name,friendly,heading,scale,self.matrix[-1]))
        if self.libname:
            # recursive call in library
            (mdlformat, bglname, realfile, offset, size, name, libscale)=self.output.libobj[name]
            if bglname==self.srcfile:
                # Hack: Just include in library objects defined in same file
                self.start=min(self.start,offset)
                self.enda=max(self.enda,offset+size)
                self.precall(False)
                self.bgl.seek(offset)
                return
            else:
                self.output.log('Unsupported request for object %s in %s' % (friendly, self.comment))
                return
        if not self.loc:
            # no location for library object!
            if __debug__:
                if self.debug: self.debug.write("!No location\n")
            return
        if friendly in self.output.subst:
            (name, biasX, biasZ, biasH)=self.output.subst[friendly]
            h1=radians(heading)
            loc=loc.biased(cos(h1)*biasX+sin(h1)*biasZ,
                           cos(h1)*biasZ-sin(h1)*biasX)
            heading=(heading+biasH)%360
        self.output.objplc.append((loc, heading, self.complexity,
                                   name, round(scale,2)))
        if self.altmsl:
            self.output.log('Absolute altitude (%sm) for object %s at (%12.8f, %13.8f) in %s' % (round(self.altmsl,2), friendly, self.loc.lat, self.loc.lon, self.comment))
        elif self.alt:
            self.output.log('Non-zero altitude (%sm) for object %s at (%12.8f, %13.8f) in %s' % (round(self.alt,2), friendly, self.loc.lat, self.loc.lon, self.comment))

    def RoadStart(self):	# 69
        (width,x,y,z)=unpack('<hhhh', self.bgl.read(8))
        width=width*self.scale*2
        if width>=10 or width<=-10:	# arbitrary
            self.linktype=('VEHICLE', width, 'TRUE')
        else:
            self.linktype=('VEHICLE', width, 'FALSE')
        if not (-1<width<=1):
            self.nodes.append(TaxiwayPoint(self.loc.biased(x*self.scale, z*self.scale)))

    def RoadCont(self):		# 6a:RoadCont, 6f:TaxiwayCont
        (x,y,z)=unpack('<hhh', self.bgl.read(6))
        (type, width, centerline)=self.linktype
        if type and not (-1<=width<=1):
            node=self.loc.biased(x*self.scale, z*self.scale)
            if node!=self.nodes[-1]:
                self.nodes.append(TaxiwayPoint(node))
                self.links.append(TaxiwayPath(type, width, centerline, len(self.nodes)-2,len(self.nodes)-1))

    def RiverStart(self):	# 6b
        # ignored
        self.bgl.seek(8,1)
        
    def RiverCont(self):	# 6c
        # ignored
        self.bgl.seek(6,1)

    def TaxiwayStart(self):	# 6e
        (width,x,y,z)=unpack('<hhhh', self.bgl.read(8))
        self.linktype=('TAXI', width*self.scale*2, 'FALSE')
        self.nodes.append(TaxiwayPoint(self.loc.biased(x*self.scale, z*self.scale)))

    def AreaSense(self):	# 70
        # Assume inside
        (off,n)=unpack('<hH', self.bgl.read(4))
        self.bgl.seek(4*n,1)	# skip

    def AddCat(self):		# 74
        (off,cat)=unpack('<2h', self.bgl.read(4))
        if not off: raise struct.error	# infloop
        self.precall(False)
        if __debug__:
            if self.debug: self.debug.write("Layer %d\n" % cat)
        self.layer=cat
        self.bgl.seek(off-6,1)

    def ScaleAGL(self):		# 77
        self.makename()
        self.bgl.read(8)	# jump,range (LOD) (may be 0),size,reserved
        (scale,)=unpack('<I', self.bgl.read(4))
        self.scale=65536.0/scale
        (lat,lon,self.alt)=self.LLA()
        self.altmsl=0
        if __debug__:
            if self.alt and self.debug: self.debug.write("!Altitude %.3f\n" % self.altmsl)	# docs say alt should be 0
        if lat>=-90 and lat<=90 and lon>=-180 and lon<=180:
            self.loc=Point(lat,lon)
            if lat<0 and not self.output.hemi:
                self.output.hemi=1
                self.setseason()
        else:
            if __debug__:
                if self.debug: self.debug.write("!Bogus Location %s\n" % Point(lat,lon))
            self.loc=None
        
    def ResPnt(self):		# 80
        (idx,)=unpack('<H', self.bgl.read(2))
        (x,y,z,c,c,c,c,c)=self.vtx[idx]
        (key,mat)=self.makekey(False)
        if not key in self.lightdat:
            self.lightdat[key]=[]
            self.keys.append(key)
        self.lightdat[key].append(((x,y,z), self.lightcol))
        self.checkmsl()
        
    def Call32(self):		# 2b:AddObj32, 8a:Call32
        (off,)=unpack('<i', self.bgl.read(4))
        if not off: raise struct.error	# infloop
        self.precall(False)
        self.bgl.seek(off-6,1)

    def AddCat32(self):		# 8b
        (off,cat)=unpack('<ih', self.bgl.read(6))
        if not off: raise struct.error	# infloop
        self.precall(False)
        if __debug__:
            if self.debug: self.debug.write("Layer %d\n" % cat)
        self.layer=cat
        self.bgl.seek(off-8,1)

    def ReScale(self):		# 83
        self.bgl.read(6)	# jump,range (LOD) (may be 0),size
        (scale,)=unpack('<I', self.bgl.read(4))
        #print hex(self.bgl.tell()),self.scale, scale, 65536.0/scale, scale/65536.0
        self.scale=self.scale*65536.0/scale

    def Jump32(self):		# 88
        (off,)=unpack('<i', self.bgl.read(4))
        if not off: raise struct.error	# infloop
        self.bgl.seek(off-6,1)

    def CrashIndirect(self):	# 95
        # Ignore - we'll see the drawing code anyway
        self.bgl.read(8)

    def CrashStart(self):	# 96
        # Skip real crash code
        (off,)=unpack('<h', self.bgl.read(2))
        if not off: raise struct.error	# infloop
        self.bgl.seek(off-4,1)
        
    def Interpolate(self):	# 9e
        # Ignored
        if __debug__:
            if self.debug: self.debug.write("!Interpolate\n")
        self.anim=True
        self.bgl.read(18)

    def Object(self):		# a0
        (size,typ)=unpack('<HH', self.bgl.read(4))
        roof=0
        if typ==4:
            # flat
            (size_x,size_z,
             bottom_texture,size_bot_y,tindex_bot_x,tindex_bot_z,
             window_texture,size_win_y,tindex_win_x,tindex_win_y,tindex_win_z,
             top_texture,size_top_y,tindex_top_x,tindex_top_z,
             roof_texture,tindex_roof_x,tindex_roof_z)=unpack('<18H', self.bgl.read(36))
            roof=0
            size_x *= self.scale
            size_z *= self.scale
            incx=incz=0
            heights=[self.scale*size_bot_y,self.scale*size_win_y,self.scale*size_top_y]
            texs=[bottom_texture, window_texture, top_texture, roof_texture]
        elif typ==7:
            # pointy
            (size_x,size_z,
             bottom_texture,size_bot_y,tindex_bot_x,tindex_bot_z,
             window_texture,size_win_y,tindex_win_x,tindex_win_y,tindex_win_z,
             top_texture,size_top_y,tindex_top_x,tindex_top_z,
             roof_texture,tindex_roof_x,tindex_roof_z,size_roof_y,tindex_roof_y)=unpack('<20H', self.bgl.read(40))
            roof=1
            size_x *= self.scale
            size_z *= self.scale
            incx=incz=0
            heights=[self.scale*size_bot_y,self.scale*size_win_y,self.scale*size_top_y,self.scale*size_roof_y]
            texs=[bottom_texture, window_texture, top_texture, roof_texture]
        elif typ==6:
            # gabled
            (size_x,size_z,
             bottom_texture,size_bot_y,tindex_bot_x,tindex_bot_z,
             window_texture,size_win_y,tindex_win_x,tindex_win_y,tindex_win_z,
             top_texture,size_top_y,tindex_top_x,tindex_top_z,
             roof_texture,tindex_roof_x,tindex_roof_z,size_roof_y,
             tindex_gable_y,gable_texture,tindex_gable_z)=unpack('<22H', self.bgl.read(44))
            roof=2
            size_x *= self.scale
            size_z *= self.scale
            incx=incz=0
            heights=[self.scale*size_bot_y,self.scale*size_win_y,self.scale*size_top_y,self.scale*size_roof_y]
            texs=[bottom_texture, window_texture, top_texture, roof_texture, gable_texture]
        elif typ==8:
            # slanty
            (size_x,size_z,
             bottom_texture,size_bot_y,tindex_bot_x,tindex_bot_z,
             window_texture,size_win_y,tindex_win_x,tindex_win_y,tindex_win_z,
             top_texture,size_top_y,tindex_top_x,tindex_top_z,
             roof_texture,tindex_roof_x,tindex_roof_z,size_roof_y,
             tindex_gable_y,gable_texture,tindex_gable_z,
             face_texture,tindex_face_x,tindex_face_y)=unpack('<25H', self.bgl.read(50))
            roof=3
            size_x *= self.scale
            size_z *= self.scale
            incx=incz=0
            heights=[self.scale*size_bot_y,self.scale*size_win_y,self.scale*size_top_y,self.scale*size_roof_y]
            texs=[bottom_texture, window_texture, top_texture, roof_texture, gable_texture,face_texture]
        elif typ==9:
            # flat pyramid
            (base_size_x,base_size_z,top_size_x,top_size_z,
             bottom_texture,size_bot_y,tindex_bot_x,tindex_bot_z,
             window_texture,size_win_y,tindex_win_x,tindex_win_y,tindex_win_z,
             top_texture,size_top_y,tindex_top_x,tindex_top_z,
             roof_texture,tindex_roof_x,tindex_roof_z)=unpack('<20H', self.bgl.read(40))
            roof=0
            size_x=self.scale*base_size_x
            size_z=self.scale*base_size_z
            h2=2*(size_bot_y+size_win_y+size_top_y)
            incx=atan((base_size_x-top_size_x)/h2)
            incz=atan((base_size_z-top_size_z)/h2)
            heights=[self.scale*size_bot_y,self.scale*size_win_y,self.scale*size_top_y]
            texs=[bottom_texture, window_texture, top_texture, roof_texture]
        elif typ in [10,11]:
            # pointy multi - note docs are incorrect
            (sides,spare,size_x,size_z,
             bottom_texture,size_bot_y,tindex_bot_x,
             window_texture,size_win_y,tindex_win_x,tindex_win_y,
             top_texture,size_top_y,tindex_top_x,
             roof_texture,size_roof_y,tindex_roof_x,tindex_roof_yz)=unpack('<BB16H', self.bgl.read(34))
            roof=1
            size_x *= self.scale
            size_z *= self.scale
            incx=incz=0
            heights=[self.scale*size_bot_y,self.scale*size_win_y,self.scale*size_top_y,self.scale*size_roof_y]
            texs=[bottom_texture, window_texture, top_texture, roof_texture]
        elif typ==0x209:
            # windsock
            self.bgl.seek(size-8,1)
            (lit,)=unpack('<H', self.bgl.read(2))
            if lit: lit=1
            self.output.misc.append((19, self.loc, [AptNav(19, '%12.8f %13.8f %d Windsock' %(self.loc.lat, self.loc.lon, lit))]))
            return
        elif typ==0x26c:
            # effect
            end=self.bgl.tell()+size-6
            name=self.bgl.read(80).strip('\0').lower()
            if not name in effects:
                self.output.log('Unsupported effect "%s" at (%12.8f, %13.8f) in %s' % (name, self.loc.lat, self.loc.lon, self.comment))
            else:
                (key,mat)=self.makekey(False)
                if not key in self.effectdat:
                    self.effectdat[key]=[]
                    self.keys.append(key)
                self.effectdat[key].append(((0,0,0), effects[name]))
                self.checkmsl()
            self.bgl.seek(end)
            return
        else:
            self.output.log('Unsupported effect at (%12.8f, %13.8f) in %s' % (self.loc.lat, self.loc.lon, self.comment))
            self.bgl.seek(size-6,1)
            return

        if self.matrix[-1]:
            heading=self.matrix[-1].heading()	# not really
            # handle translation
            loc=self.loc.biased(self.matrix[-1].m[3][0]*self.scale,
                                -self.matrix[-1].m[3][2]*self.scale)
        else:
            heading=0
            loc=self.loc
        newobj=None
        name="%s-generic-%d" % (asciify(basename(self.srcfile)[:-4]), len(self.gencount)+1)
        if typ in [10,11]:
            foo=(sides, size_x, size_z, tuple(heights), tuple(texs))
            if foo in self.gencache:
                name=self.gencache[foo]
            else:
                newobj=makegenmulti(name, self.output, *foo)
        else:
            foo=(size_x, size_z, incx, incz, tuple(heights), tuple(texs), roof)
            if foo in self.gencache:
                name=self.gencache[foo]
            else:
                newobj=makegenquad(name, self.output, *foo)
        if newobj:
            self.output.objdat[name]=[newobj]
            self.gencache[foo]=name
        self.output.objplc.append((loc, heading, self.complexity, name, 1))
        if self.altmsl:
            pass
            #self.output.log('Absolute altitude (%sm) for generic building %s at (%12.8f, %13.8f) in %s' % (round(self.altmsl,2), name, self.loc.lat, self.loc.lon, self.comment))
        elif self.alt:
            self.output.log('Non-zero altitude (%sm) for generic building %s at (%12.8f, %13.8f) in %s' % (round(self.alt,2), name, self.loc.lat, self.loc.lon, self.comment))

    def TargetIndicator(self):	# a6 - used by Aerosoft
        (x,y,z)=unpack('<3h', self.bgl.read(6))

    def SpriteVICall(self):	# a7
        (off,x,y,z,p,b,h,vp,vb,vh)=unpack('<4h6H', self.bgl.read(20))
        if not off: raise struct.error	# infloop
        self.precall(True)
        newmatrix=Matrix()
        newmatrix=newmatrix.offset(x,y,z)
        if __debug__:
            if self.debug:
                self.debug.write("SpriteVICall\n")
                if self.matrix[-1]:
                    self.debug.write("Old\n%s\n" % self.matrix[-1])
                    self.debug.write("New\n%s\n" % newmatrix)
        if self.matrix[-1]:
            newmatrix=newmatrix*self.matrix[-1]
        self.matrix.append(newmatrix)
        if __debug__:
            if self.debug: self.debug.write("Now\n%s\n" % self.matrix[-1])
        self.billboard=True
        self.bgl.seek(off-22,1)

    def TextureRoadStart(self):	# a8
        (style,width,x,y,z)=unpack('<Hhhhh', self.bgl.read(10))
        width=width*self.scale*2	# width is in [m]?, ie not scaled?
        if style<=1 and -1<=width<=-1:		# arbitrary - centreline only
            self.linktype=('TAXI', width, 'TRUE')
        elif style<=1 and (width>=10 or width<=-10):	# arbitrary
            self.linktype=('VEHICLE', width, 'TRUE')
        elif style<=1:
            self.linktype=('VEHICLE', width, 'FALSE')
        elif style==2:
            self.linktype=('VEHICLE', width, 'TRUE')
        elif style==3:
            self.linktype=('VEHICLE', width, 'FALSE')
        else:	# railroad or river
            self.rrt=True
            self.linktype=(None, width, 'FALSE')
            return
        if not (-1<=width<=1):
            self.nodes.append(TaxiwayPoint(self.loc.biased(x*self.scale, z*self.scale)))
        
    def NewRunway(self):	# aa
        # runways should now be in FS2004-style BGL. But this command is
        # sometimes used to put back lights on an excluded runway
        (size,op)=unpack('<HB', self.bgl.read(3))
        endop=self.bgl.tell()+size-5
        (lat,lon,alt)=self.LLA()
        cloc=Point(lat,lon)
        if not (lat>=-90 and lat<=90 and lon>=-180 and lon<=180):
            if __debug__:
                if self.debug: self.debug.write("!Bogus Runway location %s\n"%cloc)
            raise struct.error
        (heading, length, width, markers, surface_type, surface_lights, identifiers)=unpack('<HHHHBBB', self.bgl.read(11))
        heading=heading*(360.0/65536)
        length=length/m2f	# includes displaced threshold
        width=width/m2f
        displaced=[0,0]
        overrun=[0,0]
        if surface_type==9:	# Water - ignore
            self.bgl.seek(endop)
            return
        elif surface_type==255:	# Transparent
            surface=15
        elif surface_type>8:
            surface=1
        else:
            surface=[4,2,1,3,5,5,1,2,14][surface_type]
        if markers&0x80 and surface<=2:
            shoulder=surface
        else:
            shoulder=0
        smoothing=0.25
        if surface_lights&3:
            edgelights=2	# LOW and HIGH not supported in 8.50
        else:
            edgelights=0
        if surface_lights&0xC:
            centrelights=1
        else:
            centrelights=0
        distance=0
        loc=[cloc.biased(-sin(radians(heading))*length/2,
                         -cos(radians(heading))*length/2),
             cloc.biased( sin(radians(heading))*length/2,
                          cos(radians(heading))*length/2)]
        number=["%02d" % (identifiers&63), "%02d" % (((identifiers&63)+18)%36)]
        if number[0]=='00': number[0]='36'
        if number[1]=='00': number[1]='36'
        number[0]=number[0]+[' ','L','R','C'][identifiers/64]
        number[1]=number[1]+[' ','R','L','C'][identifiers/64]
        angle=[3,3]
        if markers&0x44:	# precision or touchdown
            markings=[3,3]
        elif markers&2:		# threshold
            markings=[2,2]
        elif markers&0x30:	# ident or dashes
            markings=[1,1]
        else:
            markings=[0,0]            
        if markers&0x0800: markings[1]=0	# single end - no markings
        #if markers&0x1000: markings[0]=7	# not supported in 8.50
        if markers&0x1000: markings[0]=0	# base  closed - no markings
        #if markers&0x2000: markings[1]=7	# not supported in 8.50
        if markers&0x2000: markings[1]=0	# recip closed - no markings
        lights=[0,0]
        tdzl=[0,0]
        reil=[0,0]
        while self.bgl.tell()<endop:
            (op,foo)=unpack('<BB', self.bgl.read(2))
            if op==2:
                (foo,)=unpack('<H', self.bgl.read(2))
                displaced[0]=foo/m2f
            elif op==3:
                (foo,)=unpack('<H', self.bgl.read(2))
                displaced[1]=foo/m2f
            elif op==4 or op==8:
                (foo,)=unpack('<H', self.bgl.read(2))
                overrun[0]=foo/m2f
            elif op==5 or op==9:
                (foo,)=unpack('<H', self.bgl.read(2))
                overrun[1]=foo/m2f
            elif op==10 or op==11:
                (foo,)=unpack('<H', self.bgl.read(2))
                distance=1
            elif op==6 or op==7:
                (flags,system,strobes,vasi_system,vasi_angle,vasi_x,vasi_z,vasi_spacing)=unpack('<BBBBHHHH', self.bgl.read(12))
                # ignore vasi - hope it's specified in XML
                if flags&5:
                    reil[op-6]=1
                if flags&40:
                    tdzl[op-6]=1
                if system>10:
                    lights[op-6]=0
                else:
                    lights[op-6]=[0,11,9,8,6,5,1,1,12,3,4][system]
            else:
                self.bgl.seek(endop)
                if __debug__:
                    if self.debug: self.debug.write("!Unknown NewRunway opcode %x\n" % op)
        # UK-style markings if Calvert approach lights
        for end in [0,1]:
            if lights[end] in [3,4] and markings[end] in [2,3]:
                markings[end]=markings[end]+2

        # Recalculate centre ignoring displaced thresholds
        clen=(displaced[0]+length-displaced[1])/2
        cloc=loc[0].biased(sin(radians(heading))*clen,
                           cos(radians(heading))*clen)
        txt="%5.2f %02d %02d %4.2f %d %d %d" % (width, surface, shoulder, smoothing, centrelights, edgelights, distance)
        for end in [0,1]:
            txt=txt+(" %-3s %12.8f %13.8f %5.1f %5.1f %02d %02d %d %d" % (number[end], loc[end].lat, loc[end].lon, displaced[end], overrun[end], markings[end], lights[end], tdzl[end], reil[end]))
        self.output.misc.append((100, cloc, [AptNav(100, txt)]))

    def ZBias(self):	# ac
        (self.zbias,)=unpack('<H', self.bgl.read(2))

    # opcodes ad to bd new in FS2002

    def Animate(self):		# ad
        # Just make a static translation matrix
        self.anim=True
        (c,c,c,c,x,y,z)=unpack('<4i3f', self.bgl.read(28))
        newmatrix=Matrix()
        newmatrix=newmatrix.offset(x,y,z)
        if __debug__:
            if self.debug:
                self.debug.write("Animate\n")
                if self.matrix[-1]:
                    self.debug.write("Old\n%s\n" % self.matrix[-1])
                    self.debug.write("New\n%s\n" % newmatrix)
        if self.matrix[-1]:
            newmatrix=newmatrix*self.matrix[-1]
        if __debug__:
            if self.debug: self.debug.write("Now\n%s\n" % self.matrix[-1])
        self.matrix.append(newmatrix)

    def TransformEnd(self):	# ae
        self.matrix.pop()
        
    def TransformMatrix(self):	# af
        (x,y,z)=unpack('<3f', self.bgl.read(12))
        (q00,q01,q02, q10,q11,q12, q20,q21,q22)=unpack('<9f',self.bgl.read(36))
        newmatrix=Matrix([[q00,q01,q02,0],
                          [q10,q11,q12,0],
                          [q20,q21,q22,0],
                          [x,y,z,1]])
        if __debug__:
            if self.debug:
                self.debug.write("TransformMatrix\n")
                if self.matrix[-1]:
                    self.debug.write("Old\n%s\n" % self.matrix[-1])
                    self.debug.write("New\n%s\n" % newmatrix)
        if self.matrix[-1]:
            newmatrix=newmatrix*self.matrix[-1]
        self.matrix.append(newmatrix)
        if __debug__:
            if self.debug: self.debug.write("Now\n%s\n" % self.matrix[-1])

    def Tag(self):	# b1
        self.bgl.read(20).rstrip(' \0')	# what's this for?
        
    def Light(self):		# b2
        (typ,x,y,z,intens,i,i,b,g,r,a,i,i,i)=unpack('<HfffIffBBBBfff', self.bgl.read(42))
        # Typical intensities are 20 and 40 - so say 40=max
        if intens<40:
            intens=intens/(40.0*255.0)
        else:
            intens=1/255.0
        (key,mat)=self.makekey(False)
        if not key in self.lightdat:
            self.lightdat[key]=[]
            self.keys.append(key)
        self.lightdat[key].append(((x,y,z), (r*intens,g*intens,b*intens)))
        self.checkmsl()
        
    def IfInF1(self):		# b3
        (off, var, vmin, vmax)=unpack('<2h2f', self.bgl.read(12))
        if vmin>vmax:	# Sigh. Seen in TFFR
            foo=vmax
            vmax=vmin
            vmin=foo
        if var==0x346:
            self.complexity=complexity(vmin)
            if vmax==4: vmax=5	# bug in eg EGNT
        val=self.getvar(var)
        if val<vmin or val>vmax:
            if not off: raise struct.error	# infloop
            self.bgl.seek(off-10,1)

    def VertexList(self):	# b5
        self.vtx=[]
        (count,)=unpack('<H', self.bgl.read(2))
        self.bgl.read(4)
        for i in range(count):
            self.vtx.append(unpack('<8f', self.bgl.read(32)))

    def MaterialList(self):	# b6
        (count,dummy)=unpack('<HI', self.bgl.read(6))
        self.mat=[]
        self.m=None
        for i in range(count):
            (dr,dg,db,da)=unpack('<4f', self.bgl.read(16))
            (ar,ag,ab,aa)=unpack('<4f', self.bgl.read(16))
            self.bgl.read(16*2)			# specular, emissive ignored according to BGLFP.doc
            (p,)=unpack('<f', self.bgl.read(4))	# specular power
            # according to BGLFP.doc ambient is ignored. But in practice seems to hold fallback color for textured materials,
            # and holds same r,g,b values as diffuse for untextured materials. Which makes it a better choice.
            self.mat.append(Material(self.output.xpver, (ar,ag,ab), alphacutoff=(1-da or None)))
        if __debug__:
            if self.debug: self.debug.write("%d materials\n" % len(self.mat))

    def TextureList(self):	# b7
        self.tex=[]
        self.t=None
        (count,)=unpack('<H', self.bgl.read(2))
        self.bgl.read(4)
        for i in range(count):
            (cls,)=unpack('<I', self.bgl.read(4))
            self.bgl.read(12)
            tex=findtex(self.bgl.read(64).rstrip(' \0'), self.texdir, self.output.addtexdir)
            if not cls&0x700 or not self.tex[-1]:
                pass	# Not a multitexture, or no primary texture
            elif cls==0x100:			# NightMap: Blends with diffuse texture
                self.tex[-1].e=tex
            elif cls==0x300 or cls==0x400:	# LightMap: Replaces diffuse texture
                self.tex[-1].e=tex
            elif not self.tex[-1] or self.output.xpver<=10:
                pass	# Remaining options not supported in<=10
            elif cls==0x200:			# RelectMap
                self.tex[-1].r=tex
            self.tex.append(tex and Texture(self.output.xpver, tex, None) or None)
        if __debug__:
            if self.debug: self.debug.write("%d textures\n" % len(self.tex))

    def SetMaterial(self):	# b8
        (self.m,self.t)=unpack('<2h', self.bgl.read(4))
        if self.m>=len(self.mat):
            if __debug__:
                if self.debug: self.debug.write("Bad material %d/%d\n"%(self.m,len(self.mat)))
            self.m=None
        if self.t<0 or self.t>=len(self.tex):
            self.t=None
            if __debug__:
                if self.debug and self.t>=len(self.tex): self.debug.write("Bad texture %d/%d\n" %(self.t,len(self.tex)))
        if __debug__:
            if self.debug: self.debug.write("%s: %s\t%s: %s\n" % (self.m, self.m!=None and self.mat[self.m], self.t, self.t!=None and self.tex[self.t]))
        
    def DrawTriList(self):	# b9
        idx=[]
        (vbase,vcount,icount)=unpack('<3H', self.bgl.read(6))
        if __debug__: self.debug.write("%d, %d, %d\n" % (vbase,vcount,icount))
        vtx=self.vtx[vbase:vbase+vcount]
        idx=unpack('<%dH' % icount, self.bgl.read(2*icount))
        (key,mat)=self.makekey()
        if not key in self.objdat and self.makepoly(True, vtx, idx):	# don't generate poly if there's already geometry here
            return
        maxy=-maxint
        for (x,y,z,nx,ny,nz,tu,tv) in vtx:
            maxy=max(maxy,y)
        if maxy+self.alt <= groundfudge:
            mat.poly=True
        if not key in self.objdat:
            self.objdat[key]=[]
            self.keys.append(key)
        self.objdat[key].append((mat, vtx, idx))
        self.checkmsl()

    def DrawLineList(self):	# ba
        (base,vcount,icount)=unpack('<3H', self.bgl.read(6))
        self.old=True
        self.bgl.seek(2*icount,1)
        
    # opcodes c0 and above new in FS2004

    def SetMatrixIndirect(self):	# c4
        # n=index into SCEN section of MDL file
        (scene,)=unpack('<H', self.bgl.read(2))
        pos=self.bgl.tell()
        self.matrix[-1]=Matrix()

        while scene!=-1:
            (child,peer,size,posa,parent)=self.scen[scene]
            self.bgl.seek(posa)		# Into ANIC section
            (cmd,src,dst)=unpack('<3H', self.bgl.read(6))
            if cmd==0xc6 and size==6:
                self.bgl.seek(self.tran+src*64)
                m=[]
                for j in range(4):
                    (a,b,c,d)=unpack('<4f',self.bgl.read(16))
                    m.append([a,b,c,d])
                # Matrices don't appear to nest - hence [-1]
                self.matrix[-1]=self.matrix[-1]*Matrix(m)
                if __debug__:
                    if self.debug: self.debug.write("Scene %d, %d %d:\n%s\n" % (scene, src,dst, Matrix(m)))
            else:
                if __debug__:
                    if self.debug: self.debug.write("!Unsupported ANIC cmd %x, size %d\n" % (cmd, size))
                self.anim=True
                break
            scene=parent

        if __debug__:
            if self.debug: self.debug.write("TransformIndirect:\n%s\n" % self.matrix[-1])
        self.bgl.seek(pos)


    # Ignored opcodes
    
    def NOP(self):
        # 02:NOOP, 76:BGL, 7d:Perspective, bd:EndVersion
        pass

    def NOPh(self):
        # 30:Brightness, 3f:ShadowCall, 81:AntiAlias, 93: Specular?, a4:VAlpha
        self.bgl.read(2)

    def NOPi(self):
        # 89:VarBase32, 8f:Alpha, 9f:Override, b4: TextureSize, bc:BGLVersion
        self.bgl.read(4)


    # Helpers

    # helper to read lat, lon, alt
    def LLA(self):
        (lo,hi)=unpack('<Hi',self.bgl.read(6))
        if hi>=0:
            lat=hi+lo/65536.0
        else:
            lat=-(~hi+(~lo+1)/65536.0)
        lat=lat*360/cirp
        (lo,hi)=unpack('<Hi',self.bgl.read(6))
        if hi>=0:
            lon=hi+lo/65536.0
        else:
            lon=-(~hi+(~lo+1)/65536.0)
        lon=lon*360.0/0x100000000
        if lon>180: lon-=360
        
        (lo,hi)=unpack('<Hi',self.bgl.read(6))
        if hi>=0:
            alt=hi+lo/65536.0
        else:
            alt=-(~hi+(~lo+1)/65536.0)

        if __debug__:
            self.debug.write("New location: %s %.3f\n" % (Point(lat,lon), alt))
        return (lat,lon,alt)


    # Stack return data prior to a call
    def precall(self, matrix):
        if len(self.stack)>100:		# arbitrary
            if __debug__: self.debug.write("!Recursion limit\n")
            raise struct.error
        self.stack.append((self.bgl.tell(), self.layer, self.billboard, matrix and True))


    def tessbegin(self, typ, polys):
        # New output polygon
        assert typ==GL_LINE_LOOP
        polys.append([[]])

    def tessvertex(self, vertex, polys):
        (x,y,z, nx,ny,nz, tu,tv)=vertex
        polys[-1][0].append((self.loc.biased(x,z), tu,tv))

    tesscombine2=array([0.5,0.5,0,0], GLfloat)
    def tesscombine(self, coords, vertex, weight, polys):
        # two cases:
        # - two co-located vertices: check that UVs match
        # - new vertex: fail - polygon is not simple
        #self.debug.write("combine: %s %s %s\n" % (coords, vertex, weight))
        if not array_equal(weight, ProcScen.tesscombine2) and vertex[0]==vertex[1]:
            if __debug__:
                if self.debug and polys[0]:
                    if not array_equal(weight, ProcScen.tesscombine2):
                        self.debug.write("Non-simple\n")
                    else:
                        self.debug.write("UV mismatch\n")
            polys[0]=False	# Can't raise an exception so do this instead
        return vertex[0]

    def csgtvertex(self, vertex, polys):
        polys[-1][0].append(vertex)

    def csgtcombine(self, coords, vertex, weight, polys):
        # Polygon meets tile border. Need to work out UV coords from polygon vertices.
        #self.debug.write("combine: %s %s %s\n" % (coords, vertex, weight))
        newtu=newtv=0
        cumw=0
        for i in range(4):
            if vertex[i] is None:
                polys[0]=False	# Shouldn't happen - Something went wrong with initial tessellation
                if __debug__:
                    if self.debug: self.debug.write("WTF?\n")
            else:
                (loc, tu, tv)=vertex[i]
                if tu is not None:	# Polygon point not tile border
                    newtu+=tu
                    newtv+=tv
                    cumw +=weight[i]
        return (Point(float(coords[2]), float(coords[0])), newtu/cumw, newtv/cumw)

    # Try to make a draped polygon
    def makepoly(self, haveuv, vtx, idx=None):
        if self.t==None: return False	# Only care about textured polygons
        if not self.loc: return False	# Not for library objects
        if __debug__:
            if self.debug: self.debug.write("Poly: %s %s %s %d " % (self.tex[self.t], self.alt, self.layer, self.zbias))

        # Altitude test on first vertex
        if self.matrix[-1]:
            (x,y,z)=self.matrix[-1].transform(*vtx[idx[0]][:3])
        else:
            (x,y,z)=vtx[idx[0]][:3]
        yval=y*self.scale
        if (self.altmsl and not self.layer) or yval+self.alt>groundfudge:
            if __debug__:
                if self.debug: self.debug.write("Above ground %s\n" % (yval+self.alt))
            return False
        elif __debug__:
            if self.debug: self.debug.write("Ground %s " % (yval+self.alt))

        # Transform & Co-planar test
        newvtx=[]
        minu=minv=maxint
        maxu=maxv=-maxint
        for (x,y,z, nx,ny,nz, tu,tv) in vtx:
            if self.matrix[-1]:
                (x,y,z)=self.matrix[-1].transform(x,y,z)
            if abs(y*self.scale-yval)>planarfudge:
                if __debug__:
                    if self.debug: self.debug.write("Not coplanar\n")
                return False
            minu=min(minu,tu)
            minv=min(minv,tv)
            maxu=max(maxu,tu)
            maxv=max(maxv,tv)
            newvtx.append((x*self.scale,y*self.scale,z*self.scale, nx,ny,nz, tu,tv))
        vtx=newvtx

        TEXFUDGE=0.01
        uvscale=max(0.1,round(self.scale*256, 0))	# Mustn't be zero

        # Check for tiled textures
        if haveuv and (maxu-minu > 1+2*TEXFUDGE or maxv-minv > 1+2*TEXFUDGE):
            # maybe do this test after tessellation - could have some orthos, some repeats, and some objs?
            if maxu-minu <= 1+2*TEXFUDGE or maxv-minv <= 1+2*TEXFUDGE:
                # Texture repeats on only one axis - can't handle this at all since we can either generate ortho with 0<=UVs<=1 or generate fully repeating texture
                if __debug__:
                    if self.debug: self.debug.write("UVs on one axis %.3f,%.3f\n " % (maxu-minu,maxv-minv))
                return False
            if __debug__:
                if self.debug: self.debug.write("Dropping UVs %.3f,%.3f " % (maxu-minu,maxv-minv))
            haveuv=False        # Trim textures that spill over edge
            # Estimate scale, assuming not distorted or disjoint
            (x0,y0,z0, nx0,ny0,nz0, tu0,tv0)=vtx[0]
            for i in range(len(vtx)-1,0,-1):
                (x1,y1,z1, nx1,ny1,nz1, tu1,tv1)=vtx[i]
                if (x0,z0) != (x1,z1):
                    uvscale=max(0.1, hypot(x1-x0, z1-z0) / hypot(tu1-tu0, tv1-tv0))
                    if __debug__:
                        if self.debug: self.debug.write("New UV scale %.1f " % uvscale)
                    break

        # Trim textures that spill over edge
        if haveuv:
            if minu%1 >= 1-TEXFUDGE:
                minu=floor(minu)+1
            else:
                minu=floor(minu)
            if minv%1 >= 1-TEXFUDGE:
                minv=floor(minv)+1
            else:
                minv=floor(minv)

        # Tessellate - two cases:
        # - without idx we have a (potentially convex) polygon described by vtx.
        # - with idx we have a set of triangles (which may have already been tessellated from a larger plane because
        #   FSX doesn't do draping) that may or may not be disjoint.
        tessObj = gluNewTess()
        gluTessNormal(tessObj, 0, -1, 0)
        gluTessProperty(tessObj, GLU_TESS_WINDING_RULE,  GLU_TESS_WINDING_NONZERO)
        gluTessProperty(tessObj, GLU_TESS_BOUNDARY_ONLY, GL_TRUE)
        gluTessCallback(tessObj, GLU_TESS_BEGIN_DATA,    self.tessbegin)
        gluTessCallback(tessObj, GLU_TESS_VERTEX_DATA,   self.tessvertex)
        gluTessCallback(tessObj, GLU_TESS_COMBINE_DATA,  self.tesscombine)
        polys=[True]	# First element is a success value
        try:
            gluTessBeginPolygon(tessObj, polys)
            if idx:
                for i in range(0,len(idx),3):
                    gluTessBeginContour(tessObj)
                    for j in idx[i:i+3]:
                        v=vtx[j]
                        (x,y,z, nx,ny,nz, tu, tv)=v
                        gluTessVertex(tessObj, [x, y, z], v)
                    gluTessEndContour(tessObj)
            else:
                gluTessBeginContour(tessObj)
                for v in vtx:
                    (x,y,z, nx,ny,nz, tu, tv)=v
                    gluTessVertex(tessObj, [x, y, z], v)
                gluTessEndContour(tessObj)
            gluTessEndPolygon(tessObj)
        except:
            gluDeleteTess(tessObj)
            if self.debug: print_exc(None, self.debug)
            raise GLUerror
        gluDeleteTess(tessObj)

        if not polys[0]:
            return False	# Failed
        else:
            polys.pop(0)

        # Output from tessellation is a list of windings.
        # Holes are CW and precede the polygon that contains them. Easier if they're the other way round.
        polys.reverse()
        i=0
        while i<len(polys):
            w=polys[i][0]
            count=len(w)
            area2=0
            for j in range(count):
                area2+=(w[j][0].lat*w[(j+1)%count][0].lon - w[(j+1)%count][0].lat*w[j][0].lon)
            if __debug__:
                self.debug.write("points: %d %s\n" % (count, area2<=0 and 'CCW' or 'CW'))
            if area2>0:
                polys[i-1].append(w)	# Add hole winding to the containing polygon
                polys.pop(i)
            else:
                i+=1

        if haveuv:
            heading=65535
        elif self.matrix[-1] and self.matrix[-1].m[1][1]==1:	# No pitch or bank?
            heading=self.matrix[-1].heading()
        else:
            heading=0

        tex=self.tex[self.t]
        if self.haze and tex.d: self.output.haze[tex.d]=self.haze
        if self.haze and tex.e: self.output.haze[tex.e]=self.haze

        # Adjust for straddling tile boundaries
        for i in range(len(polys)-1,-1,-1):
            points=polys[i]
            w=points[0]	# exterior winding
            minlat=minlon=maxint
            maxlat=maxlon=-maxint
            for (loc,tu,tv) in w:
                minlat=min(minlat,loc.lat)
                minlon=min(minlon,loc.lon)
                maxlat=max(maxlat,loc.lat)
                maxlon=max(maxlon,loc.lon)

            latrange=range(int(floor(minlat)), 1+int(floor(maxlat)))
            lonrange=range(int(floor(minlon)), 1+int(floor(maxlon)))

            # Strictly we don't have to do this tessellation if we don't straddle, but do it anyway as a sanity test
            #if len(latrange)==len(lonrange)==1:
            #    continue	# doesn't straddle a tile border

            # More tessellation, this time in CSG mode
            tessObj = gluNewTess()
            gluTessNormal(tessObj, 0, -1, 0)
            gluTessProperty(tessObj, GLU_TESS_WINDING_RULE,  GLU_TESS_WINDING_ABS_GEQ_TWO)
            gluTessProperty(tessObj, GLU_TESS_BOUNDARY_ONLY, GL_TRUE)
            gluTessCallback(tessObj, GLU_TESS_BEGIN_DATA,    self.tessbegin)
            gluTessCallback(tessObj, GLU_TESS_VERTEX_DATA,   self.csgtvertex)
            gluTessCallback(tessObj, GLU_TESS_COMBINE_DATA,  self.csgtcombine)

            polys.pop(i)
            try:
                for lat in latrange:
                    for lon in lonrange:
                        newpolys=[True]
                        gluTessBeginPolygon(tessObj, newpolys)
                        gluTessBeginContour(tessObj)
                        gluTessVertex(tessObj, [lon,   0, lat],   (Point(lat,   lon),   None, None))
                        gluTessVertex(tessObj, [lon+1, 0, lat],   (Point(lat,   lon+1), None, None))
                        gluTessVertex(tessObj, [lon+1, 0, lat+1], (Point(lat+1, lon+1), None, None))
                        gluTessVertex(tessObj, [lon,   0, lat+1], (Point(lat+1, lon),   None, None))
                        gluTessEndContour(tessObj)
                        for w in points:
                            gluTessBeginContour(tessObj)
                            for p in w:
                                (loc, tu, tv)=p
                                gluTessVertex(tessObj, [loc.lon, 0, loc.lat], p)
                            gluTessEndContour(tessObj)
                        gluTessEndPolygon(tessObj)

                        if not newpolys[0]:
                            return False	# Failed
                        else:
                            newpolys.pop(0)

                        newpolys.reverse()	# So holes follow containing polygon
                        j=0
                        while j<len(newpolys):
                            neww=newpolys[j][0]
                            count=len(neww)
                            area2=0
                            for k in range(count):
                                area2+=(neww[k][0].lat*neww[(k+1)%count][0].lon - neww[(k+1)%count][0].lat*neww[k][0].lon)
                            if area2>0:
                                newpolys[j-1].append(neww)	# Add hole winding to the containing polygon
                                newpolys.pop(j)
                            else:
                                j+=1

                        polys.extend(newpolys)
            except:
                gluDeleteTess(tessObj)
                if self.debug: print_exc(None, self.debug)
                raise GLUerror
            gluDeleteTess(tessObj)

        # Add polygons
        if __debug__:
            if self.debug: self.debug.write("OK\n")
        for points in polys:
            self.polydat.append((points, self.layer, heading, uvscale, tex))

        return True


    # Generate Objects for the current Area or Library object
    def makeobjs(self):

        if self.neednight:
            # Detect night-only objects, e.g. LIEE2008 cag_pc spotlight, and objects that manually change texture at night

            self.effectdat=self.dayeffectdat	# just use daylight effects
            # just use nighttime lights

            nightpolydat=self.polydat
            self.polydat=[]
            for npoly in nightpolydat:
                (npoints, nlayer, nheading, nscale, ntex)=npoly
                for dpoly in self.daypolydat:
                    (points, layer, heading, scale, tex)=dpoly
                    if len(points)==len(npoints) and layer==nlayer and heading==nheading and scale==nscale: break
                    for k in range(len(points)):
                        if points[k][0]!=npoints[k][0] or points[k][1]!=npoints[k][1] or points[k][2]!=npoints[k][2]:
                            break
                    else:
                        break	# dupe
                else:
                    # nighttime-only poly
                    if __debug__:
                        if self.debug: self.debug.write("Night-only poly: %s\n" % ntex)
                    if not ntex.e: ntex=Texture(self.output.xpver, None, ntex.d)	# texture manually managed
                    self.polydat.append((npoints, nlayer, nheading, nscale, ntex))
                    continue
                # Duplicate
                if not tex.e and tex.d!=ntex.d: tex.e=ntex.d	# texture manually managed
            self.polydat.extend(self.daypolydat)

            nightobjdat=self.objdat
            self.objdat=self.dayobjdat
            for nkey in nightobjdat:
                if nkey in self.objdat: continue	# dupe
                (nname, nloc, nlayer, nalt, naltmsl, nmatrix, nscale, ntex)=nkey
                for (name, loc, layer, alt, altmsl, matrix, scale, tex) in self.objdat:
                    if name==nname and loc==nloc and layer==nlayer and alt==nalt and altmsl==naltmsl and matrix==nmatrix and scale==nscale:
                        # Duplicate. TODO: Night-time only geometry?
                        if tex and not tex.e and tex.d!=ntex.d: tex.e=ntex.d	# texture manually managed
                        break
                else:
                    # nighttime-only obj
                    if __debug__:
                        if self.debug: self.debug.write("Night-only obj: %s %s\n" % (nname, ntex))
                    tex=ntex
                    if ntex:
                        if not ntex.e: tex=Texture(self.output.xpver, None, ntex.d)	# texture manually managed
                    elif __debug__:
                        if self.debug: self.debug.write("!Untextured")
                    key=(nname, nloc, nlayer, nalt, naltmsl, nmatrix, nscale, tex)
                    if not key in self.objdat:
                        self.objdat[key]=[]
                        self.keys.append(key)
                    self.objdat[key].extend(nightobjdat[nkey])
                    continue
        
        if not self.lightdat and not self.effectdat and not self.objdat and not self.polydat and not self.links:
            return	# Only contained non-scenery stuff
        elif self.libname:
            if self.loc:
                if self.debug: self.debug.write("!Location given for library object\n")
                raise struct.error	# Code assumes no spurious location
        elif self.loc or self.dayloc:
            if not self.loc: self.loc=self.dayloc
        else:
            # Must have a location for placement
            if self.debug: self.debug.write("!No location\n")
            raise struct.error

        # Do taxiways & roads
        if self.links:
            allnodes = [Node(t) for t in self.nodes]
            names=[TaxiwayName(None)]
            alllinks = [Link(p, 0, names) for p in self.links]
            # replace indices with references, and setup node links
            for l in alllinks:
                for i in [0,1]:
                    l.nodes[i]=allnodes[l.nodes[i]]
                    l.nodes[i].links.append(l)
            taxilayout(allnodes, alllinks, 0, self.output)

        # Do polygons
        for (points, layer, heading, scale, tex) in self.polydat:
            (fname,ext)=splitext(basename(tex.d or tex.e))
            # base and lit textures may not have same case
            if fname[-3:].lower()=='_lm': fname=fname[:-3]+"_LIT"
            if not ext.lower() in ['.dds', '.bmp', '.png']:
                fname+=ext[1:].lower()	# For *.xAF etc
            # Spaces not allowed in textures. Avoid Mac/PC interop problems
            fname=asciify(fname)
            poly=Polygon(fname, tex, heading==65535, scale, layer)
            if fname in self.output.polydat:
                iname=fname
                i=0
                while True:
                    # See if this is a duplicate
                    if i:
                        fname="%s-%d" % (iname, i)
                        poly.name=fname
                    if not fname in self.output.polydat:
                        break	# no match - new object
                    if poly==self.output.polydat[fname]:
                        if self.output.xpver<9:
                            # 8.60 has a bug with polygons at different layers
                            # sharing textures, so use lowest layer
                            if __debug__:
                                if self.debug and poly.layer!=self.output.polydat[fname].layer: self.debug.write("!Flattened polygon %s layers %s and %s\n" % (fname, poly.layer, self.output.polydat[fname].layer))
                            self.output.polydat[fname].layer=min(poly.layer,self.output.polydat[fname].layer)
                        break	# matched - re-use this object
                    i+=1
                    
            self.output.polydat[fname]=poly
            self.output.polyplc.append((fname, heading, points))


        # Sort throught lights and geometry to create Objects.
        # Lights first so are combined with untextured Objects.
        # Keys must be unique to avoid duplicates, and a sort order must be defined in order to detect duplicates across Areas.
        # Matrix is applied here to allow for detection of data in a bgl that is duplicated apart from by heading

        objs={}		# [Object] by (loc, layer, altmsl, hdg)
        identity=Matrix()

        for lkey in self.keys:
            (name, loc, layer, alt, altmsl, matrix, scale, tex)=lkey
            if __debug__:
                if self.debug: self.debug.write("%s %s %s %s %s %s %s %s\n" % (name, loc, layer, alt, altmsl, scale, tex, matrix))
            newmatrix=matrix
            heading=0
            
            if loc and matrix and matrix.m[1][1]==1:	# No pitch or bank?
                # Rotate at placement time in hope of commonality with Objects produced in other Areas
                heading=matrix.heading()
                # unrotate translation
                (x,y,z)=Matrix().headed(-heading).rotate(matrix.m[3][0], matrix.m[3][1], matrix.m[3][2])
                scale2=scale/2.0
                newmatrix=Matrix().offset(round(x+scale2-(x+scale2)%scale,3), round(y+scale2-(y+scale2)%scale,3), round(z+scale2-(z+scale2)%scale,3))	# round to nearest unit to encourage a match
                if __debug__:
                    if self.debug: self.debug.write("New heading %6.2f, offset (%7.3f,%7.3f,%7.3f) %s\n" % (heading, newmatrix.m[3][0], newmatrix.m[3][1], newmatrix.m[3][2], newmatrix.m==identity.m))
                if newmatrix.m==identity.m: newmatrix=None

            # Find existing Object at this location with same tex to consolidate
            okey=(loc, layer, altmsl, heading)
            if okey in objs:
                for obj in objs[okey]:
                    if tex==obj.tex or not obj.vt:			# If no geometry in obj then tex irrelevant
                        if not obj.vt or (tex and tex.e): obj.tex=tex	# Because we don't compare on emissive
                        if __debug__:
                            if self.debug: self.debug.write("Merging into %s %s\n" % (obj.name, obj.tex))
                        break
                else:
                    # new data at existing location
                    obj=Object(name, self.comment, tex, layer, [])
                    objs[okey].append(obj)
            else:
                # new data at new location
                obj=Object(name, self.comment, tex, layer, [])
                objs[okey]=[obj]

            if lkey in self.lightdat:
                for ((x,y,z),(r,g,b)) in self.lightdat[lkey]:
                    if newmatrix:
                        (x,y,z)=newmatrix.transform(x,y,z)
                    obj.vlight.append((x*scale,alt+y*scale,-z*scale, r,g,b))
                
            if lkey in self.effectdat:
                for ((x,y,z),(effect,s)) in self.effectdat[lkey]:
                    if newmatrix:
                        (x,y,z)=newmatrix.transform(x,y,z)
                    obj.veffect.append((x*scale,alt+y*scale,-z*scale, effect, s))

            if lkey in self.objdat:
                for (mat, vtx, idx) in self.objdat[lkey]:
                    newvt=[]
                    # Break out common cases for speed
                    if newmatrix:
                        nrmmatrix=newmatrix.adjoint()
                        if not tex:
                            (pu,pv)=rgb2uv(mat.d)
                            for v in vtx:
                                (x,y,z,nx,ny,nz,tu,tv)=v
                                (x,y,z)=newmatrix.transform(x,y,z)
                                (nx,ny,nz)=nrmmatrix.rotateAndNormalize(nx,ny,nz)
                                # replace materials with palette texture
                                newvt.append([x*scale,alt+y*scale,-z*scale, nx,ny,-nz, pu,pv])
                        else:
                            for v in vtx:
                                (x,y,z,nx,ny,nz,tu,tv)=v
                                (x,y,z)=newmatrix.transform(x,y,z)
                                (nx,ny,nz)=nrmmatrix.rotateAndNormalize(nx,ny,nz)
                                newvt.append([x*scale,alt+y*scale,-z*scale, nx,ny,-nz, tu,tv])
                    else:
                        for v in vtx:
                            (x,y,z,nx,ny,nz,tu,tv)=v
                            if not tex:
                                # replace materials with palette texture
                                (tu,tv)=rgb2uv(mat.d)
                            newvt.append([x*scale,alt+y*scale,-z*scale, nx,ny,-nz, tu,tv])
                        
                    # Reverse order of individual tris
                    newidx=[]
                    for j in range(0,len(idx),3):
                        for k in range(2,-1,-1):
                            newidx.append(idx[j+k])

                    obj.addgeometry(mat, newvt, newidx)


        # If altmsl adjust all objects with same placement to ground level
        for okey in objs:
            (loc, layer, altmsl, heading)=okey
            if not altmsl: continue
            # Check whether this object is a 'decal' and apply poly_os
            miny=maxint
            for obj in objs[okey]:
                for v in obj.vt:
                    miny=min(miny,v[1])
            if miny <= groundfudge:
                continue	# already at ground level
            for obj in objs[okey]:
                for v in obj.vlight + obj.veffect + obj.vt:
                    v[1]=v[1]-miny

        # Place objects
        for okey in objs:
            (loc, layer, altmsl, heading)=okey
            if self.libname:
                assert len(objs)==1
                self.output.objdat[self.libname]=objs[okey]
            else:
                # Can have multiple objects at same loc, or same object at different locations, so place individually
                for obj in objs[okey]:
                    # See if this is a duplicate
                    for old in self.objcache:
                        if obj==old:
                            if __debug__:
                                if self.debug: self.debug.write("Dupe: %s and %s\n" % (obj.filename(1), old.filename(1)))
                            self.output.objplc.append((loc, heading, self.complexity, old.filename(1), 1))
                            break
                        elif obj.filename(1)==old.filename(1):
                            if __debug__:
                                if self.debug: self.debug.write("!Couldn't merge %s\n" % obj.filename(1))
                            obj.name+='x'	# Hack - different matrices at same loc eg LIEE2008 faro_icav
                    else:
                        assert obj.filename(1) not in self.output.objdat, obj.filename(1)	# object filenames must be unique
                        if __debug__:
                            if self.debug: self.debug.write("New: %s\n" % obj.filename(1))
                        self.objcache.append(obj)
                        self.output.objdat[obj.filename(1)]=[obj]
                        self.output.objplc.append((loc, heading, self.complexity, obj.filename(1), 1))


    def checkmsl(self):
        return self.altmsl
        if self.altmsl:
            self.output.log('Absolute altitude (%sm) for object at (%12.8f, %13.8f) in %s' % (round(self.altmsl,2), self.loc.lat, self.loc.lon, self.comment))
            #if self.altmsl>0: self.altmsl=False	# Don't report again for this object
            return True
        else:
            return False


    def getvar(self, var):
        if var in self.vars:
            val=self.vars[var]
            if var==0x28c and self.vars[0x28c]==1:
                self.neednight=True
                if __debug__:
                    if self.debug: self.debug.write('Need Night\n')
            return val
        else:
            if __debug__:
                if self.debug: self.debug.write('!Undefined variable 0x%04x\n'%var)
            return 0


    def setseason(self):
        day=[61,182,243,364]
        self.vars[0x38a]=day[self.output.season]	# zulu day in the year
        self.vars[0x6F8]=(self.output.season+1)%4	# season: 1=Spring
        if self.output.hemi:
            # Southern hemisphere
            self.vars[0x38a]=(self.vars[0x38a]+182)%364
            self.vars[0x6F8]=(self.vars[0x6F8]+2)%4


    def unicol(self, c):
        cols={0xF000: (24, 24, 24),
              0xF001: (56, 56, 56),
              0xF002: (121, 121, 121),
              0xF003: (203, 203, 203),
              0xF004: (255, 255, 255),
              0xF005: (252, 60, 60),
              0xF006: (60, 252, 60),
              0xF007: (0, 153, 230),
              0xF008: (252, 126, 0),
              0xF009: (252, 252, 0),
              0xF00A: (125, 105, 80),
              0xF00B: (225, 189, 144),
              0xF00C: (252, 99, 63),
              0xF00D: (153, 198, 81),
              0xF00E: (0, 58, 104),
              0xF00F: (255, 0, 0),
              0xF010: (64, 255, 64),
              0xF011: (0, 0, 192),
              0xF012: (0, 105, 105),
              0xF013: (255, 128, 0),
              0xF014: (255, 255, 0),
              0xF015: (228, 228, 228),
              0xF016: (228, 228, 228),
              0xF017: (84, 20, 20),
              0xF018: (20, 84, 20),
              0xF019: (0, 40, 84),
              0xF01A: (84, 42, 0),
              0xF01B: (84, 84, 0),
              0xF01C: (75, 63, 48),
              0xF01D: (75, 63, 48),
              0xF01E: (84, 33, 21),
              0xF01F: (51, 66, 27),
              0xF020: (126, 30, 30),
              0xF021: (30, 126, 30),
              0xF022: (0, 71, 122),
              0xF023: (112, 56, 0),
              0xF024: (112, 112, 0),
              0xF025: (75, 63, 48),
              0xF026: (100, 84, 64),
              0xF027: (112, 44, 28),
              0xF028: (68, 88, 36),
              0xF029: (189, 45, 45),
              0xF02A: (45, 189, 45),
              0xF02B: (0, 112,179),
              0xF02C: (168, 84, 0),
              0xF02D: (168, 168, 0),
              0xF02E: (100, 84, 64),
              0xF02F: (150, 126, 96),
              0xF030: (168, 66, 42),
              0xF031: (102, 132, 54),
              0xF032: (82, 82, 82),
              0xF033: (163, 163, 163),
              0xF034: (196, 196, 196)}
        if c in cols:
            (r,g,b)=cols[c]
            return (r/255.0, g/255.0, b/255.0)
        else:
            return (0,0,0)


# Handle miscellaneous section 16
class ProcMisc:
    def __init__(self, bgl, srcfile, output):
        self.bgl=bgl
        self.output=output
        self.debug=output.debug

        cmds={0x04:self.Marker,
              0x05:self.Marker,
              0x06:self.Marker,
              0x07:self.Landme,
              0x64:self.TimeZone,
              0x65:self.Platform,
              0x70:self.AreaSense,
              0xa6:self.Reserved,
              0xe6:self.Terrain,
              }

        while True:
            pos=bgl.tell()
            (cmd,)=unpack('<B',bgl.read(1))
            if cmd==0 or cmd==0x22:
                return
            elif cmd in cmds:
                if __debug__:
                    if self.debug: self.debug.write("%x: cmd %02x %s\n" % (pos, cmd, cmds[cmd].__name__))
                cmds[cmd]()
            else:
                if __debug__:
                    if self.debug: self.debug.write("!Unknown s16 cmd %x at %x\n" %(cmd,pos))
                raise struct.error

    def Marker(self):		# 04,05,06
        # Ignore - this data should be in XML
        (size,)=unpack('<B',self.bgl.read(1))
        self.bgl.seek(size-2,1)

    def Landme(self):		# 07
        # Ignore
        (size,)=unpack('<B',self.bgl.read(1))
        self.bgl.seek(size-2,1)

    def TimeZone(self):		# 64
        # Ignore
        (size,)=unpack('<B',self.bgl.read(1))
        self.bgl.seek(size-2,1)

    def Platform(self):		# 65
        # Ignore
        (size,)=unpack('<B',self.bgl.read(1))
        self.bgl.seek(size-2,1)

    def AreaSense(self):	# 70
        # Assume inside
        (off,n)=unpack('<hH', self.bgl.read(4))
        self.bgl.seek(4*n,1)	# skip

    def Reserved(self):		# a6
        # Appears in section 16
        self.bgl.read(6)

    def Terrain(self):		# e6
        (foo,size,op,n,alt)=unpack("<BIHHi", self.bgl.read(13))
        l=[]
        for i in range(n):
            (lat,lon)=unpack("<ii", self.bgl.read(8))
            lat*=360.0/(65536*65536)
            lon*=360.0/(65536*65536)
            if lat>180: lon-=360
            if lon>180: lon-=360
            l.append(Point(lat, lon))
        # sort CCW
        area2=0
        for i in range(n):
            area2+=(l[i].lon * l[(i+1)%n].lat -
                    l[(i+1)%n].lon * l[i].lat)
        if area2<0: l.reverse()
        a=[AptNav(130, 'Flatten')]
        for i in range(n):
            a.append(AptNav(111, "%12.8f %13.8f" % (l[i].lat, l[i].lon)))
        a[-1].code=113
        if op==5:	# Flatten
            self.output.misc.append((130, l[0], a))
        elif __debug__:
            if self.debug: self.debug.write("!Unknown Terrain opcode %x\n" % op)


# Handle exception section 19
def ProcEx(bgl, output):
    while True:
        (c,)=unpack('<B',bgl.read(1))
        if c==0:
            return
        elif c==3:
            # Exclusion
            (mask,n,s,e,w)=unpack('<H4I',bgl.read(18))
            if __debug__:
                if output.debug: output.debug.write("Exclude: %d\n" % mask)
            if mask&1:
                # objects
                n=n*360.0/cirp
                s=s*360.0/cirp
                e=e*360.0/0x100000000
                if e>180: e-=360
                w=w*360.0/0x100000000
                if w>180: w-=360
                output.exc.append(('obj', Point(s,w), Point(n,e)))
                #output.exc.append(('rwy', Point(s,w), Point(n,e)))
                #output.exc.append(('fac', Point(s,w), Point(n,e)))
        elif c==4:
            # Exception - ignore
            (lat,lon,typ,sn,sf,snf)=unpack('<IIBBBB',bgl.read(12))
            lat=lat*360.0/cirp
            lon=lon*360.0/0x100000000
            if lat>180: lat-=360
            if __debug__:
                if output.debug: output.debug.write("Exception: %d %x %x %x\n" % (typ,sn,sf,snf))
        else:
            if __debug__:
                if output.debug: output.debug.write("!Unknown s19 cmd: %x\n" % c)
            raise struct.error


# Handle terrain section 8
def ProcTerrain(bgl, srcfile, output):
    (size,ver)=unpack('<2I', bgl.read(8))
    if size!=0x64: raise struct.error
    (reserved1,)=unpack('<I', bgl.read(4))	# No idea how to decode this
    bgl.seek(11*4,1)
    (lwm,vtp)=unpack('<2I', bgl.read(8))
    if lwm or vtp: output.log('Skipping terrain data in file %s' % asciify(basename(srcfile),False))


def subdivide(vtx):
    # Subdivide concave polygon into tris
    tessObj = gluNewTess()
    gluTessProperty(tessObj,GLU_TESS_WINDING_RULE,GLU_TESS_WINDING_NONZERO)
    gluTessCallback(tessObj,GLU_TESS_VERTEX_DATA,  tessvertex)
    gluTessCallback(tessObj,GLU_TESS_EDGE_FLAG,    tessedge)	# no strips
    points=[]
    idx=[]
    try:
        gluTessBeginPolygon(tessObj, (points, idx))
        gluTessBeginContour(tessObj)
        for vertex in vtx:
            (x,y,z, nx,ny,nz, tu, tv)=vertex
            gluTessVertex(tessObj, [x, y, z], vertex)
        gluTessEndContour(tessObj)
        gluTessEndPolygon(tessObj)
    except:
        gluDeleteTess(tessObj)
        raise GLUerror
    gluDeleteTess(tessObj)        
    return (points,idx)

def tessedge(flag):
    pass	# dummy

def tessvertex(vertex, (points, idx)):
    if vertex in points:
        idx.append(points.index(vertex))
    else:
        idx.append(len(points))
        points.append(vertex)


# Helper makes dict of form lowercasename: realname
def maketexdict(texdir):
    if not texdir: return None

    # Handle unicode
    if type(texdir)==types.UnicodeType:
        f=[normalize(name) for name in listdir(texdir)]
    else:
        f=listdir(texdir)

    d=dict([(name.lower(),name) for name in f])

    # Add ascii versions of filenames - eg PRAM2005
    for name in f:
        aname=asciify(name).lower()
        if aname not in d:
            d[aname]=name
    
    return (texdir, d)


# Helper to return fully-qualified case-sensitive texture filename
def findtex(name, thistexdir, addtexdir, dropmissing=True):
    for texdict in [thistexdir, addtexdir]:
        if not texdict: continue
        (texdir, d)=texdict
        # Extension is ignored by MSFS?
        (s,e)=splitext(name.lower())
        for ext in [e, '.dds', '.bmp', '.r8']:
            if s+ext in d:
                return join(texdir, d[s+ext])
            
        if len(s)==8 and s[-2]=='~' and s[-1].isdigit():
            # Crappy 8.3 name - pick first match
            s=s[:-2]
            for ext in [e, '.dds', '.bmp', '.r8']:
                for i in d.keys():
                    if i.startswith(s) and i[-4:]==ext:
                        return join(texdir, d[i])

    if not thistexdir: return name.lower()
    (texdir, d)=thistexdir

    # Look for textures that differ only in accents - eg PRAM2005
    sa=asciify(s).lower()
    for ext in [e, '.dds', '.bmp', '.r8']:
        if sa+ext in d:
            return join(texdir, d[sa+ext])

    # Not found
    if dropmissing:
        return None
    else:
        return join(texdir, sa+e)	# make lower-case to prevent dupes
