#
# Copyright (c) 2005,2006,2007 Jonathan Harris
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

from glob import glob
from math import floor
from os import listdir
from os.path import basename, join
import re

from convutil import Polygon, Point

LATRES=360.0/32768
LONRES=480.0/32768

photore=re.compile(r"S(\d)\$([+-]*\d+)-([+-]*\d+)_(\d)_(\d)\.[bB][mM][pP]$")


# Handle FS2004 and www.blueskyscenery.com photoscenery
def ProcPhoto(texdir, output):

    if output.debug: output.debug.write("%s\n" % texdir.encode("utf-8"))

    texs=listdir(texdir)
    texdict=dict([[i,True] for i in texs])

    # Blue Sky Scenery style
    for tex in texs:
        match=photore.split(tex)
        if not match or len(match)<6: continue
        lat=int(match[2])
        lon=int(match[3])
        layer=int(match[1])
        res=0.125*layer
        name=tex[:-4]

        if ishigher(name, layer, lat,lon, texdict, output): continue

        # findtex is too slow
        for ext in ['_lm.bmp', '_lm.BMP', '_LM.bmp', '_LM.BMP']:
            if name+ext in texdict:
                lit=join(texdir,name+ext)
                break
        else:
            lit=None

        lat=(lat-int(match[4])*res)*LATRES
        lon=(lon+int(match[5])*res)*LONRES
        layer=4-layer
        if layer<1: layer=1
        makephoto(name, join(texdir,tex), lit, lat, lon, res, layer, output)

    # FS2004 style
    for tex in glob(join(texdir, '[0123][0123][0123][0123][0123][0123][0123][0123][0123][0123][0123][0123][0123][0123][0123][sS][uU].[bBdD][mMdD][pPsS]')):
        seasonal=glob(tex[:-6]+["[sS][pP]","[sS][uU]","[fF][aA]","[wW][iI]"][output.season]+".[bBdD][mMdD][pPsS]")
        if seasonal: tex=seasonal[0]
        # find NW point
        lat=lon=0
        for i in tex[-21:-6]:
            lat=lat+lat
            lon=lon+lon
            if i=='1': lon=lon+1
            elif i=='2': lat=lat+1
            elif i=='3':
                lat=lat+1
                lon=lon+1
        lat=8192-lat	# = 90
        lon=lon-12288	# = -180
        name=basename(tex)[:-6]

        if ishigher(name, 0, lat,lon, texdict, output): continue

        # findtex is too slow
        for ext in ['lm.bmp', 'lm.BMP', 'LM.bmp', 'LM.BMP']:
            if name+ext in texdict:
                lit=join(texdir,name+ext)
                break
        else:
            lit=None

        lat=lat*LATRES
        lon=lon*LONRES
        makephoto(name, tex, lit, lat, lon, 1, 0, output)


# Check for higher-res Blue Sky Scenery scenery
def ishigher(name, layer, lat,lon, texdict, output):
    bstr="%d-%d" % (lat,lon)
    for (res,n) in [(1,8),(2,4),(4,2)]:
        if res==layer: return False
        hires=True
        resstr="S%d$%s" % (res,bstr)
        for i in range(n):
            for j in range(n):
                if ("%s_%d_%d.bmp" % (resstr, i, j)) not in texdict and ("%s_%d_%d.BMP" % (resstr, i, j)) not in texdict:
                    hires=False
                    break
            else:
                continue
            break

        if hires:
            if output.debug: output.debug.write("Photo: %s higher res is %s\n" % (name, basename(resstr)))
            return True
    return False
                

def makephoto(name, tex, lit, lat, lon, scale, layer, output):
    # lat and lon are the NW corner cos that's how MSFS does it
    if output.debug: output.debug.write("Photo: %s %.6f,%.6f,%s " % (name, lat, lon, scale))
    if lon+LONRES*scale > floor(lon)+1:
        # Split EW
        if output.debug: output.debug.write("EW ")
        points=[[(Point(lat-LATRES*scale,lon),0,0),
                 (Point(lat-LATRES*scale,floor(lon)+1),(floor(lon)+1-lon)/(LONRES*scale),0),
                 (Point(lat,floor(lon)+1),(floor(lon)+1-lon)/(LONRES*scale),1),
                 (Point(lat,lon),0,1)],
                [(Point(lat-LATRES*scale,floor(lon)+1),(floor(lon)+1-lon)/(LONRES*scale),0),
                 (Point(lat-LATRES*scale,lon+(LONRES*scale)),1,0),
                 (Point(lat,lon+LONRES*scale),1,1),
                 (Point(lat,floor(lon)+1),(floor(lon)+1-lon)/(LONRES*scale),1)]]
    else:
        if output.debug: output.debug.write("OK ")
        points=[[(Point(lat-LATRES*scale,lon),0,0),	# SW
                 (Point(lat-LATRES*scale,lon+LONRES*scale),1,0),
                 (Point(lat,lon+LONRES*scale),1,1),	# NE
                 (Point(lat,lon),0,1)]]

    if lat>floor(lat-LATRES*scale)+1:
        if output.debug: output.debug.write("NS\n")
        # Split NS
        for i in range(len(points)):
            points.append([(Point(floor(lat-LATRES*scale)+1,points[i][3][0].lon),points[i][3][1],(floor(lat-LATRES*scale)+1-lat+LATRES*scale)/(LATRES*scale)),
                           (Point(floor(lat-LATRES*scale)+1,points[i][2][0].lon),points[i][2][1],(floor(lat-LATRES*scale)+1-lat+LATRES*scale)/(LATRES*scale)),
                           points[i][2], points[i][3]])
            points[i][2]=points[-1][1]
            points[i][3]=points[-1][0]
    elif output.debug: output.debug.write("OK\n")

    poly=Polygon(name+'.pol', tex, lit, True, int(1216*scale), layer)
    output.polydat[name]=poly
    for p in points:
        output.polyplc.append((name, 65535, p))
