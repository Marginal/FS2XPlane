# Import BGL

from math import acos, cos, fmod, sin
from os.path import basename, dirname, exists, join, normpath, pardir
import struct
from struct import unpack

from convutil import cirp, d2r, r2d, m2f, NM2m, complexity, Object, Point

# Read BGL header
class Parse:
    def __init__(self, bgl, name, srcfile, output):
        pre2002=False
        errors=False
        matrices=[]
        if 0:	#tr:	# TRAN data from MDL file
            for i in range(len(tr)/16):
                matrices.append(Matrix([[tr[i   ],tr[i+ 1],tr[i+ 2],tr[i+ 3]],
                                        [tr[i+ 4],tr[i+ 5],tr[i+ 6],tr[i+ 7]],
                                        [tr[i+ 8],tr[i+ 9],tr[i+10],tr[i+11]],
                                        [tr[i+12],tr[i+13],tr[i+14],tr[i+15]]]))
        for section in [42,54,58,62,102,114]:
            bgl.seek(section)
            (secbase,)=unpack('<I',bgl.read(4))
            if (secbase):
                #print "Section %2d %x" % (section, secbase)
                bgl.seek(secbase)
                if section==42:
                    output.log('Skipping traffic data in file %s' % name)
                    pass
                elif section==54:
                    output.log('Skipping terrain data in file %s' % name)
                    pass
                elif section==58:
                    # OBJECT data
                    areano=0
                    while 1:
                        # LatBand
                        posl=bgl.tell()
                        #print "LatBand %x" % posl
                        (c,)=unpack('<B', bgl.read(1))
                        if c==0:
                            break
                        (foo,off)=unpack('<IH', bgl.read(6))
                        bgl.seek(secbase+off)
                        while 1:
                            # Header
                            areano+=1                        
                            posa=bgl.tell()
                            #print "Area %x" % posa
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
                                #print hex(c)
                                raise struct.error	# wtf?
                            try:
                                pre2002=(ProcScen(bgl, posa+l, None,
                                                  name, srcfile, output,
                                                  matrices).old or
                                         pre2002)
                            except struct.error:
                                output.log("Can't parse area #%d in %s" % (
                                    areano, name))
                            bgl.seek(posa+l)
                        bgl.seek(posl+7)
                elif section==62:
                    # LIBRARY data
                    objno=0
                    while 1:
                        objno+=1
                        pos=bgl.tell()
                        #print "Obj %x" % pos
                        (off,)=unpack('<I', bgl.read(4))
                        if off==0:
                            break
                        bgl.seek(secbase+off)
                        (a,b,c,d)=unpack('<4I', bgl.read(16))
                        bgl.read(1)
                        (hdsize,l)=unpack('<2I', bgl.read(8))
                        bgl.seek(hdsize-25, 1)
                        #print "%08x%08x%08x%08x Off %x, enda=%x" % (
                        #    a,b,c,d, bgl.tell(), secbase+off+hdsize+l)
                        try:
                            pre2002=(ProcScen(bgl, secbase+off+hdsize+l,
                                              "%08x%08x%08x%08x"%(a,b,c,d),
                                              name, srcfile, output,
                                              matrices).old or
                                     pre2002)
                        except struct.error:
                            output.log("Can't parse object %08x%08x%08x%08x in %s" % (a,b,c,d, name))
                        bgl.seek(pos+20)
                elif section==102:
                    output.log('Skipping misc data in file %s' % name)
                    pass
                elif section==114:
                    try:
                        ProcEx(bgl, output)
                    except struct.error:
                        errors=True
                else:
                    errors=True
        if errors:
            output.log("Can't parse %s" % name)
        elif pre2002:
            output.log("Skipping pre-FS2002 scenery in %s" % name)
                        

