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

from math import sin, cos, atan, pi
from os import listdir
from os.path import join

from convutil import Object, rgb2uv, palettetex

# X-Plane autonmatically generates versions of these from nav.dat data 
ignorestock=['air_localizerantenna01', 'air_ndb_dmeantenna','air_ndb_dmeshack','air_ndb_dmetower','gen_dme','gen_ndb01','gen_tacan','ndb','sco_gen_checkershed','sco_gen_ilstransmitter','sco_gen_radarshackb','sco_gen_radarshackbaseb','sco_gen_radarshackdish','sco_gen_vor03','sco_gen_vor03dme','sco_gen_vorsmall','sco_gen_vorsmall2','sco_gen_vorsmall2dme','sco_gen_vorsmalldme']

# Stock X-Plane objects that are close enough to stock MSFS objects
libobjs={'ag_gas_2':		'trans/truckstop.obj',
         'ag_gas_3':		'ind/truckstop.obj',
         'gen_aviator01':	'lib/cars/car.obj',
         'gen_oilrig01':	'lib/ships/OilPlatform.obj',
         'gen_rig01':		'lib/ships/OilPlatform.obj',	
         'sailboat_big_down':	'lib/ships/SailBoat.obj',
         'sailboat_big_up':	'lib/ships/SailBoat.obj',
         'sailboat_s_down':	'lib/ships/SailBoat.obj',
         'sailboat_s_up':	'lib/ships/SailBoat.obj',
         'veh_carrier1':	'lib/ships/Carrier.obj',
         'veh_water_eastcoastcarrier1':	'lib/ships/Carrier.obj',
         'veh_water_sailboat1':	'lib/ships/SailBoat.obj',
         'veh_water_sailboat2':	'lib/ships/SailBoat.obj',
         'veh_water_sailboat3':	'lib/ships/SailBoat.obj',
         'veh_water_sailboat4':	'lib/ships/SailBoat.obj',
         'veh_water_sailboat5':	'lib/ships/SailBoat.obj',
         'veh_water_smallboat1':'lib/ships/SailBoat.obj',
         'veh_water_smallboat2':'lib/ships/SailBoat.obj',
         'veh_water_smallboat3':'lib/ships/SailBoat.obj',
         'veh_water_smallboat4':'lib/ships/SailBoat.obj',
         }

def makeapronlight():
    vlight=[(0,1,0, 0.3125,0.3125,1)]
    vt=[(-1.5,0,-1.5, 0,1,0, 0,0),
        (-1.5,0, 1.5, 0,1,0, 0,1),
        ( 1.5,0, 1.5, 0,1,0, 1,1),
        ( 1.5,0,-1.5, 0,1,0, 1,0)]
    idx=[2,1,0,3,2,0]
    return Object("ApronLight.obj", "ApronEdgeLights",
                  'Resources/FS2X-ApronLight.png', None, None,
                  vlight, [], [], vt, idx,
                  [([(1,1,1),(0,0,0),(0,0,0),0.5],0,6,False)], 2)
    

def maketaxilight():
    vlight=[(0,0.1,0, 0.75,0.75,0)]
    return Object("TaxiwayLight.obj",
                  "TaxiwayPath.centerLineLighted", None, None, None,
                  vlight, [], [], [], [], [], 0)
    

