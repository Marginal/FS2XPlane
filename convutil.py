from math import sin, cos, tan, asin, acos, atan, atan2, fmod, pi, degrees, radians, sqrt
from locale import getpreferredencoding
import os	# for startfile
from os import listdir, mkdir, popen3, stat, unlink
from os.path import abspath, basename, curdir, dirname, exists, isdir, join, normpath, splitext
from shutil import copy2
from struct import pack
from sys import maxint, platform
from tempfile import gettempdir
import types
import unicodedata

if not 'startfile' in dir(os):
    # Causes problems under py2exe & not needed
    from urllib import quote
    import webbrowser

from version import appname, appversion

banner="Converted by %s %4.2f\n" % (appname, appversion)

# MSFS oblate spheroid
diae=12756270	# Equatorial diameter [m]
diap=12734620	# Polar diameter [m]
cire=40075000	# Equatorial circumference [m]
cirp=40007000	# Polar circumference [m]

diaa=12748000	# Average diameter [m]	= 12756000 in X-Plane

twopi=pi+pi

m2f=3.28084	# 1 metre [ft]
NM2m=1852	# 1 international nautical mile [m]

groundfudge=0.22	# arbitrary: 0.124 used in UNNT, 0.172 in KBOS, 2.19 in LIRP
planarfudge=0.1	# arbitrary

complexities=3		# We map to X-plane complexity 1-3 (defauilt, a lot, tons)

apronlightspacing=60.96	# [m] = 200ft
taxilightspacing=30.48	# [m] = 100ft

# for asciify
# find corresponing Windows code page for the user's locale
encoding=getpreferredencoding().lower()
#if encoding=='us-ascii': encoding='latin1'	# 2.3 on Mac
if   encoding in ['cp1250', 'mac_latin2', 'iso8859_2', 'iso8859_16']:
    # Central European
    asciitbl='[|]-_E ,f_.||^%S<STZZ \'\'"".--- s>stzz   LxA|S"cS<--rZd+ l\'uP. as>L"lzRAAAALCCCEEEEIIDDNNOOOO*RUUUUYTsraaaalccceeeeiiddnnoooo/ruuuuyty'
elif encoding in ['cp1251', 'mac_cyrillic', 'iso8859_5', 'koi8_r', 'koi8_u']:
    # Cyrillic
    asciitbl='[|]-_DG,g_.||E%L<_KH_d\'\'"".--- l>_kh_ YyJxG|SEcE<--rId+IiguP.eNe>jSsiABWGDEVJIIKLMNOPRSTUFHC_S_XYXE_Qabwgdevjiiklmnoprstufhc_s_xyxe_q'
elif encoding in ['cp1253', 'mac_greek', 'iso8859_7']:
    # Greek
    asciitbl='[|]-_E ,f_.||^%S<O Z  \'\'"".--- s>o zY "ALxY|S"ca<--r-d+23\'uP.EHI>O_YOiABGDEZHOIKLMNXOPRSSTYFX_OIYaehiuabgdezhoiklmnxoprsstufx_oiuouoy'
elif encoding in ['cp1254', 'mac_turkish', 'iso8859_3', 'iso8859_9']:
    # Turkish / Latin-5
    asciitbl='[|]-_E ,f_.||^%S<O Z  \'\'"".--- s>o zY !cLxY|S"ca<--r d+23\'uP. 10>___?AAAAAAACEEEEIIIIGNOOOOO*OUUUUISsaaaaaaaceeeeiiiignooooo/ouuuuisy'
elif encoding in ['cp1257', 'mac_iceland', 'iso8859_4', 'iso8859_10', 'iso8859_13']:
    # Baltic
    asciitbl='[|]-_E ,f_.||^%S<O"   \'\'"".--- s>o  Y !cLxY|SOcR<- rAd+23\'uP.o1r>___aAIACAAEECEZEGKILSNNOOOO*ULSUUZZsaiacaaeecezegkilsnnoooo/ulsuuzz '
else:	       # ['cp1252', 'mac_roman', 'latin1', 'iso8859_1', 'iso8859_15']:
    # Can't do anything with other encodings (incl CJK), so just use latin1
    # Western / Latin-1
    asciitbl='[|]-_E ,f_.||^%S<O Z  \'\'"".--- s>o zY !cLxY|S"ca<--r d+23\'uP. 10>___?AAAAAAACEEEEIIIIDNOOOOO*OUUUUYPsaaaaaaaceeeeiiiidnooooo/ouuuuypy'


