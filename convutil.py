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

from math import sin, cos, tan, asin, acos, atan, atan2, fmod, pi
from os import listdir, mkdir, popen3, stat, unlink
from os.path import basename, curdir, dirname, exists, isdir, join, normpath, splitext
from shutil import copyfile
from struct import pack
from tempfile import gettempdir

version='0.96'
banner="Converted by FS2XPlane %s\n" % version

# MSFS oblate spheroid
diae=12756270	# Equatorial diameter [m]
diap=12734620	# Polar diameter [m]
cire=40075000	# Equatorial circumference [m]
cirp=40007000	# Polar circumference [m]

diaa=12748000	# Average diameter [m]

d2r=pi/180.0
r2d=180.0/pi
twopi=pi+pi

m2f=3.28084	# 1 metre [ft]
NM2m=1852	# 1 international nautical mile [m]

complexities=3

def complexity(fscmplx):
    mapping=[-1,0,0,1,2,2]
    if fscmplx>5:
        return 2
    return mapping[fscmplx]


class FS2XError(Exception):
    def __init__(self, msg):
        self.msg=msg


class Point:
    def __init__(self, lat, lon):
        self.lat=lat
        self.lon=lon

    def biased(self, biasX, biasZ):
        # biases are in m
        # Approximation
        return Point(self.lat+biasZ*360.0/cirp,
                     self.lon+biasX*360.0/(cire*cos(d2r*self.lat)))
    #self.lon+biasX*360.0/(cire*cos(self.lat*2/pi)))

    # From http://www.mathforum.com/library/drmath/view/51711.html
    def distanceto(self, to):
        a1=d2r*self.lat
        b1=d2r*self.lon
        a2=d2r*to.lat
        b2=d2r*to.lon
        return (diaa/2) * acos(cos(a1)*cos(b1)*cos(a2)*cos(b2) +
                               cos(a1)*sin(b1)*cos(a2)*sin(b2) +
                               sin(a1)*sin(a2))

    # From http://www.mathforum.org/library/drmath/view/55417.html
    def headingto(self, to):
        lat1=d2r*self.lat
        lon1=d2r*self.lon
        lat2=d2r*to.lat
        lon2=d2r*to.lon
        return r2d*(atan2(sin(lon2-lon1)*cos(lat2),
                          (cos(lat1)*sin(lat2)-
                           sin(lat1)*cos(lat2)*cos(lon2-lon1))) %
                    twopi)

    def within(self, bl, tr):
        return (self.lat>=bl.lat and self.lat<=tr.lat and
                self.lon>=bl.lon and self.lon<=tr.lon)
    
    def __str__(self):
        return "%s %s" % (self.lat, self.lon)


class Matrix:
    def __init__(self, v=None):
        if v:
            self.m=[]
            # deep copy
            for i in range(4):
                x=[]
                for j in range(4):
                    x.append(v[i][j])
                self.m.append(x)
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

    def rotate(self, x, y, z):
        m=self.m
        return (m[0][0]*x + m[1][0]*y + m[2][0]*z,
                m[0][1]*x + m[1][1]*y + m[2][1]*z,
                m[0][2]*x + m[1][2]*y + m[2][2]*z)

    def heading(self):
        # Derive heading from matrix, assuming no pitch or bank
        #if self.m[1][1]!=1:
        #    raise ValueError
        if self.m[2][0]>=0:
            return r2d*acos(self.m[0][0])
        else:
            return 360-r2d*acos(self.m[0][0])

    def offset(self, x, y, z):
        n=Matrix(self.m)
        n.m[3]=[self.m[3][0]+x, self.m[3][1]+y, self.m[3][2]+z, 1]
        return n
        
    def headed(self, angle):
        # about y axis
        a=d2r*angle
        t=Matrix([[cos(a), 0,-sin(a), 0],
                  [     0, 1,      0, 0],
                  [sin(a), 0, cos(a), 0],
                  [     0, 0,      0, 1]])
        return t*self
          
    def pitched(self, angle):
        # about x axis
        a=d2r*angle
        t=Matrix([[1,      0,      0, 0],
                  [0, cos(a),-sin(a), 0],
                  [0, sin(a), cos(a), 0],
                  [0,      0,      0, 1]])
        return t*self

    def banked(self, angle):
        # about x axis
        a=d2r*angle
        t=Matrix([[cos(a),-sin(a), 0, 0],
                  [sin(a), cos(a), 0, 0],
                  [0,      0,      1, 0],
                  [0,      0,      0, 1]])
        return t*self

    #def __cmp__(self, other):
    #    # For use as a hash key
    #    return cmp(self.m, other.m)

    def __mul__(self, other):
        # self*other
        a=self.m
        b=other.m
        n=Matrix([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]])
        for i in range(4):
            for j in range(4):
                x=0
                for k in range(4):
                    x=x+a[i][k]*b[k][j]
                n.m[i][j]=x
        return n

    def __str__(self):
        s=''
        for i in range(4):
            s=s+' [%8.3f %8.3f %8.3f %8.3f]\n' % (
                self.m[i][0], self.m[i][1], self.m[i][2], self.m[i][3])
        s='['+s[1:-1]+']'
        return s