def maketaxisign(label):

    drrmap={'0':(4,19),
            '1':(23,35),
            '2':(39,54),
            '3':(58,73),
            '4':(77,92),
            '5':(96,111),
            '6':(115,130),
            '7':(134,149),
            '8':(153,168),
            '9':(172,187),
            'A':(191,208),
            'B':(212,227),
            'C':(231,246),
            'D':(250,265),
            'E':(269,284),
            'F':(288,303),
            'G':(307,322),
            'H':(326,341),
            'I':(345,354),
            'J':(358,373),
            'K':(377,392),
            'L':(396,411),
            'M':(415,433),
            'N':(437,455),
            'O':(459,477),
            'P':(481,496),
            'Q':(500,518),
            'R':(522,537),
            'S':(541,556),
            'T':(560,575),
            'U':(579,596),
            'V':(600,615),
            'W':(619,637),
            'X':(641,656),
            'Y':(660,675),
            'Z':(679,695),
            '-':(699,708),
            '*':(712,722),
            '<':(726,741),
            '>':(745,760),
            '^':(764,779),
            'v':(783,798),
            '/':(802,817),
            '\\':(821,836),
            "`":(840,855),
            "'":(859,874),
            '.':(878,885),
            ',':(889,896),
            '[':(960,968),
            ']':(1016,1024)}

    row=0	# 0=dir (b on y), 1=rwy (w on r), 2=lcn (y on b)
    addbracket=False
    donebracet=False	# Just done a bracket
    addspace=False
    array=[]	# (row, left, right)
    for c in label:
        if c=='l':
            row=2
        elif c=='d':
            row=0
        elif c=='m':
            row=1

        elif row==2:
            if c==' ':
                addspace=True
                if array and not donebracket:
                    (oldrow, start, end)=array[-1]
                    array[-1]=(oldrow,start,end+3)
            elif c=='[':
                addbracket=True
                donebracket=True
            elif c==']':
                if array:
                    (oldrow, start, end)=array[-1]
                    array[-1]=(oldrow, start, end+6)
                    addspace=False	# Can't do both
                donebracket=True
            else:
                if c in '0123456789':
                    start=32*int(c)+838
                elif c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    start=32*(ord(c)-ord('A'))+6
                end=start+20
                if addbracket:
                    start=start-6
                elif addspace:		# Can't do both
                    start=start-3
                addspace=False
                addbracket=False
                donebracket=False
                array.append((row, start, end))

        elif c in drrmap:
            (start,end)=drrmap[c]
            if c in ['[',']']:
                donebracket=True
            else:
                donebracket=False
                if addspace:
                    start=start-2
            addspace=False
            array.append((row, start, end))
        elif c==' ':
            addspace=True
            if array and not donebracket:
                (oldrow, start, end)=array[-1]
                array[-1]=(oldrow, start, end+2)

    width=0
    for (row, start, end) in array:
        width=width+end-start
    height=1.0
    depth=0.15
    pix2m=0.03
    left=width/2.0

    # Do frame
    vt=[]
    ul=608/1024.0
    ur=640/1024.0
    # add back
    vt.append((-depth,0,     -left*pix2m, -1,0,0, ul,0))
    vt.append((-depth,height,-left*pix2m, -1,0,0, ul,0.25))
    vt.append((-depth,height, left*pix2m, -1,0,0, ur,0.25))
    vt.append((-depth,0,      left*pix2m, -1,0,0, ur,0))
                                        
    # add top                           
    vt.append(( depth,height, left*pix2m,  0,1,0, ul,0))
    vt.append((-depth,height, left*pix2m,  0,1,0, ul,0.25))
    vt.append((-depth,height,-left*pix2m,  0,1,0, ur,0.25))
    vt.append(( depth,height,-left*pix2m,  0,1,0, ur,0))
                                        
    # add left                          
    vt.append((-depth,0,      left*pix2m,  0,0,1, ul,0))
    vt.append((-depth,height, left*pix2m,  0,0,1, ul,0.25))
    vt.append(( depth,height, left*pix2m,  0,0,1, ur,0.25))
    vt.append(( depth,0,      left*pix2m,  0,0,1, ur,0))
                                        
    # add right                         
    vt.append(( depth,0,     -left*pix2m, 0,0,-1, ul,0))
    vt.append(( depth,height,-left*pix2m, 0,0,-1, ul,0.25))
    vt.append((-depth,height,-left*pix2m, 0,0,-1, ur,0.25))
    vt.append((-depth,0,     -left*pix2m, 0,0,-1, ur,0))

    frameilen=(len(vt)*3)/2

    # Do the face
    width=0    
    for (row, start, end) in array:
        # hack for 6-9 in row 2
        if start>1024:
            start=start-1024
            end=end-1024
            row=row+1

        # bl, tl, tr, br
        vt.append((depth,0,     (left-width)*pix2m,
                   1,0,0, start/1024.0,(3-row)/4.0))
        vt.append((depth,height,(left-width)*pix2m,
                   1,0,0, start/1024.0,(4-row)/4.0))
        width=width+end-start
        vt.append((depth,height,(left-width)*pix2m,
                   1,0,0, end/1024.0,(4-row)/4.0))
        vt.append((depth,0,     (left-width)*pix2m,
                   1,0,0, end/1024.0,(3-row)/4.0))


    idx=[]
    for i in range(0,len(vt),4):
        idx.extend([i,i+1,i+2,i,i+2,i+3])

    # Make a legal filename
    fname=label
    fname=fname.replace('/',',')
    fname=fname.replace('\\','.')
    fname=fname.replace('<','{')
    fname=fname.replace('>','}')
    for c in ':*?"|':
        fname=fname.replace(c,'_')
    fname="TaxiwaySign-%s.obj" % fname
    return Object(fname, 'TaxiwaySign "%s"' % label,
                  'Resources/FS2X-Taxi.png', None, None, [], [], [], vt, idx,
                  [([(1,1,1),(0,0,0),(0,0,0),0.5],
                    0,frameilen,False),
                   ([(1,1,1),(0,0,0),(1,1,1),0.5],
                    frameilen,len(idx)-frameilen,False)], 0)