# smoke effects
effects={'cntrl_bldstm':	('smoke_white', 2.5),	# avg of next 3
         'fx_bldstm_sml':	('smoke_white', 1.5),
         'fx_bldstm_med':	('smoke_white', 2.0),
         'fx_bldstm_lrg':	('smoke_white', 3.5),
         'cntrl_smokestack':	('smoke_black', 3.5),	# avg of next 2
         'fx_smokestack':	('smoke_black', 3.5),
         'fx_smokestack2':	('smoke_black', 3.5),
         'fx_smkpuff_s':	('smoke_black', 2.0),
         'fx_smkpuff_m':	('smoke_black', 3.0),
         'fx_smoke_w':		('smoke_white', 1.5),
         'fx_steam1':		('smoke_white', 3.0),
         'fx_steam2':		('smoke_white', 3.0),}

# member var is defined
def D(c, v):
    return getattr(c,v,None)

# member var is defined and true
def T(c, v):
    return getattr(c,v,None) in ['TRUE','YES']

# member var is defined and equal
def E(c, v, e):
    return getattr(c,v,None)==e

# 2.3 version of case-insensitive sort
# 2.4-only version is faster: sort(cmp=lambda x,y: cmp(x.lower(), y.lower()))
def sortfolded(seq):
    seq.sort(lambda x,y: cmp(x.lower(), y.lower()))

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

    def __str__(self):
        return '%12.8f %13.8f' % (self.lat, self.lon)

    def biased(self, biasX, biasZ):
        # Biases are in m. Z is North. Approximation.
        return Point(self.lat+biasZ*360.0/cirp,
                     self.lon+biasX*360.0/(cire*cos(radians(self.lat))))

    # From http://www.mathforum.com/library/drmath/view/51711.html
    def distanceto(self, to):
        a1=radians(self.lat)
        b1=radians(self.lon)
        a2=radians(to.lat)
        b2=radians(to.lon)
        if a1==a2 and b1==b2: return 0
        x=(cos(a1)*cos(b1)*cos(a2)*cos(b2) +
           cos(a1)*sin(b1)*cos(a2)*sin(b2) +
           sin(a1)*sin(a2))
        if x>=1: return 0
        return (diaa/2) * acos(x)

    # From http://www.mathforum.org/library/drmath/view/55417.html
    def headingto(self, to):
        lat1=radians(self.lat)
        lon1=radians(self.lon)
        lat2=radians(to.lat)
        lon2=radians(to.lon)
        return degrees(atan2(sin(lon2-lon1)*cos(lat2),
                             (cos(lat1)*sin(lat2)-
                              sin(lat1)*cos(lat2)*cos(lon2-lon1))) %
                       twopi)

    # like headingto but just on 2D plane - result in radians
    def angleto(self, to):
        return atan2(to.lon-self.lon, to.lat-self.lat)

    def within(self, bl, tr):
        return (self.lat>=bl.lat and self.lat<=tr.lat and
                self.lon>=bl.lon and self.lon<=tr.lon)
    
    def __str__(self):
        return "%12.8f %13.8f" % (self.lat, self.lon)

    def __add__(self, other):
        return Point(self.lat+other.lat, self.lon+other.lon)

    def __sub__(self, other):
        return Point(self.lat-other.lat, self.lon-other.lon)

    def __mul__(self, m):
        #if not type(m) in int, float: return NotImplemented
        return Point(self.lat*m, self.lon*m)

    def __div__(self, m):
        return Point(self.lat/m, self.lon/m)

    def __eq__(self, other, precision=6):
        return round(self.lat,precision)==round(other.lat,precision) and round(self.lon,precision)==round(other.lon,precision)

    def __hash__(self):
        return hash((self.lat, self.lon))

    def round(self, precision=6):
        self.lat=round(self.lat,precision)
        self.lon=round(self.lon,precision)
        return self


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

    def rotateAndNormalize(self, x, y, z):
        m=self.m
        x1=m[0][0]*x + m[1][0]*y + m[2][0]*z
        y1=m[0][1]*x + m[1][1]*y + m[2][1]*z
        z1=m[0][2]*x + m[1][2]*y + m[2][2]*z
        if x1==y1==z1==0:
            return (0, 0, 0)
        else:
            hyp=1/sqrt(x1*x1 + y1*y1 + z1*z1)
            return (x1*hyp, y1*hyp, z1*hyp)


    # Matrix adjoint/adjugate for obtaining normals - see
    # http://www.worldserver.com/turk/computergraphics/NormalTransformations.pdf
    # Note that vectors produced using this matrix will need renormalizing
    def adjoint(self):
        m=self.m
        return Matrix([[m[1][1]*m[2][2] - m[1][2]*m[2][1],
                        m[1][2]*m[2][0] - m[1][0]*m[2][2],
                        m[1][0]*m[2][1] - m[1][1]*m[2][0], 0],
                       [m[2][1]*m[0][2] - m[2][2]*m[0][1],
                        m[2][2]*m[0][0] - m[2][0]*m[0][2],
                        m[2][0]*m[0][1] - m[2][1]*m[0][0], 0],
                       [m[0][1]*m[1][2] - m[0][2]*m[1][1],
                        m[0][2]*m[1][0] - m[0][0]*m[1][2],
                        m[0][0]*m[1][1] - m[0][1]*m[1][0], 0],
                       [0,0,0,1]])

    def heading(self):
        # Derive heading from matrix, assuming no pitch or bank
        h=round(self.m[0][0]/self.m[1][1], 3)	# arbitrary - handle rounding errors
        try:
            if self.m[2][0]>=0:
                return degrees(acos(h))
            else:
                return 360-degrees(acos(h))
        except:	# wtf?
            return 0

    def scale(self):
        # Assumes no pitch or bank
        return self.m[1][1]

    def offset(self, x, y, z):
        n=Matrix(self.m)
        n.m[3]=[self.m[3][0]+x, self.m[3][1]+y, self.m[3][2]+z, 1]
        return n
        
    def headed(self, angle):
        # about y axis
        a=radians(angle)
        t=Matrix([[cos(a), 0,-sin(a), 0],
                  [     0, 1,      0, 0],
                  [sin(a), 0, cos(a), 0],
                  [     0, 0,      0, 1]])
        return t*self
          
    def pitched(self, angle):
        # about x axis
        a=radians(angle)
        t=Matrix([[1,      0,      0, 0],
                  [0, cos(a),-sin(a), 0],
                  [0, sin(a), cos(a), 0],
                  [0,      0,      0, 1]])
        return t*self

    def banked(self, angle):
        # about x axis
        a=radians(angle)
        t=Matrix([[cos(a),-sin(a), 0, 0],
                  [sin(a), cos(a), 0, 0],
                  [0,      0,      1, 0],
                  [0,      0,      0, 1]])
        return t*self

    def __cmp__(self, o):
        return cmp(self.m, o.m)

    def __hash__(self):
        return hash(tuple([tuple(r) for r in self.m]))

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
            s=s+' [%8.3f %8.3f %8.3f %8.3f]\n' % (self.m[i][0], self.m[i][1], self.m[i][2], self.m[i][3])
        s='['+s[1:-1]+']'
        return s