class AptNav:
    def __init__(self, code, loc, text):
        self.code=code
        self.loc=loc
        self.text=text

    def __repr__(self):
        if self.code==1 or self.code>=50:
            return "\"%-2d %s\"" % (self.code, self.text)
        else:
            return "\"%-2d %10.6f %11.6f %s\"" % (
                self.code, self.loc.lat, self.loc.lat, self.text)

    def __str__(self):
        if self.code==1 or self.code>=50:
            return "%-2d %s" % (self.code, self.text)
        else:
            return "%-2d %10.6f %11.6f %s" % (
                self.code, self.loc.lat, self.loc.lon, self.text)

    def __cmp__(self,other):
        # Hack!
        code=cmp(self.code,other.code)
        if code!=0 or self.code==10:
            return code
        else:
            # Compare on textual info
            return cmp(self.text[6:],other.text[6:])


class Object:
    def __init__(self, filename, comment, tex, vlight, vline, vt, idx,
                 mattri, poly):
        self.filename=filename
        self.comment=comment
        self.tex=tex
        self.vlight=vlight
        self.vline=vline
        self.vt=vt
        self.idx=idx
        self.mattri=mattri	# [((d,s,e), start, count, dblsided)]
        self.poly=poly

    def __eq__(self, o):
        return (self.filename==o.filename and
                self.comment==o.comment and
                self.tex==o.tex and
                self.vlight==o.vlight and
                self.vline==o.vline and
                self.vt==o.vt and
                self.idx==o.idx and
                self.mattri==o.mattri and
                self.poly==o.poly)

    def export(self, scale, output):
        if scale!=1:
            comment="%s scaled x%s" % (self.comment, scale)
            filename="%s_%02d%02d.obj" % (
                self.filename[:-4], int(scale), round(scale*100,0)%100)
        else:
            comment=self.comment
            filename=self.filename
        lit=None

        if self.tex:
            path=join(output.xppath, 'textures')
            if not isdir(path): mkdir(path)
            (dst,ext)=splitext(basename(self.tex.replace(' ','_')))
            if not ext.lower() in ['.bmp', '.png']:
                dst+=ext	# For *.xAF etc
            dst=normpath(join(path, dst+'.png'))
            try:
                # Special handling for trees if no texture supplied
                if not exists(self.tex) and basename(self.tex).upper() in ['TREESWI.BMP', 'TREESSP.BMP', 'TREESSU.BMP', 'TREESFA.BMP', 'TREESHW.BMP']:
                    self.tex='Resources/Tree_side.png'	# X-Plane v8 texture
                    dst=normpath(join(path, basename(self.tex)))
                    if not exists(dst): copyfile(self.tex, dst)
                    mapping=[[(1,0),(0,6),(1,6),(1,4)],
                             [(7,2),(5,7),(3,0),(2,5)],
                             [(7,2),(1,7),(2,6),(5,4)],
                             [(7,2),(6,7),(2,6),(6,4)]]
                    newvt=[]
                    for (x,y,z,nx,ny,nz,u,v) in self.vt:
                        (un,vn)=mapping[min(int(u*4),3)][min(int(v*4),3)]
                        if un==1 and vn==0 and (v*4)%1>=0.125:	# shrub
                            v=v-0.125
                        newvt.append((x,y,z,nx,ny,nz,
                                      (un+(u*4)%1)/8.0, (vn+(v*4)%1)/8.0))
                    self.vt=newvt

                elif dirname(self.tex)=='Resources':
                    # texture is supplied with this program (ie Taxi2.png)
                    copyfile(self.tex, dst)
                    (lit,ext)=splitext(self.tex)
                    lit+='_LIT.png'
                    self.tex=basename(dst)
                    if exists(lit):
                        (dst,foo)=splitext(dst)
                        dst+='_LIT.png'
                        copyfile(lit, dst)
                        lit=basename(dst)
                    else:
                        lit=None
                    
                else:
                    if self.tex in output.haze:
                        palno=output.haze[self.tex]
                    else:
                        palno=None
                    self.maketex(self.tex, dst, output, palno)
                    (lit,ext)=splitext(self.tex)
                    lit+='_LM.BMP'
                    self.tex=basename(dst)
                    if exists(lit):
                        (dst,foo)=splitext(dst)
                        dst+='_LM.png'
                        self.maketex(lit, dst, output, palno)
                        lit=basename(dst)
                    else:
                        lit=None

            except IOError:
                output.dufftex[dst]=True
                output.log("Can't create texture %s from %s" % (
                    basename(dst), basename(self.tex)))
                lit=None

        if 0: #output.debug:	# XXX
            # Generate line at object origin
            self.vline.insert(0, (0, 0, 0,  1, 0.5, 0.5))
            self.vline.insert(1, (0, 25, 0, 1, 0.5, 0.5))
            self.idx.insert(0,0)
            self.idx.insert(1,1)
            for i in range(len(self.mattri)):
                (m, start, count, dbl)=self.mattri[i]
                self.mattri[i]=(m, start+2, count, dbl)
        
        try:
            path=join(output.xppath, 'objects')
            objpath=join(path, filename)
            if not isdir(path): mkdir(path)
            objfile=file(objpath, 'wt')
            if not filename in listdir(path):
                raise IOError
            objfile.write("I\n800\t# %sOBJ\n" % banner)
            objfile.write("\n# %s\n\n" % comment)
            if self.tex:
                objfile.write("TEXTURE\t\t../textures/%s\n" % basename(self.tex))
                if lit:
                    objfile.write("TEXTURE_LIT\t../textures/%s\n" % basename(lit))
            else:
                objfile.write("TEXTURE\t\n")
    
            objfile.write("POINT_COUNTS\t%d %d %d %d\n\n" % (
                len(self.vt), len(self.vline), len(self.vlight),
                len(self.idx)))
            
            for (x,y,z,r,g,b) in self.vlight:
                objfile.write("VLIGHT\t%8.3f %8.3f %8.3f\t%6.3f %6.3f %6.3f\n" % (x*scale, y*scale, z*scale, r, g, b))
            if self.vlight: objfile.write("\n")
            
            for (x,y,z,r,g,b) in self.vline:
                objfile.write("VLINE\t%8.3f %8.3f %8.3f\t%6.3f %6.3f %6.3f\n" % (x*scale, y*scale, z*scale, r, g, b))
            if self.vline: objfile.write("\n")

            for (x,y,z,nx,ny,nz,u,v) in self.vt:
                #if self.poly: y=0	# Adjust for bogus layering attempts
                objfile.write("VT\t%8.3f %8.3f %8.3f\t%6.3f %6.3f %6.3f\t%6.3f %6.3f\n" % (x*scale, y*scale, z*scale, nx,ny,nz, u,v))
            if self.vt: objfile.write("\n")

            n=len(self.idx)
            for i in range(0, n-9, 10):
                objfile.write("IDX10\t")
                for j in range(i, i+9):
                    objfile.write("%d " % self.idx[j])
                objfile.write("%d\n" % self.idx[i+9])
            for j in range(n-(n%10), n):
                objfile.write("IDX\t%d\n" % self.idx[j])
            if self.idx: objfile.write("\n")

            if self.vlight:
                if len(self.vlight)==1 and not self.vline and not self.vt:
                    # X-Plane 8.30 optimises single lights away otherwise
                    objfile.write("ATTR_LOD\t0 16000\n")
                objfile.write("LIGHTS\t0 %d\n\n" % len(self.vlight))
            if self.vline:
                objfile.write("LINES\t0 %d\n\n" % len(self.vline))

            # Maybe a decal
            if self.poly:
                objfile.write("ATTR_poly_os %d\n" % self.poly)
                if self.poly==1 and len(self.vt)==4:
                    objfile.write("ATTR_hard\n")	# Hack!
            else:
                objfile.write("ATTR_no_blend\n")

            a=(1.0,1.0,1.0)
            s=(0.0,0.0,0.0)
            e=(0.0,0.0,0.0)
            d=False
            for (m, start, count, dbl) in self.mattri:
                if dbl and not d:
                    objfile.write("ATTR_no_cull\n")
                elif d and not dbl:
                    objfile.write("ATTR_cull\n")
                d=dbl
                (ar,ag,ab)=m[0]
                (sr,sg,sb)=m[1]
                (er,eg,eb)=m[2]
                if a!=(ar,ag,ab) or s!=(sr,sg,sb) or e!=(er,eg,eb):
                    objfile.write("\n")
                if a!=(ar,ag,ab):
                    a=(ar,ag,ab)
                    objfile.write("ATTR_ambient_rgb\t%5.3f %5.3f %5.3f\n" % (
                        ar,ag,ab))
                if s!=(sr,sg,sb):
                    s=(sr,sg,sb)
                    objfile.write("ATTR_specular_rgb\t%5.3f %5.3f %5.3f\n" % (
                        sr,sg,sb))
                if e!=(er,eg,eb):
                    e=(er,eg,eb)
                    objfile.write("ATTR_emission_rgb\t%5.3f %5.3f %5.3f\n" % (
                        er,eg,eb))
                objfile.write("TRIS\t%d %d\n" % (start, count))
    
            objfile.close()
        except IOError:
            raise FS2XError("Can't write \"%s\"" % objpath)
        
    def maketex(self, src, dst, output, palno):
        if exists(dst) or dst in output.dufftex:
            return	# assume it's already been converted
        # Extension is ignored by MSFS?
        #(s,e)=splitext(src)
        #for ext in [e, '.bmp', '.r8']:
        #    if exists(s+ext):
        #        src=s+ext
        #        break
        if not exists(src):
            output.log("Texture %s not found" % basename(src))
            raise IOError

        # If size=65536 assume RAW and add standard BMP header
        # What about compressed RAW?
        (s,e)=splitext(src)
        tmp=join(gettempdir(), basename(s)+'.bmp')
        if stat(src).st_size==65536:
            f=file(src, 'rb')
            t=file(tmp, 'wb')
            for x in rawbmphdr:
                t.write(pack('<H',x))
            t.write(f.read())
            t.close()
            f.close()
        else:
            copyfile(src, tmp)

        if palno:
            x=helper('%s -xbrqep%d -o "%s" "%s"' % (
                output.pngexe, palno-1, dst, tmp))
        else:
            x=helper('%s -xbrqe -o "%s" "%s"' % (
                output.pngexe, dst, tmp))
        if not exists(dst):
            output.log("Can't convert texture %s (%s)" % (basename(src), x))
            raise IOError


