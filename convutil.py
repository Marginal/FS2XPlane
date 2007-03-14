from math import sin, cos, tan, asin, acos, atan, atan2, fmod, pi
from os import listdir, mkdir, popen3, stat, unlink
from os.path import basename, curdir, dirname, exists, isdir, join, normpath, splitext
from shutil import copyfile
from struct import pack
from tempfile import gettempdir

version='0.95'
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
    def __init__(self, filename, comment, tex, vlight, vline, vt, idx, mattri):
        self.filename=filename
        self.comment=comment
        self.tex=tex
        self.vlight=vlight
        self.vline=vline
        self.vt=vt
        self.idx=idx
        self.mattri=mattri	# [((d,s,e), start, count, dblsided)]
        self.poly=0

        # Maybe a decal
        if self.vt:
            mins=0
            maxs=0
            for (x,y,z,nx,ny,nz,u,v) in self.vt:
                if y>=0.101:	# Arbitrary. 0.1 used in VF London
                    break
                mins=min(mins,x,z)
                maxs=max(maxs,x,z)
            else:
                if (maxs-mins)>NM2m/4:	# arbitrary
                    self.poly=1
                else:                        
                    self.poly=2


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
            (dst,ext)=splitext(basename(self.tex))
            if ext[1].isdigit(): dst+=ext	# For *.xAF
            dst=normpath(join(path, dst.replace(' ','_')+'.png'))
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
            output.fatal("Can't write \"%s\"" % objpath)
        
    def maketex(self, src, dst, output, palno):
        if exists(dst) or dst in output.dufftex:
            return	# assume it's already been converted
        (s,e)=splitext(src)
        # Extension is ignored by MSFS?
        for ext in [e, '.bmp', '.r8']:
            if exists(s+ext):
                src=s+ext
                break
        else:
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
        elif 0: #stat(src).st_size==66614 and not palno:
            # Appears that standard bitmaps have 0-based transparency?
            palno=1
            copyfile(src, tmp)
        else:
            copyfile(src, tmp)

        if palno:
            x=helper('%s -xbrqep%d -o "%s" "%s"' % (
                output.pngexe, palno-1, dst, tmp))
        else:
            x=helper('%s -xbrqe -o "%s" "%s"' % (output.pngexe, dst, tmp))
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