class Matrix:
    def __init__(self, v=None):
        if v:
            self.m=v
        else:
            self.m=[[1,0,0,0],
                    [0,1,0,0],
                    [0,0,1,0],
                    [0,0,0,1]]

    def transform(self, x, y, z):
        m=self.m
        return (m[0][0]*x + m[1][0]*y + m[2][0]*z + m[3][0],
                m[0][1]*x + m[1][1]*y + m[2][1]*z + m[3][1],
                m[0][2]*x + m[1][2]*y + m[2][2]*z + m[3][2])

    def transformn(self, x, y, z):
        m=self.m
        return (m[0][0]*x + m[1][0]*y + m[2][0]*z,
                m[0][1]*x + m[1][1]*y + m[2][1]*z,
                m[0][2]*x + m[1][2]*y + m[2][2]*z)

    def offset(self, x, y, z):
        self.m[3]=[self.m[3][0]+x, self.m[3][1]+y, self.m[3][2]+z, 1]
        
    def headed(self, angle):
        # about y axis
        a=d2r*angle
        t=Matrix([[cos(a), 0,-sin(a), 0],
                  [     0, 1,      0, 0],
                  [sin(a), 0, cos(a), 0],
                  [     0, 0,      0, 1]])
        self=t*self
          
    def pitched(self, angle):
        # about x axis
        a=d2r*angle
        t=Matrix([[1,      0,      1, 0],
                  [0, cos(a),-sin(a), 0],
                  [0, sin(a), cos(a), 0],
                  [0,      0,      0, 1]])
        self=t*self

    def banked(self, angle):
        # about x axis
        a=d2r*angle
        t=Matrix([[cos(a),-sin(a), 0, 0],
                  [sin(a), cos(a), 0, 0],
                  [0,      0,      1, 0],
                  [0,      0,      0, 1]])
        self=t*self

    def __mul__(self, other):
        # self*other
        a=self.m
        b=other.m
        m=[[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        for i in range(4):
            for j in range(4):
                x=0
                for k in range(4):
                    x=x+a[i][k]*b[k][j]
                m[i][j]=x
        return m

# handle section 9 and 10 scenery. libname!=None if this is a library
class ProcScen:
    def __init__(self, bgl, enda, libname, comment, srcfile, output, matrices):

        self.old=False	# Old style scenery found and skipped

        self.bgl=bgl
        self.libname=libname
        self.comment=comment
        self.output=output
        self.matrices=matrices	# From TRAN section of MDL file
        self.texdir=normpath(join(join(dirname(srcfile), pardir), 'Texture'))
        
        # State
        self.complexity=1
        self.loc=None
        self.alt=0
        self.altmsl=0
        self.matrix=None
        self.scale=1.0
        self.stack=[]	# (return address, matrix)
        self.tex=[]
        self.mat=[]	# [[(ar,ag,ab),(sr,sg,sb),(er,eg,eb)]]
        self.vtx=[]
        self.m=None	# Index into mat
        self.t=None	# Index into tex
        self.billboard=None	# Emulating billboarding in a libary defn

        self.objdat={}	# (mat, scale, alt, matrix, vtx[], idx[]) by (loc, tex)
        self.linedat={}	# (scale, alt, matrix, vtx[], idx[], (r,g,b)) by loc
        self.lightdat={}# (scale, alt, matrix, (x,y,z), (r,g,b)) by loc

        self.vars={
            # Vars not listed are assumed to be 0
            0: 0,	# dummy
            0x282: 1,	# beacon: rotating bitmap shifted 1 bit/3 sec
            0x28c: 2,	# tod: 2|4 indicates night?
            0x30A: 6,	# beacon_2: 16-bit bitmap with 0x0506 add/3 sec
            0x30C: 8,	# beacon_3: 16-bit bitmap with 0x0708 add/3 sec 
            0x30E: 0xa,	# beacon_4: 16-bit bitmap with 0x090A add/3 sec 
            0x310: 0xc,	# beacon_5: 16-bit bitmap with 0x0B0C add/3 sec 
            0x33a: 0,	# rbias: eye to object distance in meters II.FF
            0x33b: 0,	# rbias_1: eye to object distance in meters IIII
            0x346: 5,	# image_complex: density of the scenery 1-5
            0x37e: 0,	# xv: rotated X-axis eye to object distance
            0x382: 0,	# yv: rotated Y-axis eye to object distance
            0x386: 0,	# zv: rotated Z-axis eye to object distance
            0x389: 12,	# zulu hours in the day - Midday
            0x38a: 92,	# zulu day in the year - Spring
            0x6F8: 1,	# season: 1=Spring
            0xc72: 5,	# ground wind velocity [mph?]
            0xc74: 0,	# ground wind direction [units?]
            }

        cmds={0x0d:self.Jump,
              0x1a:self.ResList,
              0x1e:self.NOPh,
              0x20:self.FaceTTMap,
              0x21:self.IfIn3,
              0x22:self.Return,
              0x23:self.Call,
              0x24:self.IfIn1,
              0x25:self.SeparationPlane,
              0x26:self.SetWrd,
              0x29:self.GResList,
              0x2b:self.Call32,
              0x2f:self.Scale,
              0x32:self.Call,
              0x33:self.Instance,
              0x35:self.PntRow,
              0x37:self.Point,
              0x38:self.NOP,
              0x39:self.IfMsk,
              0x43:self.Texture2,
              0x46:self.PointVICall,
              0x3f:self.NOPh,
              0x51:self.NewLColor,
              0x52:self.NewLColor,
              0x55:self.SurfaceType,
              0x5f:self.IfSizeV,
              0x63:self.LibraryCall,
              0x76:self.NOP,
              0x74:self.AddCat,
              0x77:self.ScaleAGL,
              0x7a:self.FaceTTMap,
              0x83:self.ReScale,
              0x88:self.Jump32,
              0x89:self.NOPi,
              0x8a:self.Call32,
              0x96:self.CrashStart,
              0x9e:self.Interpolate,
              0x9f:self.NOPi,
              0xa0:self.Object,
              0xa7:self.SpriteVICall,
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
            #print "%x:" % pos,
            if pos>=enda:
                self.makeobjs()
                if pos>enda:
                    raise struct.error
                #print "enda"
                return            
            (cmd,)=unpack('<H',bgl.read(2))
            if cmd==0 or (cmd==0x22 and not self.stack):
                #print "cmd 00"
                self.makeobjs()
                return
            elif cmd in cmds:
                #print "cmd %x" % cmd
                cmds[cmd]()
            else:
                #print "%x: cmd %x" % (pos, cmd)
                self.old=True
                self.makeobjs()	# Try to go with what we've got so far
                return


    def Jump(self):		# 0d
        (off,)=unpack('<h', self.bgl.read(2))
        self.bgl.seek(off-4,1)

    def ResList(self):		# 1a
        (index,count)=unpack('<2H', self.bgl.read(4))
        if len(self.vtx)<index:
            self.vertex.extend([None for i in range(index-len(self,vtx))])
        for i in range(index,index+count):
            (x,y,z)=unpack('<3h', self.bgl.read(6))
            v=(x,y,z, 0,0,0, 0,0)
            if i==len(self.vtx):
                self.vtx.append(v)
            else:
                self.vtx[i]=v

    def FaceTTMap(self):	# 20:FaceTTMap, 7a:GFaceTTMap
        (count,nx,ny,nz)=unpack('<H3h', self.bgl.read(8))
        if (count!=4): raise struct.error
        nx=nx/32767.0
        ny=ny/32767.0
        nz=nz/32767.0
        self.bgl.read(4)
        vtx=[]
        for i in range(count):
            (idx,tu,tv)=unpack('<H2h', self.bgl.read(6))
            (x,y,z,c,c,c,c,c)=self.vtx[idx]
            vtx.append((x,y,z, nx,ny,nz, tu/256.0,tv/256.0))
        if self.t==-1:
            tex=None
        else:
            tex=self.tex[self.t]
        key=(self.loc,tex)
        if not key in self.objdat:
            self.objdat[key]=[]            
        self.objdat[key].append(([(1,1,1),(0,0,0),(0,0,0)],
                                 self.scale, self.alt, self.matrix,
                                 vtx, [0,1,2,2,3,0]))
        self.checkmsl()
        
    def IfIn3(self):		# 21
        var=[0,0,0]
        mins=[0,0,0]
        maxs=[0,0,0]
        (off, var[0], mins[0], maxs[0],
         var[1], mins[1], maxs[1],
         var[2], mins[2], maxs[2])=unpack('<10h', self.bgl.read(20))
        for i in range(3):
            if var[i]==0x346: self.complexity=complexity(mins[i])
            val=self.getvar(var[i])
            if val<mins[i] or val>maxs[i]:
                self.bgl.seek(off-22,1)
                break

    def Return(self):		# 22
        (off,self.matrix)=self.stack.pop()
        self.bgl.seek(off)

    def Call(self):		# 23:Call, 32:PerspectiveCall
        (off,)=unpack('<h', self.bgl.read(2))
        self.stack.append((self.bgl.tell(),self.matrix))
        self.bgl.seek(off-4,1)

    def IfIn1(self):		# 24
        (off, var, vmin, vmax)=unpack('<4h', self.bgl.read(8))
        if var==0x346: self.complexity=complexity(vmin)
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
            self.vertex.extend([None for i in range(index-len(self,vtx))])
        for i in range(index,index+count):
            (x,y,z,nx,ny,nz)=unpack('<6h', self.bgl.read(12))
            v=(x,y,z, nx/32767.0,ny/32767.0,nz/32767.0, 0,0)
            if i==len(self.vtx):
                self.vtx.append(v)
            else:
                self.vtx[i]=v

    def Scale(self):		# 2f
        self.bgl.read(8)	# jump,range (LOD) (may be 0),size,reserved
        (scale,)=unpack('<I', self.bgl.read(4))
        self.scale=65536.0/scale
        (lat,lon,self.altmsl)=self.LLA()
        self.alt=0
        self.loc=Point(lat,lon)

    def Instance(self):		# 33
        (off,p,b,h)=unpack('<4h', self.bgl.read(8))
        self.stack.append((self.bgl.tell(),self.matrix))
        p=p*360/65536.0
        b=b*360/65536.0
        h=h*360/65536.0
        self.matrix=Matrix()
        self.matrix.headed(h)
        self.matrix.pitched(p)
        self.matrix.banked(b)
        self.bgl.seek(off-10,1)

    def PntRow(self):		# 35
        (sx,sy,sz,ex,ey,ez,count)=unpack('<6hH', self.bgl.read(14))
        if count>1:
            dx=(ex-sx)/(count-1.0)
            dy=(ey-sy)/(count-1.0)
            dz=(ez-sz)/(count-1.0)
        else:
            dx=dy=dz=0
        if not self.loc in self.lightdat:
            self.lightdat[self.loc]=[]
        for i in range(count):
            self.lightdat[self.loc].append((self.scale, self.alt, self.matrix,
                                            (sx+i*dx,sy+i*dy,sz+i*dz),
                                            self.mat[self.m][0]))
        self.checkmsl()
        
    def Point(self):		# 37
        (x,y,z)=unpack('<3h', self.bgl.read(6))
        if not self.loc in self.lightdat:
            self.lightdat[self.loc]=[]
        self.lightdat[self.loc].append((self.scale, self.alt, self.matrix,
                                        (x,y,z), self.mat[self.m][0]))
        self.checkmsl()
        
    def IfMsk(self):		# 39
        (off, var)=unpack('<2h', self.bgl.read(4))
        (mask,)=unpack('<H', self.bgl.read(2))
        val=self.getvar(var)
        if val&mask==0:
            self.bgl.seek(off-8,1)

    def Texture2(self):		# 43
        (size,)=unpack('<H', self.bgl.read(2))
        self.bgl.read(8)
        self.tex=[join(self.texdir, self.bgl.read(size-12).rstrip('\0'))]
        self.t=0
        
    def PointVICall(self):	# 46
        (off,x,y,z,p,vp,b,vb,h,vh)=unpack('<10h', self.bgl.read(20))
        self.stack.append((self.bgl.tell(),self.matrix))
        p=p*360/65536.0
        b=b*360/65536.0
        h=h*360/65536.0
        self.matrix=Matrix()
        self.matrix.offset(x,y,z)
        self.matrix.headed(h+self.getvar(vh))
        self.matrix.pitched(p+self.getvar(vp))
        self.matrix.banked(b+self.getvar(vb))
        if self.libname and h:
            self.billboard=(x,y,z)
            # XXX Implement me!
        self.bgl.seek(off-22,1)

    def NewLColor(self):	# 51: NewLColor, 52: NewSColor
        (c,)=unpack('H', self.bgl.read(2))
        self.m=0
        self.mat=[[self.unicol(c),(0,0,0),(0,0,0)]]
        
    def SurfaceType(self):	# 55
        #self.old=True
        (sfc, cnd, x, z, alt)=unpack('<BBhhh', self.bgl.read(8))
        # Don't do this - area tends to be way too big
        if 0:	#sfc==0:	# Hard
            smap={1:2, 2:1, 3:3, 4:12, 5:5, 6:2, 7:2, 8:13}	# 0:4?
            if cnd in smap:
                code=smap[cnd]
            else:
                code=1	# Asphalt
            if self.matrix:
                heading=r2d*acos(self.matrix.m[0][0])	# XXX not really
            else:
                heading=0
            length=m2f*x*self.scale
            width=m2f*z*self.scale
            self.output.misc.append((10, self.loc, 'xxx %6.2f %6d 0000.0000 0000.0000 %4d 111111 %02d 0 0 0.25 0 0000.0000' % (heading, length, width, code)))

    def IfSizeV(self):		# 5f
        # Assume in range - infinite size
        (off, a, b)=unpack('<3h', self.bgl.read(6))

    def LibraryCall(self):	# 63
        (off,a,b,c,d)=unpack('<hIIII', self.bgl.read(18))
        name="%08x%08x%08x%08x" % (a,b,c,d)
        if self.matrix:
            heading=r2d*acos(self.matrix.m[0][0])	# XXX not really
            loc=self.loc.biased(self.matrix.m[3][0], self.matrix.m[3][2])
        else:
            heading=0
            loc=self.loc
        # handle translation
        self.output.objplc.append((loc, heading, self.complexity,
                                   name, round(self.scale,2)))
        if not self.checkmsl() and self.alt:
            self.output.log('Non-zero altitude (%sm) for object %s at [%10.6f, %11.6f] in %s' % (round(self.alt,2), name, self.loc.lat, self.loc.lon, self.comment))

    def AddCat(self):		# 74
        (off,cat)=unpack('<2h', self.bgl.read(4))
        # XXX turn cat into poly_os?
        self.stack.append((self.bgl.tell(),self.matrix))
        self.bgl.seek(off-6,1)

    def ScaleAGL(self):		# 77
        self.bgl.read(8)	# jump,range (LOD) (may be 0),size,reserved
        (scale,)=unpack('<I', self.bgl.read(4))
        self.scale=65536.0/scale
        (lat,lon,self.alt)=self.LLA()
        self.altmsl=False
        self.loc=Point(lat,lon)
        
    def Call32(self):		# 2b: AddObj32, 8a:Call32
        (off,)=unpack('<i', self.bgl.read(4))
        self.stack.append((self.bgl.tell(),self.matrix))
        self.bgl.seek(off-6,1)

    def ReScale(self):		# 83
        self.bgl.read(6)	# jump,range (LOD) (may be 0),size
        (scale,)=unpack('<I', self.bgl.read(4))
        self.scale=65536.0/scale

    def Jump32(self):		# 88
        (off,)=unpack('<i', self.bgl.read(4))
        self.bgl.seek(off-6,1)

    def CrashStart(self):	# 96
        # Skip crash code
        (off,)=unpack('<h', self.bgl.read(2))
        self.bgl.seek(off-4,1)
        
    def Interpolate(self):	# 9e
        # XXX ignored
        self.bgl.read(18)

    def Object(self):		# a0
        # XXX Implement me!
        self.output.log('Unsupported generic building at [%10.6f, %11.6f] in %s' % (self.loc.lat, self.loc.lon, self.comment))
        (size,)=unpack('<H', self.bgl.read(2))
        self.bgl.seek(size-4,1)

    def SpriteVICall(self):	# a7
        (off,x,y,z,p,b,h,vp,vb,vh)=unpack('<10h', self.bgl.read(20))
        self.stack.append((self.bgl.tell(),self.matrix))
        self.matrix=Matrix()
        self.matrix.offset(x,y,z)
        if self.libname and h:
            self.billboard=(x,y,z)
            # XXX Implement me!
        self.bgl.seek(off-22,1)

    def NewRunway(self):	# aa
        # ignored - info should now be in FS2004-style BGL
        #self.old=True
        (size,)=unpack('<H', self.bgl.read(2))
        self.bgl.seek(size-4,1)

    # opcodes ad to bd new in FS2002

    def Animate(self):		# ad
        # Just make a static translation matrix
        (c,c,c,c,tx,ty,tz)=unpack('<4i3f', self.bgl.read(28))
        self.matrix=Matrix()
        self.matrix.offset(tx,ty,tz)

    def TransformEnd(self):	# ae
        self.matrix=None
        
    def TransformMatrix(self):	# af
        (tx,ty,tz)=unpack('<3f', self.bgl.read(12))
        (q00,q01,q02, q10,q11,q12, q20,q21,q22)=unpack('<9f',self.bgl.read(36))
        self.matrix=Matrix([[q00,q01,q02,0],
                            [q10,q11,q12,0],
                            [q20,q21,q22,0],
                            [tx,ty,tz,1]])

    def Tag(self):	# b1
        self.bgl.read(20).rstrip('\0')	# what's this for?
        
    def Light(self):		# b2
        (type,x,y,z,intens,i,i,b,g,r,a,i,i,i)=unpack('<HfffIffBBBBfff',
                                                     self.bgl.read(42))
        # Typical intensities are 20 and 40 - so say 40=max
        if intens<40:
            intens=intens/(40.0*255.0)
        else:
            intens=1/255.0
        if not self.loc in self.lightdat:
            self.lightdat[self.loc]=[]
        self.lightdat[self.loc].append((self.scale, self.alt, self.matrix,
                                        (x,y,z),
                                        (r*intens,g*intens,b*intens)))
        self.checkmsl()
        
    def VertexList(self):	# b5
        if self.vtx: raise struct.error
        (count,)=unpack('<H', self.bgl.read(2))
        self.bgl.read(4)
        for i in range(count):
            self.vtx.append(unpack('<8f', self.bgl.read(32)))

    def MaterialList(self):	# b6
        if self.mat: raise struct.error
        (count,)=unpack('<H', self.bgl.read(2))
        self.bgl.read(4)
        for i in range(count):
            # weighted average of diffuse & ambient
            (dr,dg,db,da)=unpack('<4f', self.bgl.read(16))
            (ar,ag,ab,aa)=unpack('<4f', self.bgl.read(16))
            daa=da+aa
            if daa!=0:
                m=[((dr*da+ar*aa)/daa, (dg*da+ag*aa)/daa, (db*da+ab*aa)/daa)]
            else:
                m=[(0,0,0)]
            for j in range(2):
                (r,g,b,a)=unpack('<4f', self.bgl.read(16))
                m.append((r,g,b))
            self.bgl.read(4)	# power
            self.mat.append(m)

    def TextureList(self):	# b7
        if self.tex: raise struct.error
        (count,)=unpack('<H', self.bgl.read(2))
        self.bgl.read(4)
        for i in range(count):
            cls=unpack('<I', self.bgl.read(4))
            self.bgl.read(12)
            self.tex.append(join(self.texdir, self.bgl.read(64).rstrip('\0')))
        
    def SetMaterial(self):	# b8
        (self.m,self.t)=unpack('<2h', self.bgl.read(4))
        
    def DrawTriList(self):	# b9
        idx=[]
        last=0
        (base,count,off)=unpack('<3H', self.bgl.read(6))
        for i in range(off/3):
            (a,b,c)=unpack('<3H', self.bgl.read(6))
            idx.extend([a,b,c])
            last=max(last,a,b,c)
        if self.t==-1:
            tex=None
        else:
            tex=self.tex[self.t]
        key=(self.loc,tex)
        if not key in self.objdat:
            self.objdat[key]=[]
        self.objdat[key].append((self.mat[self.m],
                                 self.scale, self.alt, self.matrix,
                                 self.vtx[base:base+last+1], idx))
        self.checkmsl()

    def DrawLineList(self):	# ba
        idx=[]
        last=0
        (base,count,off)=unpack('<3H', self.bgl.read(6))
        for i in range(off/2):
            (a,b)=unpack('<2H', self.bgl.read(4))
            idx.extend([a,b])
            last=max(last,a,b)
        if not self.loc in self.linedat:
            self.linedat[self.loc]=[]
        self.linedat[self.loc].append((self.scale, self.alt, self.matrix,
                                       self.vtx[base:base+last+1], idx,
                                       self.mat[self.m][0]))
        self.checkmsl()
        
    # opcodes c0 and above new in FS2004

    #def AnimateIndirect(self):	# c3
    #only appears in ANIC section

    def SetMatrixIndirect(self):	# c4
        # n=index into SCEN section of MDL file
        # Ignore!
        (n,)=unpack('<H', self.bgl.read(2))
        self.matrix=None

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
    #    if self.libname and h:
    #        self.billboard=(x,y,z)
    #        # XXX Implement me!
    #    self.bgl.seek(off-24,1)

    def TransformIndirect(self):	# c6
        # only appears in ANIC section
        (n,o)=unpack('<2H', self.bgl.read(4))
        self.matrix=self.matrices[n]

    # Ignored opcodes
    
    def NOP(self):
        # 38:Concave, 76:Perspective, bd: EndVersion
        pass

    def NOPh(self):
        # 1e:Haze, 3f:ShadowCall
        # ac:ZBias - XXX should generate poly_os n ?
        self.bgl.read(2)
        pass

    def NOPi(self):
        # 89:VarBase32, 9f:Override, bc:BGLVersion
        self.bgl.read(4)
        pass


    # helper to read lat, lon, alt
    def LLA(self):
        (lo,hi)=unpack('<HI',self.bgl.read(6))
        if hi>=0:
            lat=hi+lo/65536.0
        else:
            lat=-(~hi+(~lo+1))/65536.0
        lat=lat*360/cirp
        (lo,hi)=unpack('<HI',self.bgl.read(6))
        if hi>=0:
            lon=hi+lo/65536.0
        else:
            lon=-(~hi+(~lo+1))/65536.0
        lon=lon*360.0/0x100000000
        if lon>180: lon-=360
        
        (lo,hi)=unpack('<HI',self.bgl.read(6))
        if hi>=0:
            alt=hi+lo/65536.0
        else:
            alt=-(~hi+(~lo+1))/65536.0

        return (lat,lon,alt)


    def makeobjs(self):
        if self.libname:
            bname=self.libname
        elif self.loc:	# Must have a location for placement
            bname=self.comment
            if bname.lower()[-4:]=='.bgl':
                bname=bname[:-4]
        elif not self.lightdat and not self.linedat and not self.objdat:
            # Might have only contained non-scenery stuff
            return
        else:
            raise struct.error

        # Add dummy objs so lights and lines are picked up
        for loc in self.lightdat.keys()+self.linedat.keys():
            for (oloc,otex) in self.objdat:
                if oloc==loc:
                    break
            else:
                self.objdat[(loc,None)]=[(None, 0, 0, None,[], [])]

        # OK now sort throught the objects
        objs=[]
        for (loc,tex) in sorted(self.objdat):
            vlight=[]
            vline=[]
            vt=[]
            idx=[]
            mattri=[]
            objcount=0	# number of objs in output.objdat that we've added
            
            if objcount==0:
                # Add lights and lines to first obj
                if loc in self.lightdat:
                    for (scale, alt, matrix,
                         (x,y,z), (r,g,b)) in self.lightdat[loc]:
                        if matrix:
                            (x,y,z)=matrix.transform(x,y,z)
                        vlight.append((alt+x*scale,alt+y*scale,alt-z*scale,
                                       r,g,b))
                
                if loc in self.linedat:
                    for (scale, alt, matrix, vtx, i,
                         (r,g,b)) in self.linedat[loc]:
                        for v in vtx:
                            (x,y,z,nx,ny,nz,tu,tv)=v
                            if matrix:
                                (x,y,z)=matrix.transform(x,y,z)
                            vline.append((alt+x*scale,alt+y*scale,alt-z*scale,
                                          r,g,b))
                        for ii in i:
                            idx.append(ii)
            objcount+=1

            # Sort to minimise attribute changes
            for (m, scale, alt, matrix,
                 vtx, i) in sorted(self.objdat[(loc,tex)]):
                if not vtx:
                    continue
                
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
                    
                isterrain=True
                mins=0
                maxs=0
                for v in vtx:
                    (x,y,z,nx,ny,nz,tu,tv)=v
                    if matrix:
                        (x,y,z)=matrix.transform(x,y,z)
                        (nx,ny,nz)=matrix.transformn(nx,ny,nz)
                    # check if this is really like a terrain replacement
                    #if y:
                    #    isterrain=False
                    #else:
                    #    mins=min(mins,x*scale,y*scale)
                    #    maxs=max(maxs,x*scale,y*scale)
                    # replace materials with palette texture
                    if not tex:
                        tu=pu
                        tv=pv
                    vt.append((x*scale, alt + y*scale, -z*scale,
                               nx,ny,-nz, tu,tv))
                if 0:	#isterrain and (maxs-mins)>NM2m/4:
                    self.output.log('Skipping terrain %d %s' % (maxs-mins,basename(tex)))
                    vt[vbase:]=[]	# Lose the vertices we just addded
                    continue
                    
                # Reverse order of tris
                for j in range(0,len(i),3):
                    for k in range(2,-1,-1):
                        idx.append(vbase+i[j+k])
                mattri.append((m, firsttri, len(idx)-firsttri))

            if not vlight and not vline and not vt:
                continue
            
            texname=tex
            if tex:
                fname="%s-%s" % (bname, basename(tex).lower()[:-4])
            else:
                fname=bname
                if vt: texname='.\\palette.png'
                
            obj=Object(fname+'.obj', self.comment, texname, vlight, vline, vt,
                       idx, mattri)
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
                self.output.objplc.append((loc, 0, self.complexity, fname, 1))

        # Add objs to library with one name
        if self.libname and objs:
            self.output.objdat[self.libname]=objs


    def checkmsl(self):
        if self.altmsl:
            self.output.log('Absolute altitude (%sm) for object at [%10.6f, %11.6f] in %s' % (round(self.altmsl,2), self.loc.lat, self.loc.lon, self.comment))
            self.altmsl=False	# Don't report again for this object
            return True
        else:
            return False


    def getvar(self, var):
        if var in self.vars:
            val=self.vars[var]
            return val
        else:
            #self.output.log('Undefined variable 0x%04x' % var)
            return 0


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
        #print "Off %x:" % bgl.tell(),
        (c,)=unpack('<B',bgl.read(1))
        #print "%x" % c
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
                #print "Exclude:",n,s,e,w
                output.exc.append((Point(s,w), Point(n,e)))
        elif c==4:
            # Exception
            bgl.seek(12,1)
        else:
            raise struct.error