class AptNav:
    def __init__(self, code, text):
        self.code=code
        self.text=text

    def __repr__(self):
        return '"%-4d %s"' % (self.code, self.text)

    def __str__(self):
        return "%-4d %s" % (self.code, self.text)

    def __cmp__(self, other):
        # Just sort on code
        return self.code-other.code
        #if c:
        #    return c
        #elif self.text > other.text:
        #    return 1
        #elif self.text < other.text:
        #    return -1
        #else:
        #    return 0


# MDLX-style material with texture split out (since it can be specified separately under MDL9)
# http://www.fsdeveloper.com/wiki/index.php?title=MDL_file_format_(FSX)
class Material:

    FSX_MAT_SPECULAR=0x1
    FSX_MAT_HAS_DIFFUSE=0x2
    FSX_MAT_HAS_NORMAL=0x4
    FSX_MAT_HAS_SPECULAR=0x8
    FSX_MAT_HAS_REFLECTION=0x20
    FSX_MAT_HAS_EMISSIVE=0x80
    FSX_MAT_NO_SHADOW=0x200000
    FSX_MAT_ZTEST_ALPHA=0x400000
    FSX_MAT_ALPHA_TEST_GREATER=5
    FSX_MAT_ALPHA_TEST_GREATER_EQUAL=7
    FSX_MAT_DOUBLE_SIDED=0x8

    def __init__(self, xpver, diffuse, specular=None, poly=False, dblsided=False, alphacutoff=None, shiny=False, shadow=True):
        self.d=diffuse		# diffuse color
        self.s=xpver>10 and specular or None	# specular color or None if default. <=v10 has no support for specular color - http://xplanescenery.blogspot.co.uk/2006/01/obj8-what-not-to-use.html
        self.poly=poly		# poly_os or draped
        self.dblsided=dblsided	# True or False
        self.alpha=alphacutoff	# AlphaTestValue or None
        self.shiny=shiny	# True or False
        self.shadow=xpver<10 or shadow	# True or False. v9 has no explicit support for shadows
        if poly:
            # Draped ignores all state - http://developer.x-plane.com/?article=obj8-file-format-specification#DRAPING
            self.poly=self.dblsided=self.shiny=False
            self.alpha=None
            self.shadow=True

    if __debug__:
        def __str__(self):
            return "d:%s s:%s poly:%s dbl:%s alpha:%s shiny:%s shadow:%s" % (self.d, self.s, self.poly, self.dblsided, self.alpha, self.shiny, self.shadow)

    def __eq__(self, o):
        # Note don't compare diffuse color cos its irrelevant once its been mapped to palette
        return self.s==o.s and self.alpha==o.alpha and self.shiny==o.shiny and self.shadow==o.shadow

    def clone(self):
        return Material(99, self.d, self.s, self.poly, self.dblsided, self.alpha, self.shiny, self.shadow)

