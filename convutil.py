from math import sin, cos, tan, asin, acos, atan, atan2, fmod, pi
from os import mkdir, system, unlink
from os.path import basename, curdir, dirname, exists, isdir, join, normpath, splitext
from shutil import copyfile

version='0.90'
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
                     self.lon+biasX*360.0/(cire*cos(self.lat*2/pi)))

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
        self.mattri=mattri	# [((d,s,e), start, count)]

    def __eq__(self, o):
        return (self.filename==o.filename and
                self.comment==o.comment and
                self.tex==o.tex and
                self.vlight==o.vlight and
                self.vline==o.vline and
                self.vt==o.vt and
                self.idx==o.idx and
                self.mattri==o.mattri)

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
            path=join(output.xppath, 'custom object textures')
            if not isdir(path): mkdir(path)
            (dst,ext)=splitext(basename(self.tex))
            dst=normpath(join(path, dst+'.png'))
            try:
                # Special handling for trees if no texture supplied
                if not exists(self.tex) and basename(self.tex).upper() in ['TREESWI.BMP', 'TREESSP.BMP', 'TREESSU.BMP', 'TREESFA.BMP', 'TREESHW.BMP']:
                    self.tex='Tree_side.png'	# standard X-Plane v8 texture
                    dst=normpath(join(path, self.tex))
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

                elif dirname(self.tex)==curdir:
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
                    self.maketex(self.tex, dst, output)
                    (lit,ext)=splitext(self.tex)
                    lit+='_LM.BMP'
                    self.tex=basename(dst)
                    if exists(lit):
                        (dst,foo)=splitext(dst)
                        dst+='_LM.png'
                        self.maketex(lit, dst, output)
                        lit=basename(dst)
                    else:
                        lit=None

            except IOError:
                output.log("Can't create texture %s" % basename(dst))
                lit=None

        try:
            path=join(output.xppath, 'custom objects')
            objpath=join(path, filename)
            if not isdir(path): mkdir(path)
            objfile=file(objpath, 'wt')
            objfile.write("I\n800\t# %sOBJ\n" % banner)
            objfile.write("\n# %s\n\n" % comment)
            if self.tex:
                objfile.write("TEXTURE\t\t%s\n" % basename(self.tex))
                if lit:
                    objfile.write("TEXTURE_LIT\t%s\n" % basename(lit))
            else:
                objfile.write("TEXTURE\t\n")
    
            objfile.write("POINT_COUNTS\t%d %d %d %d\n\n" % (
                len(self.vt), len(self.vline), len(self.vlight),
                len(self.idx)))
            
            for (x,y,z,r,g,b) in self.vlight:
                objfile.write("VLIGHT\t%8.3f %8.3f %8.3f\t%5.3f %5.3f %5.3f\n" % (x*scale, y*scale, z*scale, r, g, b))
            if self.vlight: objfile.write("\n")
            
            for (x,y,z,r,g,b) in self.vline:
                objfile.write("VLINE\t%8.3f %8.3f %8.3f\t%5.3f %5.3f %5.3f\n" % (x*scale, y*scale, z*scale, r, g, b))
            if self.vline: objfile.write("\n")

            for (x,y,z,nx,ny,nz,u,v) in self.vt:
                objfile.write("VT\t%8.3f %8.3f %8.3f\t%6.3f %6.3f %6.3f\t%5.3f %5.3f\n" % (x*scale, y*scale, z*scale, nx,ny,nz, u,v))
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
                objfile.write("LIGHTS\t0 %d\n\n" % len(self.vlight))
            if self.vline:
                objfile.write("LINES\t0 %d\n\n" % len(self.vline))

            # Maybe a decal
            mins=0
            maxs=0
            for (x,y,z,nx,ny,nz,u,v) in self.vt:
                mins=min(mins,x*scale,z*scale)
                maxs=max(maxs,x*scale,z*scale)
                if y>=0.101:	# Arbitrary. 0.1 used in VF London
                    if self.mattri:
                        objfile.write("ATTR_no_blend\n")
                    break
            else:
                if self.vt:
                    if (maxs-mins)>NM2m/4:	# arbitrary
                        objfile.write("ATTR_poly_os 1\n")
                    else:                        
                        objfile.write("ATTR_poly_os 2\n")

            a=(1.0,1.0,1.0)
            s=(0.0,0.0,0.0)
            e=(0.0,0.0,0.0)
            for (m, start, count) in self.mattri:
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
            output.log("Can't write \"%s\"" % objpath)
        
    def maketex(self, src, dst, output):
        if exists(dst):
            return	# assume it's already been converted
        if not exists(src):
            output.log("Texture %s not found" % basename(src))
            raise IOError
        (foo,ext)=splitext(src)
        (tmp,foo)=splitext(dst)
        copyfile(src, tmp+ext)
        # imagetool may fail on some normal bmp files
        system(output.imgexe+' -nobeep -nogui -nomip -nowarning -32 "'+
               tmp+ext+'"')
        if (system(output.pngexe+' -aqe "'+tmp+ext+'" 2>nul:')!=0 or
            not exists(dst)):
            if exists(tmp+ext): unlink(tmp+ext)
            raise IOError