# Standard BMP header for RAW data
rawbmphdr=[
    0x4d42, 0x0000, 0x0000, 0x0000, 0x0000, 0x0436, 0x0000, 0x0028,
    0x0000, 0x0100, 0x0000, 0x0100, 0x0000, 0x0001, 0x0008, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0001, 0x0000, 0x0001, 0x0000, 0x0000,
    0x0000, 0x0000, 0x0000, 0x0000, 0x0000, 0x2121, 0x0018, 0x2121,
    0x0021, 0x3129, 0x0029, 0x2929, 0x0031, 0x3129, 0x0031, 0x2931,
    0x0029, 0x3131, 0x0029, 0x2931, 0x0031, 0x1039, 0x0000, 0x1842,
    0x0008, 0x2142, 0x0008, 0x2142, 0x0010, 0x3142, 0x0010, 0x424a,
    0x0010, 0x314a, 0x0021, 0x0084, 0x0000, 0x0084, 0x0008, 0x0884,
    0x0008, 0x1084, 0x0010, 0x108c, 0x0010, 0x108c, 0x0018, 0x188c,
    0x0018, 0x2190, 0x0021, 0x2194, 0x0029, 0x2952, 0x0000, 0x2994,
    0x0029, 0x2994, 0x0031, 0x3152, 0x0021, 0x396b, 0x0000, 0x426b,
    0x0000, 0x526b, 0x0021, 0x3131, 0x0031, 0x3942, 0x0039, 0x4239,
    0x0039, 0x2931, 0x0042, 0x3129, 0x0042, 0x3931, 0x0042, 0x3942,
    0x0042, 0x4239, 0x0042, 0x4221, 0x004a, 0x4a4a, 0x004a, 0x524a,
    0x004a, 0x4242, 0x0052, 0x312d, 0x005a, 0x3931, 0x0063, 0x422d,
    0x0067, 0x4239, 0x00a5, 0x524a, 0x005a, 0x524a, 0x0063, 0x4252,
    0x0039, 0x5252, 0x004a, 0x4a52, 0x0052, 0x5252, 0x0052, 0x4a5a,
    0x0042, 0x4a63, 0x0039, 0x4a63, 0x0042, 0x5263, 0x004a, 0x5273,
    0x004a, 0x3194, 0x0031, 0x3396, 0x0039, 0x3d9c, 0x003d, 0x469c,
    0x004a, 0x4aa5, 0x004a, 0x6653, 0x003c, 0x5a5a, 0x0063, 0x5e56,
    0x0063, 0x635a, 0x0063, 0x6363, 0x0063, 0x6363, 0x006b, 0x6b63,
    0x006b, 0x735a, 0x0073, 0x6070, 0x0057, 0x6b6b, 0x006b, 0x6f67,
    0x006f, 0x706d, 0x0070, 0x677b, 0x004e, 0x6f73, 0x0073, 0x5da4,
    0x0059, 0x7197, 0x006f, 0x6b4a, 0x007b, 0x716a, 0x008a, 0x7b7b,
    0x007b, 0x847b, 0x007b, 0x7b7b, 0x0084, 0x847b, 0x0084, 0x7b84,
    0x007b, 0x7b84, 0x0084, 0x8484, 0x0084, 0x7b8c, 0x007b, 0x7bad,
    0x007b, 0x7bad, 0x0084, 0x73b5, 0x007b, 0x7bb5, 0x007b, 0x7bb5,
    0x0084, 0x7bbd, 0x0084, 0xb85f, 0x0029, 0xc38e, 0x0070, 0x8c8c,
    0x0084, 0x84ac, 0x0081, 0x8484, 0x008c, 0x8c94, 0x0084, 0x949c,
    0x0084, 0x84b9, 0x008c, 0x8c84, 0x008c, 0x8c84, 0x0094, 0x8c8c,
    0x008c, 0x9494, 0x008c, 0x949c, 0x008c, 0x94a5, 0x008c, 0x8cb9,
    0x008c, 0x8cc6, 0x008c, 0x8c8c, 0x0094, 0x8c94, 0x0094, 0x9494,
    0x0094, 0x9494, 0x009c, 0x8cbd, 0x0094, 0x8cc6, 0x0094, 0x94bd,
    0x0094, 0x94c1, 0x0098, 0x9c8c, 0x009c, 0x9c94, 0x009c, 0x9c9c,
    0x0094, 0x98b1, 0x009c, 0xa09c, 0x00a5, 0x9cb7, 0x009e, 0xa5ad,
    0x009c, 0xd3b2, 0x0099, 0x7b08, 0x00c6, 0x9c10, 0x00c6, 0x2929,
    0x00ad, 0x2929, 0x00bd, 0x3939, 0x00ce, 0x4239, 0x00ce, 0x4239,
    0x00e7, 0x5242, 0x00b5, 0x3942, 0x00bd, 0x4a42, 0x00bd, 0x3942,
    0x00ce, 0x4242, 0x00ef, 0x4a4a, 0x00ce, 0x6352, 0x00ce, 0x735a,
    0x00bd, 0x5a6b, 0x00c6, 0x7377, 0x00d6, 0x8883, 0x00d2, 0xa5a5,
    0x00a5, 0xa998, 0x00b1, 0x636b, 0x00e7, 0x837f, 0x00e7, 0x948c,
    0x00e7, 0xa594, 0x00ef, 0xa5a5, 0x00ad, 0xadad, 0x00ad, 0xadb5,
    0x00a5, 0xa5c6, 0x00a9, 0xadad, 0x00b5, 0x94ad, 0x00de, 0xa0a9,
    0x00e2, 0xadad, 0x00e7, 0xb529, 0x00ef, 0xc539, 0x00ef, 0xd66b,
    0x00ef, 0xbd94, 0x00e7, 0xb5ad, 0x00ad, 0xb5ad, 0x00b5, 0xb5ad,
    0x00c6, 0xb5ad, 0x00de, 0xadb5, 0x00b5, 0xb5b5, 0x00b5, 0xb5b5,
    0x00bd, 0xbdb5, 0x00bd, 0xceb5, 0x00ef, 0xefbd, 0x00a5, 0xb5bd,
    0x00ad, 0xb5bd, 0x00b5, 0xbdbd, 0x00b5, 0xbdbd, 0x00bd, 0xbdbd,
    0x00c6, 0xc6bd, 0x00c6, 0xc6bd, 0x00d6, 0xadc6, 0x00a5, 0xadc6,
    0x00ad, 0xbdc6, 0x00b5, 0xbdc6, 0x00bd, 0xc6c6, 0x00bd, 0xbdc6,
    0x00c6, 0xc6c6, 0x00c6, 0xc6c6, 0x00ce, 0xcec6, 0x00ce, 0xcec6,
    0x00d6, 0xbdc6, 0x00ef, 0xa5ce, 0x00ad, 0xadce, 0x00ad, 0xadce,
    0x00b5, 0xb5ce, 0x00b5, 0xb5ce, 0x00bd, 0xbdd2, 0x00bd, 0xbdce,
    0x00c6, 0xbdd6, 0x00c6, 0xc6ce, 0x00bd, 0xc6ce, 0x00c6, 0xc6ce,
    0x00ce, 0xc6d6, 0x00c6, 0xc6d6, 0x00ce, 0xcece, 0x00c6, 0xcece,
    0x00ce, 0xced6, 0x00c6, 0xced6, 0x00ce, 0xcede, 0x00ce, 0xd6d6,
    0x00ce, 0xd6de, 0x00ce, 0xcece, 0x00d6, 0xced6, 0x00d6, 0xcede,
    0x00d6, 0xd6ce, 0x00d6, 0xd6d6, 0x00d6, 0xd6de, 0x00d6, 0xdede,
    0x00d6, 0xd6d6, 0x00de, 0xd6de, 0x00de, 0xded6, 0x00de, 0xdede,
    0x00de, 0xded6, 0x00e7, 0xdede, 0x00e7, 0xdee7, 0x00de, 0xdee7,
    0x00e7, 0xe7ce, 0x00ef, 0xe7ce, 0x00f7, 0xe7de, 0x00de, 0xe7de,
    0x00e7, 0xe7de, 0x00ef, 0xe7de, 0x00f7, 0xe7e7, 0x00de, 0xe7e7,
    0x00e7, 0xe7e7, 0x00ef, 0xe7e7, 0x00f7, 0xe7ef, 0x00e7, 0xefe7,
    0x00ef, 0xefe7, 0x00f7, 0xefef, 0x00e7, 0xefef, 0x00ef, 0xefef,
    0x00f7, 0xeff7, 0x00ef, 0xeff7, 0x00f7, 0xf7ef, 0x00ef, 0xf7ef,
    0x00f7, 0xf7f7, 0x00ef, 0xf7f7, 0x00f7, 0xffc6, 0x00ff, 0xffef,
    0x00e7, 0xffef, 0x00ef, 0xfff7, 0x00f7, 0xfff7, 0x00ff, 0xffff,
    0x00f7, 0xffff, 0x00ff]