# Texture collection
class Texture:

    def __init__(self, xpver, diffuse, emissive, specular=None, normal=None, reflection=None):
        # arguments are case-corrected full pathnames to source textures
        self.d=diffuse
        self.e=emissive
        self.s=xpver>10 and specular or None	# Specular map unused
        self.n=xpver>10 and normal or None	# Normal map unused
        self.r=xpver>10 and reflection or None	# Reflection map unused

    if __debug__:
        def __str__(self):
            return "d:%s e:%s s:%s n:%s r:%s" % (self.d and basename(self.d), self.e and basename(self.e), self.s and basename(self.s), self.n and basename(self.n), self.r and basename(self.r))

    def __eq__(self, o):
	# Only compare on diffuse (unless diffuse is None)
        assert (not self.s and not self.n and not self.r)	# Naming scheme will need re-work
        return isinstance(o,Texture) and self.d==o.d and (self.d or self.e==o.e)

    def __hash__(self):
        return hash(self.d or (None,self.e))	# Only compare on diffuse (unless diffuse is None)

class Object:
    def __init__(self, name, comment, tex, layer, vlight=None, veffect=None):
        self.name=name
        self.comment=comment
        self.tex=tex
        self.layer=layer		# FS layer - can only be set in pre-FS9 BGL code
        self.vlight=vlight or []	# http://docs.python.org/2/tutorial/controlflow.html#default-argument-values
        self.veffect=veffect or []
        self.vt=[]
        self.idx=[]
        self.mattri=[]			# [(Material, start, count)]

    def __eq__(self, o):
        return (#self.name==o.name and		# don't care about name
                #self.comment==o.comment and	# redundant
                isinstance(o,Object) and
                self.tex==o.tex and
                self.layer==o.layer and
                self.vt==o.vt and
                self.vlight==o.vlight and
                self.veffect==o.veffect and
                self.mattri==o.mattri)

    def addgeometry(self, mat, vt, idx):
        if not vt:		# re-using existing vertex table
            start=len(self.idx)
            count=len(idx)
            self.idx.extend(idx)
        elif not self.vt:	# common case
            start=0
            count=len(idx)
            self.vt=[(round(x,3), round(y,3), round(z,3), round(nx,3), round(ny,3), round(nz,3), round(tu,3), round(tv,3)) for (x,y,z,nx,ny,nz,tu,tv) in vt]	# round to increase chance of detecting dupes
            self.idx.extend(idx)
        else:
            base=len(self.vt)
            start=len(self.idx)
            count=len(idx)
            self.vt.extend([(round(x,3), round(y,3), round(z,3), round(nx,3), round(ny,3), round(nz,3), round(tu,3), round(tv,3)) for (x,y,z,nx,ny,nz,tu,tv) in vt])	# round to increase chance of detecting dupes
            self.idx.extend([base+i for i in idx])
        if not self.mattri:	# or __debug__:
            self.mattri.append((mat, start, count))
        else:
            # Consolidate TRI commands if possible
            (oldmat, oldstart, oldcount)=self.mattri[-1]
            if start==oldstart+oldcount and oldmat==mat:
                self.mattri[-1]=(oldmat, oldstart, oldcount+count)	# Merge successive
            else:
                self.mattri.append((mat, start, count))

    def filename(self, scale):
        assert not self.tex or (not self.tex.s and not self.tex.n and not self.tex.r)	# Naming scheme will need re-work
        if self.tex and (self.tex.d or self.tex.e):
            (tex,ext)=splitext(basename(self.tex.d or self.tex.e))
            if not ext.lower() in ['.dds', '.bmp', '.png']: tex+=ext[1:].lower()	# For *.xAF etc
            filename=asciify("%s-%s" % (self.name, tex))
        else:
            filename=self.name
        if scale!=1:
            filename="%s_%02d%02d.obj" % (filename, int(scale), round(scale*100,0)%100)
        else:
            filename=filename+'.obj'
        return filename
        
    def export(self, scale, output, fslayers):
        if not self.comment: return		# Nothing to do for X-Plane library objects

        if scale!=1:
            comment="%s scaled x%s" % (self.comment, scale)
        else:
            comment=self.comment

        if self.tex and self.tex.d and not exists(self.tex.d) and basename(self.tex.d).lower() in ['treeswi.bmp', 'treessp.bmp', 'treessu.bmp', 'treesfa.bmp', 'treeshw.bmp']:
            # Special handling for trees using default MSFS tree texture
            (tex,lit)=maketexs(output.dds and 'Resources/trees.dds' or 'Resources/trees.png', None, output)
        elif not self.tex:
            # Palette
            (tex,lit)=maketexs(output.palettetex, None, output)
        elif self.vt:
            assert self.tex.d!=None	# self.tex should just be None instead
            (tex,lit)=maketexs(self.tex.d, self.tex.e, output)
        else:
            tex=lit=None

        if False: #output.debug:
            # Generate line at object origin
            self.vline.insert(0, (0, 0, 0,  1, 0.5, 0.5))
            self.vline.insert(1, (0, 25, 0, 1, 0.5, 0.5))
            self.idx.insert(0,0)
            self.idx.insert(1,1)
            for i in range(len(self.mattri)):
                (m, start, count, dbl)=self.mattri[i]
                self.mattri[i]=(m, start+2, count, dbl)
        
        # Re-order to move poly/draped items first
        poly=False
        for i in range(len(self.mattri)):
            (mat,start,count)=self.mattri[i]
            if mat.poly:
                self.mattri.pop(i)
                self.mattri.insert(0, (mat,start,count))
                poly=True
        # Have to calculate an explicit LOD for draped-only geometry
        if not self.vt and len(self.vlight)<=1 and len(self.veffect)<=1:
            # X-Plane optimises single lights away otherwise
            lod=1000
        else:
            minx=minz=maxint
            maxx=maxz=-maxint
            for (x,y,z, nx,ny,nz, tu,tv) in self.vt:
                minx=min(minx,x)
                maxx=max(maxx,x)
                minz=min(minz,z)
                maxz=max(maxz,z)
            lod=sqrt((maxx-minx)*(maxz-minz))*120	# Roughly what X-Plane 10 calculates if LOD not specified?
            lod=max(1000,round(lod+5,-1))		# round up to next 10 for neatness, and set a minimum size
            if not (poly and output.draped) and lod>1000:
                lod=None	# If larger than minimum, let X-Plane calculate for non-draped

        try:
            path=join(output.xppath, 'objects')
            if not isdir(path): mkdir(path)
            objpath=join(path, self.filename(scale))
            assert not exists(objpath), self.filename(scale)	# Something's wrong if the target file already exists
            objfile=file(objpath, 'wt')
            if not self.filename(scale) in listdir(path):
                raise IOError	# case mixup
            objfile.write("I\n800\t# %sOBJ\n" % banner)
            objfile.write("\n# %s\n\n" % comment)
            if tex and self.vt:
                objfile.write("TEXTURE\t\t%s\n" % tex)
                if lit:
                    objfile.write("TEXTURE_LIT\t%s\n" % lit)
                if poly and output.draped:
                    objfile.write("TEXTURE_DRAPED\t%s\n" % tex)
                    # lit not supported
            else:
                objfile.write("TEXTURE\t\n")
    
            objfile.write("POINT_COUNTS\t%d %d %d %d\n\n" % (len(self.vt), 0, len(self.vlight), len(self.idx)))

            for (x,y,z,nx,ny,nz,u,v) in self.vt:
                objfile.write("VT\t%8.3f %8.3f %8.3f\t%6.3f %6.3f %6.3f\t%6.4f %6.4f\n" % (x*scale, y*scale, z*scale, nx,ny,nz, u,v))
            if self.vt: objfile.write("\n")

            for (x,y,z,r,g,b) in self.vlight:
                objfile.write("VLIGHT\t%8.3f %8.3f %8.3f\t%6.3f %6.3f %6.3f\n" % (x*scale, y*scale, z*scale, r, g, b))
            if self.vlight: objfile.write("\n")

            n=len(self.idx)
            for i in range(0, n-9, 10):
                objfile.write("IDX10\t")
                for j in range(i, i+9):
                    objfile.write("%d " % self.idx[j])
                objfile.write("%d\n" % self.idx[i+9])
            for j in range(n-(n%10), n):
                objfile.write("IDX\t%d\n" % self.idx[j])
            if self.idx: objfile.write("\n")

            if self.tex and self.tex.s: objfile.write("GLOBAL_specular\t%5.3f\n" % 1)	# needed for specular map
            # default state
            poly=False
            dblsided=False
            alpha=None
            shiny=False
            shadow=True
            for (mat, start, count) in self.mattri:
                if mat.poly and not poly:
                    if output.draped:
                        if self.layer:
                            objfile.write("ATTR_layer_group_draped\t%s\n" % fslayers[self.layer])
                        if lod:
                            objfile.write("ATTR_LOD_draped\t%d\n" % lod)
                        objfile.write("ATTR_draped\n")
                    else:
                        if self. layer:
                            objfile.write("ATTR_layer_group\t%s\n" % fslayers[self.layer])
                            #if layer and layer>4)	# can't remember where '4' is documented
                            #    objfile.write("ATTR_hard\tconcrete\n")
                        if lod:
                            objfile.write("ATTR_LOD\t0 %d\n" % lod)
                        objfile.write("ATTR_poly_os\t%d\n" % 2)
                elif poly and not mat.poly:
                    if output.draped:
                        objfile.write("\nATTR_no_draped\n")
                        if lod:
                            objfile.write("ATTR_LOD\t0 %d\n" % lod)
                    else:
                        objfile.write("\nATTR_poly_os\t%d\n" % 0)
                elif lod and not poly:	# assumes poly sorted first
                    objfile.write("ATTR_LOD\t0 %d\n" % lod)
                    lod=None
                poly=mat.poly

                if mat.shadow and not shadow:
                    objfile.write("ATTR_shadow\n")
                elif shadow and not mat.shadow:
                    objfile.write("ATTR_no_shadow\n")
                shadow=mat.shadow
                
                assert not (self.tex and self.tex.s and mat.shiny)	# specularity is handled using GLOBAL_specular when we have a map
                if mat.shiny and not shiny:
                    objfile.write("ATTR_shiny_rat\t%5.3f\n" % 1)
                elif shiny and not mat.shiny:
                    objfile.write("ATTR_shiny_rat\t%5.3f\n" % 0)
                shiny=mat.shiny

                if mat.alpha and not alpha:
                    objfile.write("ATTR_no_blend\t%5.3f\n" % mat.alpha)
                elif alpha and not mat.alpha:
                    objfile.write("ATTR_blend\n")
                alpha=mat.alpha

                if mat.dblsided and not dblsided:
                    objfile.write("ATTR_no_cull\n")
                elif dblsided and not mat.dblsided:
                    objfile.write("ATTR_cull\n")
                dblsided=mat.dblsided

                objfile.write("TRIS\t%d %d\n\n" % (start, count))

            if self.vlight:
                objfile.write("LIGHTS\t0 %d\n\n" % len(self.vlight))
    
            for (x,y,z,effect,s) in self.veffect:
                objfile.write("%s\t%8.3f %8.3f %8.3f\t%6.3f\n" % (effect, x, y, z, s))
            if self.veffect: objfile.write("\n")

            objfile.close()
        except IOError:
            raise FS2XError("Can't write \"%s\"" % objpath)