def makestock(output, uid, name):
    if name in libobjs:
        return Object(libobjs[name], "X-Plane library object", None,None,None,
                      None, None, None, None, None, None, 0)
    
    objname=name+'.obj'
    #defaultobj=Object(objname, "Placeholder for built-in object %s (%s)" %
    #                  (uid, name), None, None, None, [], [], [], [], [], [],0)
    if not objname in listdir('Resources'): return None

    tex=None
    vt=[]
    idx=[]
    obj=file(join('Resources', objname), 'rU')
    if obj.next() not in ['A\n', 'I\n']: return None
    if not obj.next().startswith('800'): return None
    if obj.next()!='OBJ\n': return None
    for line in obj:
        tokens=line.split()
        if not tokens:
            continue
        if tokens[0]=='TEXTURE' and len(tokens)==2:
            tex='Resources/'+tokens[1]
        elif tokens[0]=='VT' and len(tokens)==9:
            vt.append((float(tokens[1]), float(tokens[2]), float(tokens[3]),
                       float(tokens[4]), float(tokens[5]), float(tokens[6]),
                       float(tokens[7]), float(tokens[8])))
        elif tokens[0]=='IDX' and len(tokens)==2:
            idx.append(int(tokens[1]))
        elif tokens[0]=='IDX10' and len(tokens)==11:
            idx.extend([int(tokens[1]), int(tokens[2]), int(tokens[3]),
                        int(tokens[4]), int(tokens[5]), int(tokens[6]),
                        int(tokens[7]), int(tokens[8]), int(tokens[9]),
                        int(tokens[10])])
    obj.close()
    return Object(objname, "(c) Jonathan Harris 2007. http://creativecommons.org/licenses/by-sa/2.5/",
                  tex, None, None, [], [], [], vt, idx,
                  [([(1,1,1),(0,0,0),(0,0,0),0.5], 0, len(idx), False)], 0)