# Run helper app and return stderr
def helper(cmds):
    (i,o,e)=popen3(cmds)
    i.close()
    o.read()
    txt=e.read()
    o.close()
    e.close()
    return txt.strip().replace('\n', ', ')


# Standard BMP header & palette for RAW data
rawbmphdr=[
    0x4d42, 0x0000, 0x0000, 0x0000, 0x0000, 0x0436, 0x0000, 0x0028,
    0x0000, 0x0100, 0x0000, 0x0100, 0x0000, 0x0001, 0x0008, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0001, 0x0000, 0x0001, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0808, 0x0008, 0x1010,
    0x0010, 0x1818, 0x0018, 0x2020, 0x0020, 0x2828, 0x0028, 0x3030,
    0x0030, 0x3838, 0x0038, 0x4141, 0x0041, 0x4949, 0x0049, 0x5151,
    0x0051, 0x5959, 0x0059, 0x6161, 0x0061, 0x6969, 0x0069, 0x7171,
    0x0071, 0x7979, 0x0079, 0x8282, 0x0082, 0x8a8a, 0x008a, 0x9292,
    0x0092, 0x9a9a, 0x009a, 0xa2a2, 0x00a2, 0xaaaa, 0x00aa, 0xb2b2,
    0x00b2, 0xbaba, 0x00ba, 0xc3c3, 0x00c3, 0xcbcb, 0x00cb, 0xd3d3,
    0x00d3, 0xdbdb, 0x00db, 0xe3e3, 0x00e3, 0xebeb, 0x00eb, 0xf7f7,
    0x00f7, 0xffff, 0x00ff, 0x0505, 0x0015, 0x0a0a, 0x002a, 0x0f0f,
    0x003f, 0x1414, 0x0054, 0x1919, 0x0069, 0x1e1e, 0x007e, 0x2323,
    0x0093, 0x2828, 0x00a8, 0x2d2d, 0x00bd, 0x3232, 0x00d2, 0x3737,
    0x00e7, 0x3c3c, 0x00fc, 0x1505, 0x0005, 0x2a0a, 0x000a, 0x3f0f,
    0x000f, 0x5414, 0x0014, 0x6919, 0x0019, 0x7e1e, 0x001e, 0x9323,
    0x0023, 0xa828, 0x0028, 0xbd2d, 0x002d, 0xd232, 0x0032, 0xe737,
    0x0037, 0xfc3c, 0x003c, 0x0717, 0x0000, 0x0f28, 0x0000, 0x173a,
    0x0000, 0x2854, 0x0000, 0x4068, 0x0000, 0x477a, 0x0000, 0x578f,
    0x0000, 0x639c, 0x0000, 0x70b3, 0x0000, 0x80c7, 0x0000, 0x8fd7,
    0x0000, 0x99e6, 0x0000, 0x0e00, 0x001c, 0x1c00, 0x0038, 0x2a00,
    0x0054, 0x3800, 0x0070, 0x4600, 0x008c, 0x5400, 0x00a8, 0x6200,
    0x00c4, 0x7000, 0x00e0, 0x7e00, 0x00fc, 0x1c00, 0x001c, 0x3800,
    0x0038, 0x5400, 0x0054, 0x7000, 0x0070, 0x8c00, 0x008c, 0xa800,
    0x00a8, 0xc400, 0x00c4, 0xe000, 0x00e0, 0xfc00, 0x00fc, 0x1510,
    0x0019, 0x2a20, 0x0032, 0x3f30, 0x004b, 0x5440, 0x0064, 0x6950,
    0x007d, 0x7e60, 0x0096, 0x9370, 0x00af, 0xa880, 0x00c8, 0xbd90,
    0x00e1, 0x0b07, 0x001c, 0x160e, 0x0038, 0x2115, 0x0054, 0x2c1c,
    0x0070, 0x3723, 0x008c, 0x422a, 0x00a8, 0x4d31, 0x00c4, 0x5838,
    0x00e0, 0x633f, 0x00fc, 0x1609, 0x0011, 0x2c12, 0x0022, 0x421b,
    0x0033, 0x5824, 0x0044, 0x6e2d, 0x0055, 0x8436, 0x0066, 0x9a3f,
    0x0077, 0xb048, 0x0088, 0xc651, 0x0099, 0x3a68, 0x0000, 0x5770,
    0x0000, 0x7080, 0x002b, 0x0000, 0x00ff, 0xff40, 0x0040, 0x00c0,
    0x0000, 0x6969, 0x0000, 0x8000, 0x00ff, 0xff00, 0x00ff, 0x5151,
    0x0051, 0x7979, 0x0079, 0x9292, 0x0092, 0xaaaa, 0x00aa, 0xc3c3,
    0x00c3, 0xe3e3, 0x00e3, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0xc0ff, 0x00c0, 0xc8ff, 0x00c8, 0xd0ff,
    0x00d0, 0xd8ff, 0x00d8, 0xe0ff, 0x00e0, 0xe8ff, 0x00e8, 0xf0ff,
    0x00f0, 0xf8ff, 0x00f8, 0xffff, 0x00ff, 0xffff, 0x00ff, 0xffff,
    0x00ff, 0xffff, 0x00ff, 0xffff, 0x00ff, 0xffff, 0x00ff, 0xffff,
    0x00ff, 0xffff, 0x00ff, 0x4810, 0x0010, 0x5020, 0x0020, 0x5830,
    0x0030, 0x6040, 0x0040, 0x6850, 0x0050, 0x7060, 0x0060, 0x7870,
    0x0070, 0x7c78, 0x0078, 0x8080, 0x0080, 0x8080, 0x0080, 0x8080,
    0x0080, 0x8080, 0x0080, 0x8080, 0x0080, 0x8080, 0x0080, 0x8080,
    0x0080, 0x8080, 0x0080, 0x8cbd, 0x0021, 0x84a5, 0x0039, 0x4242,
    0x00bd, 0x4242, 0x009c, 0x4a4a, 0x0084, 0x526b, 0x0021, 0x5a52,
    0x00d6, 0x5a52, 0x00bd, 0x5a52, 0x00a5, 0x3931, 0x007b, 0x3931,
    0x0063, 0x4a42, 0x006b, 0x5a52, 0x007b, 0x5a42, 0x00b5, 0x3129,
    0x004a, 0x735a, 0x00bd, 0x5a31, 0x008c, 0x314a, 0x0021, 0x7331,
    0x00b5, 0x4221, 0x0063, 0x7342, 0x00a5, 0x2921, 0x0031, 0x8c73,
    0x00a5, 0xa58c, 0x00bd, 0x637b, 0x0039, 0x6b18, 0x00b5, 0x7b21,
    0x00ce, 0x6321, 0x009c, 0x6b31, 0x0094, 0x5231, 0x006b, 0x2139,
    0x0021, 0x73a5, 0x0021, 0xd621, 0x00d6, 0xad21, 0x00ad, 0xc629,
    0x00c6, 0x8c21, 0x008c, 0x7321, 0x0073, 0xbd39, 0x00bd, 0x9c31,
    0x009c, 0xad39, 0x00ad, 0x7b31, 0x007b, 0x7b42, 0x007b, 0x4a31,
    0x004a, 0x7b5a, 0x007b, 0x2921, 0x0029, 0x6339, 0x005a, 0x734a,
    0x006b, 0x9452, 0x007b, 0xad63, 0x008c, 0x9c63, 0x0084, 0x4229,
    0x0031, 0xa55a, 0x0063, 0xd64a, 0x004a, 0x8c39, 0x0039, 0xb54a,
    0x004a, 0xc65a, 0x005a, 0x7b39, 0x0039, 0x6331, 0x0031, 0xa55a,
    0x005a, 0x9452, 0x0052, 0x634a, 0x004a, 0x7384, 0x0039, 0x637b,
    0x0021, 0x7384, 0x004a]