class Polygon:
    def __init__(self, name, tex, nowrap, scale, layer, paging=None):
        self.name=name
        self.tex=tex
        self.nowrap=nowrap
        self.scale=scale
        self.layer=layer
        self.surface=(layer!=None and layer>4)
        self.paging=paging

    def __eq__(self, o):
        return (self.name==o.name and
                self.tex==o.tex and
                self.nowrap==o.nowrap and
                self.layer==o.layer)	 	# was ignored - 8.60 layer bug
                #self.scale==o.scale		# scale is boring
                #self.surface==o.surface	# redundant

    def filename(self):
        return self.name+'.pol'

    def export(self, output, fslayers):
        if self.paging and ((self.tex.d in output.donetex) or (self.tex.e and self.tex.e in output.donetex)):
            # Avoid paging shared textures
            self.paging=None
        (tex,lit)=maketexs(self.tex.d, self.tex.e, output, True)
        try:
            path=join(output.xppath, 'objects')
            objpath=join(path, self.filename())
            if not isdir(path): mkdir(path)
            objfile=file(objpath, 'wt')
            if not self.filename() in listdir(path):
                raise IOError	# case mixup
            objfile.write("I\n850\t# %sDRAPED_POLYGON\n\n" % banner)
            if tex:
                if self.nowrap:
                    suffix='_NOWRAP'
                else:
                    suffix=''                    
                objfile.write("TEXTURE%s\t\t%s\n" % (suffix, tex))
                if lit:
                    objfile.write("TEXTURE_LIT%s\t%s\n" % (suffix, lit))
            else:
                objfile.write("TEXTURE\t\n")
            objfile.write("SCALE\t\t%.1f %.1f\n" % (self.scale, self.scale))
            if self.layer!=None:
                objfile.write("LAYER_GROUP\t%s\n" % fslayers[self.layer])
            if self.paging:
                (lat, lon, pixels)=self.paging
                objfile.write("LOAD_CENTER\t%12.8f %13.8f %d %d\n" % (
                    lat, lon, int(self.scale*1.414), pixels))
            if self.surface:
                objfile.write("SURFACE\t\tconcrete\n")
            objfile.close()
        except IOError:
            raise FS2XError("Can't write \"%s\"" % objpath)