def makegenquad(name, x, z, incx, incz, heights, texs, roof):
    # roof types: 0=flat, 1=pointy, 2=gabled, 3=slanty
    cumheight=0
    vt=[]
    idx=[]
    rgbs=[]
    for i in range(len(texs)):
        rgbs.append(genrgb(i, texs[i]))
    sign=[(1,1), (1,-1), (-1,-1), (-1,1), (1,1)]
    n=[( cos(incx),sin(incx),0), (0,sin(incz),-cos(incz)),
       (-cos(incx),sin(incx),0), (0,sin(incz), cos(incz))]
    for story in range(3):
        if not heights[story]:
            continue
        (u,v)=rgb2uv(rgbs[story])
        x0=x/2-sin(incx)*cumheight
        z0=z/2-sin(incz)*cumheight
        x1=x/2-sin(incx)*(cumheight+heights[story])
        z1=z/2-sin(incz)*(cumheight+heights[story])
        for side in range(4):
            (nx,ny,nz)=n[side]
            base=len(vt)
            for corner in [side, side+1]:
                (sx,sz)=sign[corner]
                vt.extend([(sx*x0, cumheight, sz*z0, nx,ny,nz, u,v),
                           (sx*x1, cumheight+heights[story], sz*z1,
                            nx,ny,nz, u,v)])
            idx.extend([base,base+1,base+2, base+3,base+2,base+1])
        cumheight += heights[story]

    # roof
    x0=x/2-sin(incx)*cumheight
    z0=z/2-sin(incz)*cumheight
    (u,v)=rgb2uv(rgbs[3])
    base=len(vt)
    if roof==0 or heights[3]==0:        # simplify if actually flat
        vt.extend([( x0, cumheight,  z0, 0,1,0, u,v),
                   ( x0, cumheight, -z0, 0,1,0, u,v),
                   (-x0, cumheight, -z0, 0,1,0, u,v),
                   (-x0, cumheight,  z0, 0,1,0, u,v)])
        idx.extend([base+2,base+1,base, base,base+3,base+2])

    elif roof==1:
        # pointy
        topheight=cumheight+heights[3]
        incx=atan(x/(2*heights[3]))
        incz=atan(z/(2*heights[3]))
        vt.extend([( x0, cumheight,  z0,  cos(incx),sin(incx),0, u,v),
                   (  0, topheight,   0,  cos(incx),sin(incx),0, u,v),
                   ( x0, cumheight, -z0,  cos(incx),sin(incx),0, u,v),
                   (-x0, cumheight,  z0, -cos(incx),sin(incx),0, u,v),
                   (  0, topheight,   0, -cos(incx),sin(incx),0, u,v),
                   (-x0, cumheight, -z0, -cos(incx),sin(incx),0, u,v),
                   ( x0, cumheight,  z0, 0,sin(incz), cos(incz), u,v),
                   (  0, topheight,   0, 0,sin(incz), cos(incz), u,v),
                   (-x0, cumheight,  z0, 0,sin(incz), cos(incz), u,v),
                   ( x0, cumheight, -z0, 0,sin(incz),-cos(incz), u,v),
                   (  0, topheight,   0, 0,sin(incz),-cos(incz), u,v),
                   (-x0, cumheight, -z0, 0,sin(incz),-cos(incz), u,v)])
        idx.extend([  base,base+1,base+2, base+5,base+4,base+3,
                    base+8,base+7,base+6, base+9,base+10,base+11])

    elif roof==2:
        # gabled
        topheight=cumheight+heights[3]
        incz=atan(z/(2*heights[3]))
        ny=sin(incz)
        nz=cos(incz)
        #roof
        vt.extend([( x0, cumheight,  z0, 0,ny,nz, u,v),
                   ( x0, topheight,   0, 0,ny,nz, u,v),
                   (-x0, topheight,   0, 0,ny,nz, u,v),
                   (-x0, cumheight,  z0, 0,ny,nz, u,v),
                   ( x0, cumheight, -z0, 0,ny,-nz, u,v),
                   ( x0, topheight,   0, 0,ny,-nz, u,v),
                   (-x0, topheight,   0, 0,ny,-nz, u,v),
                   (-x0, cumheight, -z0, 0,ny,-nz, u,v)])
        idx.extend([base+2,base+1,base,     base,base+3,base+2,
                    base+4,base+5,base+6, base+6,base+7,base+4])
        #gables
        (u,v)=rgb2uv(rgbs[4])
        base=len(vt)
        vt.extend([( x0, cumheight,  z0, 1,0,0, u,v),
                   ( x0, topheight,   0, 1,0,0, u,v),
                   ( x0, cumheight, -z0, 1,0,0, u,v),
                   (-x0, cumheight,  z0, -1,0,0, u,v),
                   (-x0, topheight,   0, -1,0,0, u,v),
                   (-x0, cumheight, -z0, -1,0,0, u,v)])
        idx.extend([base,base+1,base+2, base+5,base+4,base+3])

    elif roof==3:
        # slanty
        topheight=cumheight+heights[3]
        incz=atan(z/heights[3])
        ny=sin(incz)
        nz=cos(incz)
        #roof
        vt.extend([( x0, cumheight,  z0, 0,ny,nz, u,v),
                   ( x0, topheight, -z0, 0,ny,nz, u,v),
                   (-x0, topheight, -z0, 0,ny,nz, u,v),
                   (-x0, cumheight,  z0, 0,ny,nz, u,v)])
        idx.extend([base+2,base+1,base, base,base+3,base+2])
        #gables
        (u,v)=rgb2uv(rgbs[4])
        base=len(vt)
        vt.extend([( x0, topheight, -z0,  1,0,0, u,v),
                   ( x0, cumheight, -z0,  1,0,0, u,v),
                   ( x0, cumheight,  z0,  1,0,0, u,v),
                   (-x0, topheight, -z0, -1,0,0, u,v),
                   (-x0, cumheight, -z0, -1,0,0, u,v),
                   (-x0, cumheight,  z0, -1,0,0, u,v)])
        idx.extend([base,base+1,base+2, base+5,base+4,base+3])
        #face
        (u,v)=rgb2uv(rgbs[5])
        base=len(vt)
        vt.extend([( x0, topheight, -z0, 0,0,-1, u,v),
                   ( x0, cumheight, -z0, 0,0,-1, u,v),
                   (-x0, cumheight, -z0, 0,0,-1, u,v),
                   (-x0, topheight, -z0, 0,0,-1, u,v)])
        idx.extend([base+2,base+1,base, base,base+3,base+2])
        
    return Object(name, "Generic building", palettetex, None,
                  None, [], [], [], vt, idx,
                  [([(1,1,1),(0,0,0),(0,0,0),0.5], 0, len(idx), False)], 0)


