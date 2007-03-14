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

from math import acos, cos, fmod, pow, sin
from os import listdir
from os.path import basename, dirname, exists, join, normpath, pardir, splitext
import struct
from struct import unpack
from sys import maxint

from convutil import cirp, d2r, r2d, m2f, NM2m, complexity, asciify, cross, dot, AptNav, Object, Point, Matrix, apronlightspacing, taxilightspacing
from convobjs import maketaxilight

# Read BGL header
class Parse:
    def __init__(self, bgl, srcfile, output):
        if output.debug:
            debug=file(join(output.xppath,'debug.txt'),'at')
            debug.write('%s\n' % srcfile)
        else:
            debug=None
        name=basename(srcfile)
        for section in [42,54,58,102,114]:
            bgl.seek(section)
            (secbase,)=unpack('<I',bgl.read(4))
            if (secbase):
                bgl.seek(secbase)
                if section==42:
                    output.log('Skipping traffic data in file %s' % name)
                elif section==54:
                    output.log('Skipping terrain data in file %s' % name)
                elif section==58:
                    # OBJECT data
                    areano=0
                    old=False
                    rrt=False
                    anim=False
                    while 1:
                        # LatBand
                        posl=bgl.tell()
                        (c,)=unpack('<B', bgl.read(1))
                        if not c in [0, 21]:
                            if debug: debug.write("!Bogus LatBand %2x\n" % c)
                            raise struct.error	# wtf?
                        if c==0:
                            break
                        (foo,off)=unpack('<Ii', bgl.read(8))
                        bgl.seek(secbase+off)
                        while 1:
                            # Header
                            areano+=1                        
                            posa=bgl.tell()
                            if debug: debug.write("----\nArea %x\n" % posa)
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
                                if debug:debug.write("!Bogus area type %x\n"%c)
                                raise struct.error	# wtf?
                            try:
                                p=ProcScen(bgl, posa+l, None, srcfile,
                                           output, None, None, debug)
                                if p.old:
                                    old=True
                                    if debug: debug.write("Pre-FS2002\n")
                                if p.rrt:
                                    rrt=True
                                    if debug: debug.write("Old-style rr\n")
                                if p.anim:
                                    anim=True
                                    if debug: debug.write("Animation\n")
                            except struct.error:
                                output.log("Can't parse area #%d in %s" % (
                                    areano, name))
                                if debug: debug.write("Can't parse area %x in file %s\n" % (posa, name))
                            bgl.seek(posa+l)
                        bgl.seek(posl+9)
                    if anim:
                        output.log("Skipping animation in file %s" % name)
                    if old:
                        output.log("Skipping pre-FS2002 scenery in file %s" % name)
                    if rrt:
                        output.log("Skipping pre-FS2004 runways and/or roads in file %s" % name)
                elif section==102:
                    output.log('Skipping misc data in file %s' % name)
                elif section==114:
                    try:
                        ProcEx(bgl, output)
                    except struct.error:
                        output.log("Can't parse Exception section in file %s"%(
                            name))
        if debug: debug.close()