def maketexs(fstex, fslit, output, substituteblank=False):
    path=join(output.xppath, 'objects')
    if not isdir(path): mkdir(path)
    palno=None
    if fstex or fslit:
        if not fstex:
            fstex='Resources/transparent.png'
        elif fstex in output.haze:
            palno=output.haze[fstex]
        tex=maketex(fstex, path, output, palno, substituteblank)
    else:
        tex=None

    if fslit:
        if fslit in output.haze:
            palno=output.haze[fslit]
        lit=maketex(fslit, path, output, palno)
        return (tex,lit)
    else:
        return (tex,None)


# Assumes src filename has correct case
# Returns new base dst name
def maketex(src, dstdir, output, palno, substituteblank=False):
    if not substituteblank and src in output.donetex:
        return output.donetex[src]

    if dirname(src)=='Resources':
        # texture is supplied with this program (eg FS2X-palette.png)
        tex=output.donetex[src]=basename(src)
        copy2(join(os.getcwdu(),src), dstdir)
        return tex

    # Spaces not allowed in textures. Avoid Mac/PC interop problems
    (tex,ext)=splitext(asciify(basename(src)))

    if tex[-3:].lower()=='_lm':
        tex=tex[:-3]+'_LIT'
    ext=ext.lower()
    if not ext in ['.dds', '.bmp', '.png']:
        tex+=ext	# For *.xAF etc

    if not exists(src):
        if output.dds:
            tex=tex+'.dds'
        else:
            tex=tex+'.png'
        for f in listdir('Resources'):
            if f.lower()==tex.lower():
                copy2(join(os.getcwdu(),'Resources',tex), dstdir)
                output.donetex[src]=tex
                return tex
        if src not in output.donetex:
            output.log("Texture %s not found" % basename(src))
        if substituteblank:
            # Missing texture in polygon causes crash
            if output.dds:
                copy2(join(os.getcwdu(),'Resources','blank.dds'), dstdir)
                return 'blank.dds'
            else:
                copy2(join(os.getcwdu(),'Resources','blank.png'), dstdir)
                return 'blank.png'
        output.donetex[src]=tex
        return tex
    elif src in output.donetex:
        return output.donetex[src]

    if output.dds and ext in ['.dds', '.bmp']:
        dds=tex+'.dds'
        dst=join(dstdir,dds)
        x=helper(output.ddsexe, src, dst)
        if exists(dst):
            output.donetex[src]=dds
            return dds
        elif output.debug:
            output.debug.write("DDS:\t%s:\t%s\n" % (src, x))

    tex+='.png'
    dst=join(dstdir,tex)
    try:
        newsrc=src
        if stat(src).st_size>=65536 and stat(src).st_size<65600:
            # Fucking nl2000 guys append crud to eof
            f=file(src, 'rb')
            c=f.read(4)
            if c[:2]!='BM' and c!='DDS ':
                # Not a BMP or DDS. Assume RAW and add standard BMP header
                f.seek(0)
                newsrc=join(gettempdir(), basename(src))
                t=file(newsrc, 'wb')
                for x in rawbmphdr:
                    t.write(pack('<H',x))
                t.write(f.read())
                t.close()
            f.close()

        if palno:
            x=helper(output.pngexe, '-xbrqp%d' % (palno-1), '-o', dst, newsrc)
        else:
            x=helper(output.pngexe, '-xbrq', '-o', dst, newsrc)
        if newsrc!=src: unlink(newsrc)
        if not exists(dst):
            output.log("Can't convert texture %s\n%s" % (basename(src),x))
        elif output.debug:
            output.debug.write("PNG:\t%s:\t%s\n" % (src, x))

    except IOError:
        output.log("Can't convert texture %s" % basename(src))

    output.donetex[src]=tex
    return tex