def makegenmulti(name, sides, x, z, heights, texs):
    # building fits inside an oval inscribed in a x*z box
    slice=2*pi/sides
    halfslice=pi/sides
    sides2=sides*2
    cumheight=0
    vt=[]
    idx=[]
    rgbs=[]
    for i in range(len(texs)):
        rgbs.append(genrgb(i, texs[i]))
    for story in range(3):
        (u,v)=rgb2uv(rgbs[story])
        base=len(vt)
        for corner in range(sides):
            angle=corner*slice-halfslice
            nx=sin(angle)
            nz=cos(angle)
            x0=x*nx/2
            z0=z*nz/2
            vt.append((x0, cumheight, z0, nx,0,nz, u,v))
            vt.append((x0, cumheight+heights[story], z0, nx,0,nz, u,v))
            idx.extend([base + corner*2,
                        base +(corner*2+1)%sides2,
                        base +(corner*2+2)%sides2,
                        base +(corner*2+3)%sides2,
                        base +(corner*2+2)%sides2,
                        base +(corner*2+1)%sides2])
        cumheight += heights[story]

    # roof
    (u,v)=rgb2uv(rgbs[3])
    base=len(vt)

    if heights[3]==0:        # simplify if actually flat
        for corner in range(sides):
            angle=corner*slice-halfslice
            x0=sin(angle)*x/2
            z0=cos(angle)*z/2
            vt.append((x0, cumheight, z0, 0,1,0, u,v))
            vt.append((0,  cumheight, 0, 0,1,0, u,v))
            idx.extend([base +corner*2,
                        base+(corner*2+1)%sides2,
                        base+(corner*2+2)%sides2])
    else:
        incx=atan(x/(2*heights[3]))
        incz=atan(z/(2*heights[3]))
        for corner in range(sides):
            # FIXME: normal calculation is incorrect
            angle=corner*slice-halfslice
            nx=cos(incx)*sin(angle)
            ny=sin(incx)*sin(angle)+sin(incz)*cos(angle)
            nz=cos(incz)*cos(angle)
            x0=sin(angle)*x/2
            z0=cos(angle)*z/2
            vt.append((x0, cumheight, z0, nx,ny,nz, u,v))
            angle=corner*slice
            nx=cos(incx)*sin(angle)
            ny=sin(incx)*sin(angle)+sin(incz)*cos(angle)
            nz=cos(incz)*cos(angle)
            vt.append((0, cumheight+heights[3], 0, nx,ny,nz, u,v))
            idx.extend([base +corner*2,
                        base+(corner*2+1)%sides2,
                        base+(corner*2+2)%sides2])

    return Object(name, "Generic building", palettetex, None,
                  None, [], [], [], vt, idx,
                  [([(1,1,1),(0,0,0),(0,0,0),0.5], 0, len(idx), False)], 0)



# Generic buildings fallback colours from "Generic Building Textures.xls" in
# FS2004 BGLComp SDK. Note these are (b,g,r).