# handle section 9 and 10 scenery. libname!=None if this is a library
class ProcScen:
    def __init__(self, bgl, enda, libname, srcfile, output,
                 scen, tran, debug):

        self.old=False	# Old style scenery found and skipped
        self.rrt=False	# Old style runways/roads found and skipped
        self.anim=False	# Animations found and skipped
        self.debug=debug

        self.bgl=bgl
        self.libname=libname
        self.srcfile=basename(srcfile)
        if libname:
            self.comment="object %s in file %s" % (libname,self.srcfile)
        else:
            self.comment="file %s" % self.srcfile	# Used for reporting
        self.output=output
        self.texdir=normpath(join(dirname(srcfile), pardir))
        # For case-sensitive filesystems
        if 'Texture' in listdir(self.texdir):
            self.texdir=join(self.texdir, 'Texture')
        else:
            self.texdir=join(self.texdir, 'texture')

        pos=bgl.tell()
        if tran: self.tran=pos+tran		# Location of TRAN table
        if scen:
            # Decode SCEN table
            bgl.seek(pos+scen)
            (count,)=unpack('<H', bgl.read(2))
            scen=pos+scen+2
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
            bgl.seek(pos)
        
        # State
        self.complexity=1
        self.loc=None
        self.alt=0
        self.altmsl=0
        self.matrix=[None]
        self.scale=1.0
        self.stack=[]	# (return address, pop matrix?)
        self.tex=[]
        self.mat=[]	# [[(ar,ag,ab),(sr,sg,sb),(er,eg,eb)]]
        self.vtx=[]
        self.idx=[]	# Indices into vtx
        self.m=None	# Index into mat
        self.t=None	# Index into tex
        self.billboard=None	# Emulating billboarding in a libary defn
        self.taxiway=None	# Last taxiway (width, loc)
        self.pnt=None	# Last line location (x,y,z)
        self.haze=0	# Whether palette-based transaprency. 0=none
        self.concave=False

        self.objdat={}	# (mat, alt, vtx[], idx[]) by (loc, matrix, scale, tex)
        self.linedat={}	# (alt, vtx[], idx[], (r,g,b)) by (loc, matrix, scale)
        self.lightdat={}# (alt, (x,y,z), (r,g,b)) by (loc, matrix, scale)

        self.vars={
            # Vars not listed are assumed to be 0
            0: 0,	# dummy
            #0x07e: 0,	# FS5_CG_TO_GROUND_X: ???
            0x280: 0,	# altmsl (presumably of airplane?)
            0x282: 1,	# beacon: rotating bitmap shifted 1 bit/3 sec
            0x28c: 4,	# tod: 2|4 indicates night?
            0x30A: 6,	# beacon_2: 16-bit bitmap with 0x0506 add/3 sec
            0x30C: 8,	# beacon_3: 16-bit bitmap with 0x0708 add/3 sec 
            0x30E: 0xa,	# beacon_4: 16-bit bitmap with 0x090A add/3 sec 
            0x310: 0xc,	# beacon_5: 16-bit bitmap with 0x0B0C add/3 sec
            #0x338, 1,	# SHADOW_FLAG: 0=do crash detection???
            0x33a: 0,	# rbias: eye to object distance in meters II.FF
            0x33b: 0,	# rbias_1: eye to object distance in meters IIII
            0x340: 255,	# ground_texture
            0x342: 255,	# building_texture
            0x344: 255,	# aircraft_texture
            0x346: 5,	# image_complex: complexity of the scenery 0-5
            0x37e: 0,	# xv: rotated X-axis eye to object distance
            0x382: 0,	# yv: rotated Y-axis eye to object distance
            0x386: 0,	# zv: rotated Z-axis eye to object distance
            0x389: 12,	# zulu hours in the day - Midday
            0x390: 0,	# water_texture
            0xc72: 5,	# ground wind velocity [kts?]
            0xc74: 0,	# ground wind direction [units?]
            0xc76: 0,	# ground wind turbulence [units?]
            }
        self.setseason()

        cmds={0x02:self.NOP,
              0x05:self.NOP,
              0x06:self.SPnt,
              0x07:self.CPnt,
              0x08:self.Closure,
              0x0d:self.Jump,
              0x0f:self.StrRes,
              0x10:self.StrRes,        
              0x14:self.SColor,
              0x17:self.TextureEnable,
              0x18:self.Texture,
              0x1a:self.ResList,
              0x1b:self.Jump,
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
              0x30:self.NOPh,
              0x2a:self.FaceT,
              0x2b:self.Call32,
              0x2d:self.SColor24,
              0x2e:self.SColor24,
              0x2f:self.Scale,
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
              0x42:self.TextureRunway,
              0x43:self.Texture2,
              0x44:self.TextureRunway,
              0x4d:self.MoveL2G,
              0x4e:self.MoveL2G,
              0x46:self.PointVICall,
              0x49:self.Building,
              0x3f:self.NOPh,
              0x50:self.SColor,
              0x51:self.SColor,
              0x52:self.SColor,
              0x55:self.SurfaceType,
              0x5d:self.TextureRepeat,
              0x5f:self.IfSizeV,
              0x62:self.IfVis,
              0x63:self.LibraryCall,
              0x69:self.RoadStart,
              0x6a:self.RoadCont,
              0x6b:self.RoadStart,
              0x6c:self.RoadCont,
              0x6d:self.IfSizeV,
              0x6e:self.TaxiwayStart,
              0x6f:self.TaxiwayCont,
              0x70:self.AreaSense,
              0x76:self.NOP,
              0x73:self.Jump,
              0x74:self.AddCat,
              0x77:self.ScaleAGL,
              0x7a:self.FaceTTMap,
              0x7d:self.NOP,
              0x80:self.ResPnt,
              0x81:self.NOPh,
              0x83:self.ReScale,
              0x88:self.Jump32,
              0x89:self.NOPi,
              0x8a:self.Call32,
              0x8f:self.Haze,
              0x93:self.NOPh,
              0x95:self.CrashIndirect,
              0x96:self.CrashStart,
              0x9e:self.Interpolate,
              0x9f:self.NOPi,
              0xa0:self.Object,
              0xa7:self.SpriteVICall,
              0xa8:self.TextureRoadStart,
              0xaa:self.NewRunway,
              0xad:self.Animate,
              0xae:self.TransformEnd,
              0xac:self.NOPh,
              0xaf:self.TransformMatrix,
              0xb1:self.Tag,
              0xb2:self.Light,
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

        while 1:
            pos=bgl.tell()
            if pos>=enda:
                self.makeobjs()
                if pos>enda:
                    if self.debug: self.debug.write("!Overrun at %x enda=%x in %s\n" % (pos, enda, self.comment))
                    raise struct.error
                return            
            (cmd,)=unpack('<H',bgl.read(2))
            if cmd==0 or (cmd==0x22 and not self.stack):
                if self.debug:
                    self.debug.write("%x: cmd %02x\n" % (pos, cmd))
                    for i in range(1, len(self.matrix)):
                        self.debug.write("!Unbalanced matrix:\n%s\n" % (
                            self.matrix[i]))
                self.makeobjs()
                return
            elif cmd in cmds:
                if self.debug: self.debug.write("%x: cmd %02x %s\n" % (
                    pos, cmd, cmds[cmd].__name__))
                cmds[cmd]()
            else:
                if self.debug: self.debug.write("!Unknown cmd %x at %x in %s\n" % (cmd, pos, self.comment))
                self.makeobjs()	# Try to go with what we've got so far
                raise struct.error


    def SPnt(self):		# 06
        self.pnt=unpack('<hhh', self.bgl.read(6))

    def CPnt(self):		# 07
        (cx,cy,cz)=unpack('<hhh', self.bgl.read(6))
        key=(self.loc,self.matrix[-1],self.scale)
        mat=self.mat[self.m]
        if not mat:
            self.pnt=(cx,cy,cz)
            return	# transparent
        if self.pnt:
            (sx,sy,sz)=self.pnt
        else:	# continuation
            if not key in self.linedat:
                self.pnt=(cx,cy,cz)
                return	# CPnt with no SPnt
            (a,vtx,idx,m)=self.linedat[key][-1]
            if m==mat[0]:
                idx.append(len(vtx))
                vtx.append((cx,cy,cz,0,0,0,0,0))
                self.linedat[key][-1]=(a,vtx,idx,m)
                self.checkmsl()
                return
            else:	# change of material - can't do continuation
                (sx,sy,sz,nx,ny,nz,tu,tv)=vtx[-1]

        if not key in self.linedat:
            self.linedat[key]=[]
        self.linedat[key].append((self.alt,
                                  [(sx,sy,sz,0,0,0,0,0), (cx,cy,cz,0,0,0,0,0)],
                                  [0,1], mat[0]))
        self.checkmsl()
        self.pnt=None

    def Closure(self):		# 08
        count=len(self.idx)
        vtx=[]
        for i in range(count):
            (x,y,z,c,c,c,c,c)=self.vtx[self.idx[i]]
            vtx.append((x,y,z, 0,1,0, x*self.scale/256, z*self.scale/256))
        self.idx=[]
        if self.concave:
            (vtx,idx)=subdivide(vtx)
            self.concave=False
        else:
            idx=[]
            for i in range(1,len(vtx)-1):
                idx.extend([0,i,i+1])
        if self.t==None or self.t==-1:
            tex=None
        else:
            tex=self.tex[self.t]
            if self.haze: self.output.haze[tex]=self.haze
        key=(self.loc,self.matrix[-1],self.scale,tex)
        if not key in self.objdat:
            self.objdat[key]=[]
        self.objdat[key].append(([(1,1,1), (0,0,0), (0,0,0)],
                                 self.alt, vtx, idx, True))
        self.checkmsl()
        
        
    def Jump(self):		# 0d, 1b: IfInBoxRawPlane, 73: IfInBoxP
        (off,)=unpack('<h', self.bgl.read(2))
        if not off: raise struct.error	# infloop
        self.bgl.seek(off-4,1)

    def StrRes(self):		# 0f:StrRes, 10:CntRes
        (i,)=unpack('<H',self.bgl.read(2))
        self.idx.append(i)
        
    def SColor(self):	# 14:Scolor, 2d: SColor24, 2e: LColor24, 50:GColor, 51:NewLColor, 52:NewSColor
        (c,)=unpack('H', self.bgl.read(2))
        self.m=0
        self.mat=[[self.unicol(c), (0,0,0), (0,0,0)]]
        
    def TextureEnable(self):		# 17
        (c,)=unpack('<H', self.bgl.read(2))
        if not c:
            self.t=-1
        else:
            self.t=0

    def Texture(self):		# 18
        (c,x,c,y)=unpack('<4h', self.bgl.read(8))
        tex=self.bgl.read(14).rstrip(' \0')
        l=tex.find('.')
        if l!=-1:	# Sometimes formatted as 8.3 with spaces
            tex=tex[:l].rstrip(' \0')+tex[l:]
        # Extension is ignored by MSFS?
        (s,e)=splitext(tex)
        for ext in [e, '.bmp', '.r8']:
            if exists(join(self.texdir,s+ext)):
                tex=s+ext
                break
        # Fix case for case sensitive filesystems
        for f in listdir(self.texdir):
            if tex.lower()==f.lower():
                tex=f
                break
        else:
            tex=tex.lower()
        self.tex=[join(self.texdir,tex)]
        self.t=0
        if self.debug: self.debug.write("%s\n" % basename(self.tex[0]))
        if x or y:
            if self.debug: self.debug.write("!Tex offsets %d,%d\n" % (x,y))
        
    def IfInBoxRawPlane(self):	# 1b
        # Skip
        (off,)=unpack('<h', self.bgl.read(2))
        self.bgl.seek(off-4,1)
        
    def ResList(self):		# 1a
        (index,count)=unpack('<2H', self.bgl.read(4))
        if len(self.vtx)<index:
            self.vtx.extend([None for i in range(index-len(self.vtx))])
        for i in range(index,index+count):
            (x,y,z)=unpack('<3h', self.bgl.read(6))
            v=(x,y,z, 0,0,0, 0,0)
            if i==len(self.vtx):
                self.vtx.append(v)
            else:
                self.vtx[i]=v

    def Haze(self):		# 1e:Haze, 8f:Alpha
        # XXX Alpha (8f) Also has meaning for non-textured polygons
        (self.haze,)=unpack('<H', self.bgl.read(2))
        
    def TaxiMarkings(self):	# 1f
        # ignored - info should now be in FS2004-style BGL
        self.rrt=True
        (size,)=unpack('<H', self.bgl.read(2))
        self.bgl.seek(size-4,1)
        
    def FaceTTMap(self):	# 20:FaceTTMap, 7a:GFaceTTMap
        (count,nx,ny,nz,)=unpack('<H3h', self.bgl.read(8))
        nx=nx/32767.0
        ny=ny/32767.0
        nz=nz/32767.0
        self.bgl.read(4)
        vtx=[]
        for i in range(count):
            (idx,tu,tv)=unpack('<H2h', self.bgl.read(6))
            (x,y,z,c,c,c,c,c)=self.vtx[idx]
            vtx.append((x,y,z, nx,ny,nz, tu/256.0,tv/256.0))
        if self.concave:
            (vtx,idx)=subdivide(vtx)
            self.concave=False
        else:
            idx=[]
            for i in range(1,len(vtx)-1):
                idx.extend([0,i,i+1])
        # Change order if necessary to face in direction of normal
        (x0,y0,z0,c,c,c,c,c)=vtx[0]
        (x1,y1,z1,c,c,c,c,c)=vtx[1]
        (x2,y2,z2,c,c,c,c,c)=vtx[2]
        (x,y,z)=cross((x1-x0,y1-y0,z1-z0), (x2-x0,y2-y0,z2-z0))
        if dot((x,y,z), (nx,ny,nz))>0:
            idx.reverse()
        if self.t==None or self.t==-1:
            tex=None
        else:
            tex=self.tex[self.t]
            if self.haze: self.output.haze[tex]=self.haze
        key=(self.loc,self.matrix[-1],self.scale,tex)
        if not key in self.objdat:
            self.objdat[key]=[]
        self.objdat[key].append(([(1,1,1),(0,0,0),(0,0,0)],
                                 self.alt, vtx, idx, False))
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
                self.bgl.seek(off-22,1)
                break

    def Return(self):		# 22
        (off,pop)=self.stack.pop()
        if pop:
            self.matrix.pop()
            if self.debug: self.debug.write("Now\n%s\n" % self.matrix[-1])
        self.bgl.seek(off)

    def Call(self):		# 23:Call, 32:PerspectiveCall
        (off,)=unpack('<h', self.bgl.read(2))
        if not off: raise struct.error	# infloop
        self.stack.append((self.bgl.tell(),False))
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
        if val<vmin or val>vmax:
            self.bgl.seek(off-10,1)

    def SeparationPlane(self):	# 25
        # Used for animating distance. Skip
        (off,nx,ny,nz,dist)=unpack('<4hi', self.bgl.read(12))
        #self.stack.append((self.bgl.tell(),self.matrix))
        #self.bgl.seek(off-14,1)

    def SetWrd(self):		# 26
        (var,val)=unpack('<2h',self.bgl.read(4))
        self.vars[var]=val

    def GResList(self):		# 29
        (index,count)=unpack('<2H', self.bgl.read(4))
        if len(self.vtx)<index:
            self.vtx.extend([None for i in range(index-len(self.vtx))])
        for i in range(index,index+count):
            (x,y,z,nx,ny,nz)=unpack('<6h', self.bgl.read(12))
            v=(x,y,z, nx/32767.0,ny/32767.0,nz/32767.0, 0,0)
            if i==len(self.vtx):
                self.vtx.append(v)
            else:
                self.vtx[i]=v

    def FaceT(self):		# 2a:GFaceT, 3e:FaceT
        (count,nx,ny,nz)=unpack('<H3h', self.bgl.read(8))
        if count<=4: self.concave=False	# Don't bother
        nx=nx/32767.0
        ny=ny/32767.0
        nz=nz/32767.0
        self.bgl.read(4)
        vtx=[]
        for i in range(count):
            (idx,)=unpack('<H', self.bgl.read(2))
            (x,y,z,c,c,c,c,c)=self.vtx[idx]
            vtx.append((x,y,z, nx,ny,nz, x*self.scale/256, z*self.scale/256))
        if self.concave:
            (vtx,idx)=subdivide(vtx)
            self.concave=False
        else:
            idx=[]
            for i in range(1,len(vtx)-1):
                idx.extend([0,i,i+1])
        # Change order if necessary to face in direction of normal
        (x0,y0,z0,c,c,c,c,c)=vtx[0]
        (x1,y1,z1,c,c,c,c,c)=vtx[1]
        (x2,y2,z2,c,c,c,c,c)=vtx[2]
        (x,y,z)=cross((x1-x0,y1-y0,z1-z0), (x2-x0,y2-y0,z2-z0))
        if dot((x,y,z), (nx,ny,nz))>0:
            idx.reverse()
        # If color defined then use it in preference to bitmap
        if self.m!=None or self.t==None or self.t==-1:
            tex=None
            if self.m!=None:
                mat=self.mat[self.m]
                if not mat: return	# transparent
            else:
                mat=[(0.5,0.5,0.5), (0,0,0), (0,0,0)]	# wtf?
        else:
            tex=self.tex[self.t]
            if self.haze: self.output.haze[tex]=self.haze
            mat=[(1,1,1), (0,0,0), (0,0,0)]
        key=(self.loc,self.matrix[-1],self.scale,tex)
        if not key in self.objdat:
            self.objdat[key]=[]
        self.objdat[key].append((mat, self.alt, vtx, idx, False))
        self.checkmsl()
        
    def SColor24(self):		# 2d: SColor24, 2e: LColor24
        (r,a,g,b)=unpack('4B', self.bgl.read(4))
        self.m=0
        if a==0xf0:	# unicol
            self.mat=[[self.unicol(0xf000+r), (0,0,0), (0,0,0)]]
        #elif (a>=0xb3 and a<=0xb8) or (a>=0xe3 and a<=0xe8):
        #    # E0 = transparent ... EF=opaque. Same for B?
        #    self.mat=[[(r/255.0,g/255.0,b/255.0,0.25), (0,0,0,0), (0,0,0,0)]]
        elif (a>=0xb0 and a<=0xb7) or (a>=0xe0 and a<=0xe7):
            # Treat semi-transparent as fully transparent
            self.mat=[None]
        else:
            self.mat=[[(r/255.0,g/255.0,b/255.0), (0,0,0), (0,0,0)]]
        
    def Scale(self):		# 2f
        self.bgl.read(8)	# jump,range (LOD) (may be 0),size,reserved
        (scale,)=unpack('<I', self.bgl.read(4))
        self.scale=65536.0/scale
        (lat,lon,self.altmsl)=self.LLA()
        self.alt=0
        self.loc=Point(lat,lon)
        if lat<0 and not self.output.hemi:
            self.output.hemi=1
            self.setseason()

    def Instance(self):		# 33
        (off,p,b,h)=unpack('<h3H', self.bgl.read(8))
        self.stack.append((self.bgl.tell(),True))
        p=p*360/65536.0
        b=b*360/65536.0
        h=h*360/65536.0
        newmatrix=Matrix()
        newmatrix=newmatrix.headed(h)
        newmatrix=newmatrix.pitched(p)
        newmatrix=newmatrix.banked(b)
        if self.debug:
            self.debug.write("Instance\n")
            if self.matrix[-1]:
                self.debug.write("Old\n%s\n" % self.matrix[-1])
                self.debug.write("New\n%s\n" % newmatrix)
        if self.matrix[-1]:
            newmatrix=newmatrix*self.matrix[-1]
        self.matrix.append(newmatrix)
        if self.debug:
            self.debug.write("Now\n%s\n" % self.matrix[-1])
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
        mat=self.mat[self.m]
        if not mat:
            return	# transparent
        key=(self.loc,self.matrix[-1],self.scale)
        if not key in self.lightdat:
            self.lightdat[key]=[]
        for i in range(count):
            self.lightdat[key].append((self.alt,
                                       (sx+i*dx,sy+i*dy,sz+i*dz), mat[0]))
        self.checkmsl()
        
    def Point(self):		# 37
        (x,y,z)=unpack('<3h', self.bgl.read(6))
        mat=self.mat[self.m]
        if not mat:
            return	# transparent
        key=(self.loc,self.matrix[-1],self.scale)
        if not key in self.lightdat:
            self.lightdat[key]=[]
        self.lightdat[key].append((self.alt, (x,y,z), mat[0]))
        self.checkmsl()

    def Concave(self):		# 38
        self.concave=True

    def IfMsk(self):		# 39
        (off, var)=unpack('<2h', self.bgl.read(4))
        (mask,)=unpack('<H', self.bgl.read(2))
        val=self.getvar(var)
        if val&mask==0:
            self.bgl.seek(off-8,1)

    def VInstance(self):	# 3b
        (off,var)=unpack('<hH', self.bgl.read(4))
        self.stack.append((self.bgl.tell(),True))
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
        if self.debug:
            self.debug.write("Now\n%s\n" % self.matrix[-1])
        self.matrix.append(newmatrix)
        self.bgl.seek(off-6,1)

    def Position(self):		# 3c
        self.bgl.read(8)	# jump,range (LOD) (may be 0),size,reserved
        (lat,lon,alt)=self.LLA()
        pt=Point(lat,lon)
        if self.loc:
            (x,y,z)=Matrix().headed(self.loc.headingto(pt)).rotate(0,0,self.loc.distanceto(pt))
            if self.matrix[-1]:
                if self.debug: self.debug.write("Old\n%s\n" % self.matrix[-1])
                self.matrix[-1]=self.matrix[-1].offset(x,alt,z)
            else:
                self.matrix[-1]=Matrix().offset(x,alt,z)
            if self.debug:
                self.debug.write("New\n%s\n" % self.matrix[-1])
                self.debug.write("Now\n%s\n" % Matrix().offset(x,alt,z))
        else:
            self.loc=pt
            self.alt=alt
        self.altmsl=False

    def Texture2(self):		# 43
        (size,)=unpack('<H', self.bgl.read(2))
        self.bgl.read(8)	# 00, flags0, unicol
        # FFS nl2000 crew can't count - so stop when hit first '\0'
        #tex=self.bgl.read(size-12).rstrip(' \0')
        tex=''
        size=size-12
        while size:
            c=self.bgl.read(1)
            if c=='\0':
                # Hope we're not at end of area - cos this will overrun.
                while self.bgl.read(1)=='\0':
                    pass
                self.bgl.seek(-1, 1)        
                break
            tex=tex+c
            size=size-1
        tex=tex.rstrip()
        # Extension is ignored by MSFS?
        (s,e)=splitext(tex)
        for ext in [e, '.bmp', '.r8']:
            if exists(join(self.texdir,s+ext)):
                tex=s+ext
                break
        # Fix case for case sensitive filesystems
        for f in listdir(self.texdir):
            if tex.lower()==f.lower():
                tex=f
                break
        else:
            tex=tex.lower()
        self.tex=[join(self.texdir, tex)]
        if self.debug: self.debug.write("%s\n" % basename(self.tex[0]))
        self.t=0
        
    def TextureRunway(self):	# 42: PolygonRunway, 44:TextureRunway
        # ignored - info should now be in FS2004-style BGL
        self.rrt=True
        self.bgl.seek(62,1)	# SDK lies

    def PointVICall(self):	# 46
        (off,x,y,z,p,vp,b,vb,h,vh)=unpack('<4h6H', self.bgl.read(20))
        if not off: raise struct.error	# infloop
        #if self.debug: self.debug.write("PointVICall %d %d %d %d %d %d %d %d %d\n" % (x,y,z,p,vp,b,vb,h,vh))
        self.stack.append((self.bgl.tell(),True))
        p=p*360/65536.0
        b=b*360/65536.0
        h=h*360/65536.0
        newmatrix=Matrix()
        newmatrix=newmatrix.offset(x,y,z)
        newmatrix=newmatrix.headed(h+self.getvar(vh))
        newmatrix=newmatrix.pitched(p+self.getvar(vp))
        newmatrix=newmatrix.banked(b+self.getvar(vb))
        if self.debug:
            self.debug.write("PointVICall\n")
            if self.matrix[-1]:
                self.debug.write("Old\n%s\n" % self.matrix[-1])
                self.debug.write("New\n%s\n" % newmatrix)
        if self.matrix[-1]:
            newmatrix=newmatrix*self.matrix[-1]
        self.matrix.append(newmatrix)
        if self.debug:
            self.debug.write("Now\n%s\n" % self.matrix[-1])
        if self.libname and h:
            self.billboard=(x,y,z)
            # XXX Implement me!
        self.bgl.seek(off-22,1)

    def Building(self):		# 49
        # XXX Implement me!
        self.output.log('Unsupported generic building at (%10.6f, %11.6f) in %s' % (self.loc.lat, self.loc.lon, self.comment))
        self.bgl.seek(16,1)

    def MoveL2G(self):		# 4d:MoveL2G, 4e:MoveG2L
        (to, fr)=unpack('<2H', self.bgl.read(4))
        self.vars[to]=self.getvar(fr)
        
    def SurfaceType(self):	# 55
        self.rrt=True
        (sfc, cnd, x, z, alt)=unpack('<BBhhh', self.bgl.read(8))
        if sfc==0:	# Hard
            smap={0:4, 1:2, 2:1, 3:3, 4:12, 5:5, 6:2, 7:2, 8:13}
            if cnd in smap:
                code=smap[cnd]
            else:
                code=1	# Asphalt
            if self.matrix[-1]:
                heading=self.matrix[-1].heading()	# XXX not really
            else:
                heading=0
            length=m2f*x*self.scale
            width=m2f*z*self.scale
            if self.debug: self.debug.write("SurfaceType %d %d (%dx%d)\n" % (
                sfc, code, length, width))
            # Don't do this - area tends to be way too big
            #self.output.misc.append((10, self.loc, 'xxx %6.2f %6d 0000.0000 0000.0000 %4d 111111 %02d 0 0 0.25 0 0000.0000' % (heading, length, width, code)))

    def TextureRepeat(self):	# 5d
        (x,c,y)=unpack('<3h', self.bgl.read(6))
        if x or y:
            if self.debug: self.debug.write("!Tex offsets %d,%d\n" % (x,y))
        
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
        if self.libname:
            # recursive call in library
            self.output.log('Unsupported request for object %s in %s' % (name, self.comment))
            return
        if self.matrix[-1]:
            heading=self.matrix[-1].heading()	# XXX not really
            # handle translation
            loc=self.loc.biased(self.matrix[-1].m[3][0]*self.scale,
                                -self.matrix[-1].m[3][2]*self.scale)
        else:
            heading=0
            loc=self.loc
        if self.debug:
            self.debug.write("LibraryCall %s\n%s\n" % (name,self.matrix[-1]))
        self.output.objplc.append((loc, heading, self.complexity,
                                   name, round(self.scale,2)))
        if self.altmsl:
            self.output.log('Absolute altitude (%sm) for object %s at (%10.6f, %11.6f) in %s' % (round(self.altmsl,2), name, self.loc.lat, self.loc.lon, self.comment))
            self.altmsl=False	# Don't report again for this object
        elif self.alt:
            self.output.log('Non-zero altitude (%sm) for object %s at (%10.6f, %11.6f) in %s' % (round(self.alt,2), name, self.loc.lat, self.loc.lon, self.comment))

    def RoadStart(self):	# 69:RoadStart, 6b:RiverStart
        # ignored - info should now be in FS2004-style BGL
        self.rrt=True
        self.bgl.seek(8,1)

    def RoadCont(self):		# 6a:RoadCont, 6c:RiverCont
        # ignored - info should now be in FS2004-style BGL
        self.rrt=True
        self.bgl.seek(6,1)

    def TaxiwayStart(self):	# 6e
        (width,x,y,z)=unpack('<hhhh', self.bgl.read(8))
        self.taxiway=(width*self.scale*m2f,
                      self.loc.biased(x*self.scale, z*self.scale))

    def TaxiwayCont(self):	# 6f
        (x,y,z)=unpack('<hhh', self.bgl.read(6))
        if not self.taxiway: return
        (width, start)=self.taxiway
        end=self.loc.biased(x*self.scale, z*self.scale)
        self.taxiway=(width, end)
        heading=start.headingto(end)
        l=start.distanceto(end)
        if l>taxilightspacing/8:
            obj=maketaxilight()
            fname=obj.filename[:-4]
            self.output.objdat[fname]=[obj]
            if l<taxilightspacing/2:
                l=start.distanceto(end)	# Just do one in the middle
            else:
                l=l-taxilightspacing/2
            n=1+int(l/taxilightspacing)
            (x,y,z)=Matrix().headed(heading).transform(0,0,l/n)
            for j in range(n):
                loc=start.biased(x*(j+0.5),z*(j+0.5))
                self.output.objplc.append((loc, 0, 1, fname, 1))

        length=0.5*width + m2f*start.distanceto(end)
        if width>0:
            lights=6
        else:
            lights=1
            width=-width
        if length<1 or width<1:
            return	# This was just for the lighting
        loc=Point((start.lat+end.lat)/2, (start.lon+end.lon)/2)
        surface=1	# Assume asphalt
        self.output.misc.append((10, loc, "xxx %6.2f %6d 0000.0000 0000.0000 %4d 1%d11%d1 %02d 0 0 0.25 0 0000.0000" % (
            heading, length, width, lights, lights, surface)))

    def AreaSense(self):	# 70
        # Assume inside
        (off,n)=unpack('<hH', self.bgl.read(4))
        self.bgl.seek(4*n,1)

    def AddCat(self):		# 74
        (off,cat)=unpack('<2h', self.bgl.read(4))
        # XXX turn cat into poly_os?
        self.stack.append((self.bgl.tell(),False))
        self.bgl.seek(off-6,1)

    def ScaleAGL(self):		# 77
        self.bgl.read(8)	# jump,range (LOD) (may be 0),size,reserved
        (scale,)=unpack('<I', self.bgl.read(4))
        self.scale=65536.0/scale
        (lat,lon,self.alt)=self.LLA()
        self.altmsl=False
        self.loc=Point(lat,lon)
        if lat<0 and not self.output.hemi:
            self.output.hemi=1
            self.setseason()
        
    def ResPnt(self):		# 80
        (idx,)=unpack('<H', self.bgl.read(2))
        (x,y,z,c,c,c,c,c)=self.vtx[idx]
        mat=self.mat[self.m]
        if not mat:
            return	# transparent
        key=(self.loc,self.matrix[-1],self.scale)
        if not key in self.lightdat:
            self.lightdat[key]=[]
        self.lightdat[key].append((self.alt, (x,y,z), mat[0]))
        self.checkmsl()
        
    def Call32(self):		# 2b:AddObj32, 8a:Call32
        (off,)=unpack('<i', self.bgl.read(4))
        if not off: raise struct.error	# infloop
        self.stack.append((self.bgl.tell(),False))
        self.bgl.seek(off-6,1)

    def ReScale(self):		# 83
        self.bgl.read(6)	# jump,range (LOD) (may be 0),size
        (scale,)=unpack('<I', self.bgl.read(4))
        self.scale=65536.0/scale

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
        self.bgl.seek(off-4,1)
        
    def Interpolate(self):	# 9e
        # XXX ignored
        self.anim=True
        self.bgl.read(18)

    def Object(self):		# a0
        # XXX Implement me!
        self.output.log('Unsupported generic building at (%10.6f, %11.6f) in %s' % (self.loc.lat, self.loc.lon, self.comment))
        (size,)=unpack('<H', self.bgl.read(2))
        self.bgl.seek(size-4,1)

    def SpriteVICall(self):	# a7
        (off,x,y,z,p,b,h,vp,vb,vh)=unpack('<4h6H', self.bgl.read(20))
        if not off: raise struct.error	# infloop
        self.stack.append((self.bgl.tell(),self.matrix[-1]))
        newmatrix=Matrix()
        newmatrix=newmatrix.offset(x,y,z)
        if self.debug:
            self.debug.write("SpriteVICall\n")
            if self.matrix[-1]:
                self.debug.write("Old\n%s\n" % self.matrix[-1])
                self.debug.write("New\n%s\n" % newmatrix)
        if self.matrix[-1]:
            newmatrix=newmatrix*self.matrix[-1]
        self.matrix.append(newmatrix)
        if self.debug:
            self.debug.write("Now\n%s\n" % self.matrix[-1])
        if self.libname and h:
            self.billboard=(x,y,z)
            # XXX Implement me!
        self.bgl.seek(off-22,1)

    def TextureRoadStart(self):	# a8
        # ignored - info should now be in FS2004-style BGL
        self.rrt=True
        self.bgl.seek(10,1)
        
    def NewRunway(self):	# aa
        # ignored - info should now be in FS2004-style BGL
        self.rrt=True
        (size,)=unpack('<H', self.bgl.read(2))
        self.bgl.seek(size-4,1)

    # opcodes ad to bd new in FS2002

    def Animate(self):		# ad
        # Just make a static translation matrix
        self.anim=True
        (c,c,c,c,x,y,z)=unpack('<4i3f', self.bgl.read(28))
        newmatrix=Matrix()
        newmatrix=newmatrix.offset(x,y,z)
        if self.debug:
            self.debug.write("Animate\n")
            if self.matrix[-1]:
                self.debug.write("Old\n%s\n" % self.matrix[-1])
                self.debug.write("New\n%s\n" % newmatrix)
        if self.matrix[-1]:
            newmatrix=newmatrix*self.matrix[-1]
        if self.debug:
            self.debug.write("Now\n%s\n" % self.matrix[-1])
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
        if self.debug:
            self.debug.write("TransformMatrix\n")
            if self.matrix[-1]:
                self.debug.write("Old\n%s\n" % self.matrix[-1])
                self.debug.write("New\n%s\n" % newmatrix)
        if self.matrix[-1]:
            newmatrix=newmatrix*self.matrix[-1]
        self.matrix.append(newmatrix)
        if self.debug:
            self.debug.write("Now\n%s\n" % self.matrix[-1])

    def Tag(self):	# b1
        self.bgl.read(20).rstrip(' \0')	# what's this for?
        
    def Light(self):		# b2
        (type,x,y,z,intens,i,i,b,g,r,a,i,i,i)=unpack('<HfffIffBBBBfff',
                                                     self.bgl.read(42))
        # Typical intensities are 20 and 40 - so say 40=max
        if intens<40:
            intens=intens/(40.0*255.0)
        else:
            intens=1/255.0
        key=(self.loc,self.matrix[-1],self.scale)
        if not key in self.lightdat:
            self.lightdat[key]=[]
        self.lightdat[key].append((self.alt,
                                   (x,y,z), (r*intens,g*intens,b*intens)))
        self.checkmsl()
        
    def VertexList(self):	# b5
        self.vtx=[]
        (count,)=unpack('<H', self.bgl.read(2))
        self.bgl.read(4)
        for i in range(count):
            self.vtx.append(unpack('<8f', self.bgl.read(32)))

    def MaterialList(self):	# b6
        self.mat=[]
        self.m=None
        (count,)=unpack('<H', self.bgl.read(2))
        self.bgl.read(4)
        for i in range(count):
            # average of diffuse & ambient
            (dr,dg,db,da)=unpack('<4f', self.bgl.read(16))
            (ar,ag,ab,aa)=unpack('<4f', self.bgl.read(16))
            m=[((dr+ar)/2, (dg+ag)/2, (db+ab)/2)]
            for j in range(2):
                (r,g,b,a)=unpack('<4f', self.bgl.read(16))
                m.append((r,g,b))
            self.bgl.read(4)	# power
            self.mat.append(m)

    def TextureList(self):	# b7
        self.tex=[]
        self.t=None
        (count,)=unpack('<H', self.bgl.read(2))
        self.bgl.read(4)
        for i in range(count):
            cls=unpack('<I', self.bgl.read(4))
            self.bgl.read(12)
            tex=self.bgl.read(64).rstrip(' \0')
            # Extension is ignored by MSFS?
            (s,e)=splitext(tex)
            for ext in [e, '.bmp', '.r8']:
                if exists(join(self.texdir,s+ext)):
                    tex=s+ext
                    break
            # Fix case for case sensitive filesystems
            for f in listdir(self.texdir):
                if tex.lower()==f.lower():
                    tex=f
                    break
            else:
                tex=tex.lower()
            self.tex.append(join(self.texdir, tex))
        
    def SetMaterial(self):	# b8
        (self.m,self.t)=unpack('<2h', self.bgl.read(4))
        if self.m>len(self.mat):
            if self.debug:
                self.debug.write("Bad material %d/%d\n"%(self.m,len(self.mat)))
            self.m=0
        if self.t>len(self.tex):
            if self.debug:
                self.debug.write("Bad texture %d/%d\n" %(self.t,len(self.tex)))
            self.t=-1
        if self.debug and self.t>=0:
            self.debug.write("%s\n" % basename(self.tex[self.t]))
        
    def DrawTriList(self):	# b9
        idx=[]
        first=maxint
        last=0
        (base,count,off)=unpack('<3H', self.bgl.read(6))
        for i in range(off/3):
            (a,b,c)=unpack('<3H', self.bgl.read(6))
            idx.extend([a,b,c])
            first=min(first,a,b,c)
            last=max(last,a,b,c)
        for i in range(len(idx)):
            idx[i]=idx[i]-first
        mat=self.mat[self.m]
        if not mat:
            return	# transparent
        if self.t==None or self.t==-1:
            tex=None
        else:
            tex=self.tex[self.t]
            if self.haze: self.output.haze[tex]=self.haze
        key=(self.loc,self.matrix[-1],self.scale,tex)
        if not key in self.objdat:
            self.objdat[key]=[]
        self.objdat[key].append((mat, self.alt,
                                 self.vtx[base+first:base+last+1], idx, False))
        self.checkmsl()

    def DrawLineList(self):	# ba
        idx=[]
        last=0
        first=maxint
        (base,count,off)=unpack('<3H', self.bgl.read(6))
        for i in range(off/2):
            (a,b)=unpack('<2H', self.bgl.read(4))
            idx.extend([a,b])
            first=min(first,a,b)
            last=max(last,a,b)
        for i in range(len(idx)):
            idx[i]=idx[i]-first
        mat=self.mat[self.m]
        if not mat:
            return	# transparent
        key=(self.loc,self.matrix[-1],self.scale)
        if not key in self.linedat:
            self.linedat[key]=[]
        self.linedat[key].append((self.alt, self.vtx[base+first:base+last+1],
                                  idx, mat[0]))
        self.checkmsl()
        
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
                if self.debug:
                    self.debug.write("Scene %d, %d %d:\n%s\n" % (
                        scene, src,dst, Matrix(m)))
            else:
                if self.debug:
                    self.debug.write("!Unsupported ANIC cmd %x, size %d\n" % (
                        cmd, size))
                self.anim=True
                break
            scene=parent

        if self.debug:
            self.debug.write("TransformIndirect:\n%s\n" % self.matrix[-1])
        self.bgl.seek(pos)


    #def PointVIIndirect(self):	# c5
    # Havn't seen one of these
    #    (off,x,y,z,p,vp,b,vb,h,vh,n)=unpack('<12h', self.bgl.read(22))
    #    self.stack.append((self.bgl.tell(),self.matrix))
    #    p=p*360/65536.0
    #    b=b*360/65536.0
    #    h=h*360/65536.0
    #    self.matrix=self.matrices[n]
    #    self.matrix.offset(x,y,z)
    #    self.matrix.headed(h+self.getvar(vh))
    #    self.matrix.pitched(p+self.getvar(vp))
    #    self.matrix.banked(b+self.getvar(vb))
    #    self.bgl.seek(off-24,1)

    # Ignored opcodes
    
    def NOP(self):
        # 02:NOOP, 05:Surface, 76:BGL, 7d:Perspective, bd:EndVersion
        pass

    def NOPh(self):
        # 30:Brightness, 3f:ShadowCall, 81:AntiAlias, 93: ???
        # ac:ZBias - XXX should generate poly_os n ?
        self.bgl.read(2)
        pass

    def NOPi(self):
        # 89:VarBase32, 9f:Override, bc:BGLVersion
        self.bgl.read(4)
        pass


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

        return (lat,lon,alt)


    def makeobjs(self):
        if not self.lightdat and not self.linedat and not self.objdat:
            return	# Only contained non-scenery stuff
        elif self.libname:
            bname=self.libname
            if self.loc:
                if self.debug:
                    self.debug.write("!Location given for library object\n")
                raise struct.error	# Code assumes no spurious location
        elif self.loc:
            bname=self.srcfile
            if bname.lower()[-4:]=='.bgl':
                bname=bname[:-4]
        else:
            # Must have a location for placement
            if self.debug: self.debug.write("!No location\n")
            raise struct.error

        objdat={}	# (vlight, vline, vt, idx, mattri) by (loc, hdg, tex)

        # Sort throught lights and lines
        for lkey in self.lightdat.keys()+self.linedat.keys():
            (loc, matrix, scale)=lkey
            newmatrix=matrix
            newloc=loc
            heading=0
            
            # Try to find tri data to bundle lights and lines with
            for (oloc, omatrix, oscale, tex) in self.objdat:
                if (oloc==loc and oscale==scale and
                    ((not omatrix and not matrix) or
                     (omatrix and matrix and omatrix.m==matrix.m))):
                    break	# Found matching tri data
            else:
                tex=None	# Oh well, this will be a new object

            if loc and matrix:
                newloc=loc.biased(matrix.m[3][0]*scale, matrix.m[3][2]*scale)
                if matrix.m[1][1]==1:	# No pitch or bank?
                    # Transform at placement time in hope of commonality
                    heading=matrix.heading()
                    if matrix.m[3][1]:
                        # carry over alt
                        newmatrix=Matrix()
                        newmatrix.m[3][1]=matrix.m[3][1]
                    else:
                        newmatrix=None
                else:
                    newmatrix=Matrix(list(matrix.m))
                    newmatrix.m[3][0]=0
                    newmatrix.m[3][2]=0

            if newloc:
                okey=(newloc.lat, newloc.lon, heading, tex)
            else:
                okey=(None, None, 0, tex)
            if not okey in objdat:
                vlight=[]
                vline=[]
                vt=[]
                idx=[]
                mattri=[]
            else:
                (vlight, vline, vt, idx, mattri)=objdat[okey]

            if lkey in self.lightdat:
                for (alt,(x,y,z),(r,g,b)) in self.lightdat[lkey]:
                    if newmatrix:
                        (x,y,z)=newmatrix.transform(x,y,z)
                    vlight.append((x*scale,alt+y*scale,-z*scale, r,g,b))
                
            if lkey in self.linedat:
                for (alt, vtx, i, (r,g,b)) in self.linedat[lkey]:
                    vbase=len(vline)
                    for v in vtx:
                        (x,y,z,nx,ny,nz,tu,tv)=v
                        if newmatrix:
                            (x,y,z)=newmatrix.transform(x,y,z)
                        vline.append((x*scale,alt+y*scale,-z*scale, r,g,b))
                    for j in i:
                        idx.append(vbase+j)

            objdat[okey]=(vlight, vline, vt, idx, mattri)

        # OK now sort throught the objects.
        # Matrix is brought out here to allow for detection of data in a bgl
        # that is duplicated apart from translation and/or rotation by heading
        for lkey in sorted(self.objdat):
            (loc,matrix,scale,tex)=lkey
            newmatrix=matrix
            newloc=loc
            heading=0

            if loc and matrix:
                newloc=loc.biased(matrix.m[3][0]*scale, matrix.m[3][2]*scale)
                if matrix.m[1][1]==1:	# No pitch or bank?
                    # Transform at placement time in hope of commonality
                    heading=matrix.heading()
                    if matrix.m[3][1]:
                        # carry over alt
                        newmatrix=Matrix()
                        newmatrix.m[3][1]=matrix.m[3][1]
                    else:
                        newmatrix=None
                else:
                    newmatrix=Matrix(matrix.m)
                    newmatrix.m[3][0]=0
                    newmatrix.m[3][2]=0
                if self.debug:
                    if tex:
                        self.debug.write("New heading %d, offset (%d,%d), matrix for %s:\n%s\n" % (heading, matrix.m[3][0]*scale, matrix.m[3][2]*scale, basename(tex), newmatrix))
                    else:
                        self.debug.write("New heading %d, offset (%d,%d), matrix for None:\n%s\n" % (heading, matrix.m[3][0]*scale, matrix.m[3][2]*scale, newmatrix))
                    
            # Consolidate with other data that only differs in matrix
            if newloc:
                okey=(newloc.lat, newloc.lon, heading, tex)
            else:
                okey=(None, None, 0, tex)
            if not okey in objdat:
                vlight=[]
                vline=[]
                vt=[]
                idx=[]
                mattri=[]
            else:
                (vlight, vline, vt, idx, mattri)=objdat[okey]

            # Sort to minimise attribute changes
            for (m, alt, vtx, i, dbl) in sorted(self.objdat[lkey]):

                # replace materials with palette texture
                if not tex:
                    (r,g,b)=m[0]
                    r=(round(r*15,0)+0.5)/64
                    g=(round(g*15,0)+0.5)/64
                    b=(round(b*15,0)+0.5)
                    pu=int(b%4)/4.0 + r
                    pv=int(b/4)/4.0 + g
                
                vbase=len(vt)
                firsttri=len(idx)

                for v in vtx:
                    (x,y,z,nx,ny,nz,tu,tv)=v
                    if newmatrix:
                        (x,y,z)=newmatrix.transform(x,y,z)
                        (nx,ny,nz)=newmatrix.rotate(nx,ny,nz)
                    # replace materials with palette texture
                    if not tex:
                        tu=pu
                        tv=pv
                    vt.append((x*scale, alt + y*scale, -z*scale,
                               nx,ny,-nz, tu,tv))
                    
                # Reverse order of tris
                for j in range(0,len(i),3):
                    for k in range(2,-1,-1):
                        idx.append(vbase+i[j+k])

                if mattri:
                    # Consolidate TRI commands if possible
                    (xm, xfirsttri, xlen, xdbl)=mattri[-1]
                    if m==xm and dbl==xdbl:
                        mattri[-1]=(m, xfirsttri, xlen+len(idx)-firsttri, dbl)
                        continue
                mattri.append((m, firsttri, len(idx)-firsttri, dbl))

            if not vlight and not vline and not vt:
                continue	# Only contained non-scenery stuff

            objdat[okey]=(vlight, vline, vt, idx, mattri)

        objs=[]
        for okey in objdat:
            (lat, lon, heading, tex)=okey
            (vlight, vline, vt, idx, mattri)=objdat[okey]
            loc=Point(lat, lon)
            texname=tex
            if tex:
                (fname,ext)=splitext(basename(tex))
                if not ext.lower() in ['.bmp', '.png']:
                    fname+=ext	# For *.xAF etc
                # Spaces not allowed in textures. Avoid Mac/PC interop problems
                fname="%s-%s" % (asciify(bname),
                                 asciify(fname).replace(' ','_'))
            else:
                fname=asciify(bname)
                if vt: texname='Resources/FS2X-palette.png'

            # Check whether this object is a 'decal' and apply poly_os
            poly=0
            minx=minz=maxint
            maxx=maxz=-maxint
            if vt:
                decal=True
                for (x,y,z, nx,ny,nz, tu,tv) in vt:
                    minx=min(minx,x)
                    maxx=max(maxx,x)
                    minz=min(minz,z)
                    maxz=max(maxz,z)
                    if y>=0.125:	# Arbitrary. 0.124 used in UNNT
                        decal=False
                if decal:
                    if (maxx-minx)>NM2m/4 or (maxz-minz)>NM2m/4:    # arbitrary
                        poly=1	# probably orthophoto
                    else:
                        poly=2	# probably detail
                
            # Last check that bounding box of consolidated data is within a
            # reasonable distance of the origin to prevent clipping.
            # Can't do this for library objs, but those are probably
            # reasonable anyway.
            # Don't do for orthophotos, since these need exact alignment
            if not self.libname: # and poly!=1:
                for (x,y,z, r,g,b) in vlight:
                    minx=min(minx,x)
                    maxx=max(maxx,x)
                    minz=min(minz,z)
                    maxz=max(maxz,z)
                for (x,y,z, r,g,b) in vline:
                    minx=min(minx,x)
                    maxx=max(maxx,x)
                    minz=min(minz,z)
                    maxz=max(maxz,z)
                limit=(maxx-minx)*(maxx-minx) + (maxz-minz)*(maxz-minz)
                if 0: #not Point(0,0).within(Point(minx,minz),Point(maxx,maxz))
                    #minx*minx+minz*minz<limit or
                    #minx*minx+maxz*maxz<limit or
                    #maxx*maxx+minz*minz<limit or
                    #maxx*maxx+maxz*maxz<limit):
                    newx=int((minx+maxx)/2)
                    newz=int((minz+maxz)/2)
                    (bx,by,bz)=Matrix().headed(heading).rotate(newx,0,-newz)
                    loc=loc.biased(bx,bz)
                    newv=[]
                    for (x,y,z, r,g,b) in vlight:
                        newv.append((x-newx,y,z-newz, r,g,b))
                    vlight=newv
                    newv=[]
                    for (x,y,z, r,g,b) in vline:
                        newv.append((x-newx,y,z-newz, r,g,b))
                    vline=newv
                    newv=[]
                    for (x,y,z, nx,ny,nz, tu,tv) in vt:
                        newv.append((x-newx,y,z-newz, nx,ny,nz, tu,tv))
                    vt=newv
                    if self.debug and tex:
                        self.debug.write("New origin for %s: (%d,%d)\n" % (
                            basename(tex), newx, newz))
                    elif self.debug:
                        self.debug.write("New origin for None: (%d,%d)\n" % (
                            newx, newz))

            # Finally build the object
            obj=Object(fname+'.obj', self.comment, texname, vlight, vline, vt,
                       idx, mattri, poly)
            if self.libname:
                objs.append(obj)
            else:
                # handle multiple objs with same tex at different locs
                if fname in self.output.objdat:
                    iname=fname
                    i=0
                    while(1):
                        # See if this is a duplicate
                        if i:
                            fname="%s-%d" % (iname, i)
                            obj.filename=fname+'.obj'
                        if not fname in self.output.objdat:
                            break	# no match - new object
                        if obj==self.output.objdat[fname][0]:
                            break	# matched - re-use this object
                        i+=1
                
                self.output.objdat[fname]=[obj]
                self.output.objplc.append((loc, heading,
                                           self.complexity, fname, 1))

        # Add objs to library with one name
        if self.libname and objs:
            self.output.objdat[self.libname]=objs


    def checkmsl(self):
        if self.altmsl:
            self.output.log('Absolute altitude (%sm) for object at (%10.6f, %11.6f) in %s' % (round(self.altmsl,2), self.loc.lat, self.loc.lon, self.comment))
            self.altmsl=False	# Don't report again for this object
            return True
        else:
            return False


    def getvar(self, var):
        if var in self.vars:
            val=self.vars[var]
            return val
        else:
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


# Handle exception section
def ProcEx(bgl, output):
    while 1:
        (c,)=unpack('<B',bgl.read(1))
        if c==0:
            return
        elif c==3:
            # Exclusion
            (mask,n,s,e,w)=unpack('<H4I',bgl.read(18))
            if mask&1:
                # objects
                n=n*360.0/cirp
                s=s*360.0/cirp
                e=e*360.0/0x100000000
                if e>180: e-=360
                w=w*360.0/0x100000000
                if w>180: w-=360
                output.exc.append(('obj', Point(s,w), Point(n,e)))
                output.exc.append(('fac', Point(s,w), Point(n,e)))
        elif c==4:
            # Exception - ignore
            bgl.seek(12,1)
        else:
            raise struct.error


def subdivide(vtx):
    # Subdivide concave polygon into tris
    idx=[]
    count=len(vtx)
    
    if count<=4:
        # don't bother for quads
        for i in range(1,count-1):
            idx.extend([0,i,i+1])
        return (vtx, idx)
        
    planar=True
    ax=ay=az=au=av=0
    vx=[]
    vy=[]
    (c,y0,c,c,c,c,c,c)=vtx[0]
    for i in range(count):
        (x,y,z, nx,ny,nz, tu, tv)=vtx[i]
        if y!=y0:
            planar=False
        ax+=x
        ay+=y
        az+=z
        au+=tu
        av+=tv
        vx.append(x)
        vy.append(z)

    if not planar:
        # Just add a new vertex in the middle and use that in every triangle
        ax/=float(count)
        ay/=float(count)
        az/=float(count)
        for i in range(1,count-1):
            idx.extend([0,i,i+1])
        vtx.insert(0, (ax,ay,az, nx,ny,nz, au,av))
        idx.extend([0,count-1,count, 0,count,1])
        return (vtx, idx)

    # Simple O(n2) Greedy algorithm.
    # Remove candidate vertex if triangle formed by it and adjacent
    # vertices doesn't cross any edges.

    # Determine order
    area2=0
    for i in range(count):
        area2+=(vx[i]*vy[(i+1)%count] - vx[(i+1)%count]*vy[i])

    candidate=-1		# index of tested vertex
    count=len(vx)
    remaining=count
    vi=[True for i in range(count)]	# whether vertex is still a candidate
    edges=[]
    for i in range(count):
        edges.append((i,(i+1)%count))
    infloop=0

    # This needs to work for integer values of x and y
    while remaining>4:
        if infloop>count:
            # Shouldn't happen
            #if self.debug: self.debug.write('!InfLoop in polygon\n')
            return(vtx,idx)

        # Candidate and adjacent vertices
        candidate=(candidate+1)%count
        while not vi[candidate]: candidate=(candidate+1)%count
        p1=(candidate+1)%count
        while not vi[p1]: p1=(p1+1)%count
        p2=(candidate-1)%count
        while not vi[p2]: p2=(p2-1)%count

        # Is this triangle outside?
        a=0
        ii=[candidate, p1, p2]
        for i in range(3):
            a+=(vx[ii[i]]*vy[ii[(i+1)%3]] - vx[ii[(i+1)%3]]*vy[ii[i]])
        if area2*a<0:
            # this triangle no good
            infloop+=1
            continue

        # Does this triangle cross any edge (including those we've removed)?
        for edge in edges:
            (p3,p4)=edge
            if p3==p1 or p3==p2 or p4==p1 or p4==p2:
                continue
            d=(vy[p4]-vy[p3])*(vx[p2]-vx[p1])-(vx[p4]-vx[p3])*(vy[p2]-vy[p1])
            if d==0:
                continue	# parallel
            a=(vx[p4]-vx[p3])*(vy[p1]-vy[p3])-(vy[p4]-vy[p3])*(vx[p1]-vx[p3])
            b=(vx[p2]-vx[p1])*(vy[p1]-vy[p3])-(vy[p2]-vy[p1])*(vx[p1]-vx[p3])
            if a<0 or a>d or b<0 or b>d:
                continue	# no intersection
            # intersection - this triangle no good
            infloop+=1
            break
        else:
            # No intersection - make triangle
            idx.extend([candidate, p1, p2])
            vi[candidate]=False
            edges.insert(0, (p2,p1))	# so tested first
            remaining-=1
            infloop=0

    p1=0
    while not vi[p1]: p1+=1
    p2=p1+1
    while not vi[p2]: p2+=1
    p3=p2+1
    while not vi[p3]: p3+=1
    p4=p3+1
    while not vi[p4]: p4+=1
    idx.extend([p1,p2,p3, p1,p3,p4])
    return(vtx,idx)