# Uniquify list, retaining order. Assumes list items are hashable
def unique(seq):
    seen = set()
    result = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


# Convert r,g,b to offset in palette texture
def rgb2uv(rgb):
    (r,g,b)=rgb
    r=(round(r*15,0)+0.5)/64
    g=(round(g*15,0)+0.5)/64
    b=(round(b*15,0)+0.5)
    return (int(b%4)/4.0 + r, int(b/4)/4.0 + g)


# Run helper app and return stderr
def helper(*cmds):
    if platform=='win32':
        # Bug - how to suppress environment variable expansion?
        cmdstr=cmds[0]+' '+' '.join(['"%s"' % cmd for cmd in cmds[1:]])
        if type(cmdstr)==types.UnicodeType:
            # commands must be MBCS encoded
            cmdstr=cmdstr.encode("mbcs")
    else:
        # See "QUOTING" in bash(1).
        cmdstr=' '.join(['"%s"' % cmd.replace('\\','\\\\').replace('"','\\"').replace("$", "\\$").replace("`", "\\`") for cmd in cmds])
    (i,o,e)=popen3(cmdstr)
    i.close()
    err=o.read()
    err+=e.read()
    o.close()
    e.close()
    #if __debug__: print err
    err=err.strip().split('\n')
    if len(err)>1 and err[-1].startswith('('):
        err=err[-2].strip()	# DSF errors appear on penultimate line
    else:
        err=', '.join(err)
    return err