# Wall fallback colours
genwall=[
    (255,255,255),
    (255,255,255),
    (0,0,255),
    (0,0,255),
    (0,255,0),
    (0,255,0),
    (255,0,0),
    (255,0,0),
    (198,214,222),
    (198,214,222),
    (90,99,107),
    (90,99,107),
    (82,107,120),
    (82,107,120),
    (84,92,81),
    (84,92,81),
    (99,116,123),
    (99,116,123),
    (51,90,131),
    (51,90,131),
    (123,137,140),
    (123,137,140),
    (123,139,150),
    (123,139,150),
    (65,82,99),
    (65,82,99),
    (139,151,171),
    (139,151,171),
    (212,206,204),
    (212,206,204),
    (123,173,181),
    (123,173,181),
    (110,115,131),
    (110,115,131),
    (54,53,99),
    (54,53,99),
    (73,76,78),
    (73,76,78),
    (76,80,80),
    (76,80,80),
    (66,65,65),
    (66,65,65),
    (82,82,99),
    (82,82,99),
    (83,73,69),
    (83,73,69),
    (56,54,54),
    (56,54,54),
    (99,99,100),
    (99,99,100),
    (145,146,147),
    (145,146,147),
    (124,123,125),
    (124,123,125),
    (98,104,105),
    (98,104,105),
    (131,133,133),
    (131,133,133),
    (87,93,110),
    (87,93,110),
    (70,77,85),
    (70,77,85),
    (176,184,193),
    (176,184,193),
    (100,108,110),
    (100,108,110),
    (207,207,211),
    (207,207,211),
    (130,131,132),
    (130,131,132),
    (109,119,125),
    (109,119,125),
    (91,93,108),
    (91,93,108),
    (108,117,120),
    (108,117,120),
    (209,205,206),
    (209,205,206),
    (149,156,156),
    (149,156,156),
    (92,121,155),
    (92,121,155),
    (64,82,121),
    (64,82,121),
    (100,108,110),
    (100,108,110),
    ]

# Window fallback colours
genwin=[
    (255,255,255),
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (148,173,181),
    (198,214,214),
    (66,74,82),
    (156,173,173),
    (129,150,148),
    (48,101,148),
    (49,74,82),
    (129,149,137),
    (123,140,148),
    (115,140,148),
    (82,123,148),
    (57,90,148),
    (57,57,66),
    (115,132,140),
    (49,57,57),
    (82,123,140),
    (96,124,160),
    (60,59,64),
    (92,104,96),
    (44,66,89),
    (72,93,126),
    (71,83,120),
    (151,183,197),
    (141,196,213),
    (45,86,164),
    (57,74,115),
    (85,103,151),
    (152,196,224),
    (175,170,181),
    (92,121,155),
    (199,201,203),
    (52,54,49),
    (46,48,47),
    (50,48,50),
    (109,94,85),
    (152,139,131),
    (131,114,106),
    (54,56,58),
    (90,83,84),
    (70,71,72),
    (168,167,167),
    (103,106,105),
    (180,180,179),
    (191,190,190),
    (138,141,141),
    (112,112,112),
    (109,113,113),
    (88,89,97),
    (93,103,125),
    (48,56,62),
    (135,149,151),
    (163,167,167),
    (111,125,132),
    (201,207,207),
    (132,133,130),
    (142,141,137),
    (150,166,164),
    (178,191,209),
    (155,147,164),
    (100,111,156),
    (79,90,106),
    (117,125,133),
    (61,57,113),
    (166,167,169),
    (106,118,136),
    (131,131,106),
    (126,129,134),
    (189,205,214),
    (99,114,127),
    (26,20,28),
    (161,173,181),
    (102,89,83),
    (35,35,35),
    (50,48,49),
    (89,81,80),
    (45,45,45),
    (42,42,42),
    (70,76,78),
    (100,100,101),
    (201,206,209),
    (129,134,132),
    ]

# Roof fallback colours
genroof=[
    (255,255,255),
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (96,88,81),
    (114,118,120),
    (152,194,156),
    (158,162,161),
    (57,61,60),
    (74,82,99),
    (106,124,119),
    (125,132,130),
    (104,111,117),
    (149,146,147),
    (90,98,98),
    (116,118,122),
    (158,166,162),
    (130,133,125),
    (140,95,72),
    (58,58,50),
    (118,100,97),
    (108,88,78),
    (141,138,137),
    (154,151,149),
    (112,110,109),
    (100,100,101),
    (89,91,92),
    (91,91,90),
    (129,132,132),
    (147,149,149),
    (113,116,116),
    (74,78,78),
    (72,76,78),
    (128,139,139),
    ]


# Fallback colour for index in story
def genrgb(story, idx):
    if story==1:
        tbl=genwin
    elif story==3:
        tbl=genroof
    else:
        tbl=genwall

    if idx>=len(tbl):
        return (1,1,1)
    
    (b,g,r)=tbl[idx]
    return (r/255.0, g/255.0, b/255.0)

        