# View contents of file
def viewer(filename):
    try:
        if 'startfile' in dir(os):
            os.startfile(filename)
        else:
            filename=abspath(filename)
            if type(filename)==types.UnicodeType:
                filename=filename.encode('utf-8')
            webbrowser.open("file:"+quote(filename))
    except:
        pass


# Turn string into ascii
def asciify(s, forfilename=True):
    if type(s)==types.UnicodeType:
        s=normalize(s)
    if forfilename:
        s=s.replace(' - ','_')
    # s may be unicode, so can't use translate()
    a=''
    for c in s:
        if ord(c)<32 or ord(c)>255:
            a=a+'_'
        elif c in ' \\/:*?"<>|"' and forfilename:
            a=a+'_'
        elif ord(c)<0x7b:
            a=a+chr(ord(c))	# convert from unicode string
        else:			# X-Plane won't show {|}~ either
            a=a+asciitbl[ord(c)-0x7b]
    return a


# Turn 8-bit string into unicode
def unicodeify(s):
    if type(s)==types.UnicodeType:
        return s
    else:
        return unicode(s, 'latin_1')


# Return normalized (pre-combined) unicode string
def normalize(s):
    return unicodedata.normalize('NFC',s)
    
# cross product of two triples
def cross(a, b):
    (ax,ay,az)=a
    (bx,by,bz)=b
    return (ay*bz-az*by, az*bx-ax*bz, ax*by-ay*bx)

# dot product of two triples
def dot(a, b):
    (ax,ay,az)=a
    (bx,by,bz)=b
    return ax*bx + ay*by + az*bz


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
