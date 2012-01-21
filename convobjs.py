import codecs
from math import sin, cos, atan, pi
from os import listdir
from os.path import join
import xml.parsers.expat

from convutil import asciify, Object, rgb2uv

# X-Plane automatically generates versions of these from nav.dat data 
ignorestock=['air_localizerantenna01', 'air_ndb_dmeantenna','air_ndb_dmeshack','air_ndb_dmetower','gen_dme','gen_ndb01','gen_tacan','ndb','ndbhigh','sco_gen_checkershed','sco_gen_ilstransmitter','sco_gen_radarshackb','sco_gen_radarshackbaseb','sco_gen_radarshackdish','sco_gen_vor03','sco_gen_vor03dme','sco_gen_vorsmall','sco_gen_vorsmall2','sco_gen_vorsmall2dme','sco_gen_vorsmalldme']

# Stock MSFS objects that are close enough to stock X-Plane objects
libobjs={'ag_building_1':		'ins/church.obj',
         'ag_factory':			'/lib/global8/us/ind_irr_60_30r.obj',
         'ag_gas_2':			'trans/truckstop.obj',
         'ag_gas_3':			'ind/truckstop.obj',
         'gen_aviator01':		'lib/cars/car.obj',
         'gen_oilrig01':		'lib/ships/OilPlatform.obj',
         'gen_rig01':			'lib/ships/OilPlatform.obj',	
         'sailboat_big_down':		'lib/ships/SailBoat.obj',
         'sailboat_big_up':		'lib/ships/SailBoat.obj',
         'sailboat_s_down':		'lib/ships/SailBoat.obj',
         'sailboat_s_up':		'lib/ships/SailBoat.obj',
         'veh_carrier1':		'lib/ships/Carrier.obj',
         'veh_carrier2':		'lib/ships/Carrier.obj',
         'VEH_carrier01':		'lib/ships/Carrier.obj',
         'VEH_carrier01_high_detail':	'lib/ships/Carrier.obj',
         'VEH_cruiser01':		'lib/ships/Frigate.obj',
         'VEH_destroyer01':		'lib/ships/Frigate.obj',
         'veh_water_eastcoastcarrier1':	'lib/ships/Carrier.obj',
         'veh_water_eastcoastcarrier2':	'lib/ships/Carrier.obj',
         'veh_water_sailboat1':		'lib/ships/SailBoat.obj',
         'veh_water_sailboat2':		'lib/ships/SailBoat.obj',
         'veh_water_sailboat3':		'lib/ships/SailBoat.obj',
         'veh_water_sailboat4':		'lib/ships/SailBoat.obj',
         'veh_water_sailboat5':		'lib/ships/SailBoat.obj',
         'veh_water_smallboat1':	'lib/ships/SailBoat.obj',
         'veh_water_smallboat2':	'lib/ships/SailBoat.obj',
         'veh_water_smallboat3':	'lib/ships/SailBoat.obj',
         'veh_water_smallboat4':	'lib/ships/SailBoat.obj',
         }

def makestock(output, uid, name):
    if name in libobjs:
        return Object(libobjs[name], "X-Plane library object", None,None,None,None,
                      None, None, None, None, None, None, 0)
    
    objname=name+'.obj'
    #defaultobj=Object(objname, "Placeholder for built-in object %s (%s)" %
    #                  (uid, name), None, None, None, [],[],[],[],[],[],[],0)
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
            if output.dds and tokens[1][-4:]=='.png':
                tex='Resources/'+tokens[1][:-4]+'.dds'
            else:
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
    return Object(objname, "(c) Jonathan Harris 2008. http://creativecommons.org/licenses/by-sa/3.0/",
                  tex, None, None, [], [], [], [], vt, idx,
                  [([(1,1,1),(0,0,0),(0,0,0),0.5], 0, len(idx), False)], 0)


def makegenquad(name, palettetex, x, z, incx, incz, heights, texs, roof):
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
                  None, [], [], [], [], vt, idx,
                  [([(1,1,1),(0,0,0),(0,0,0),0.5], 0, len(idx), False)], 0)


def makegenmulti(name, palettetex, sides, x, z, heights, texs):
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
                  None, [], [], [], [], vt, idx,
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

        
# read EZ-Scenery UID mappings
# EZ-Scenery: http://www.simforums.com/forums/forum_posts.asp?TID=21569
# SBuilder: http://www.fsdeveloper.com/forum/showpost.php?p=49183&postcount=2
def friendlytxt(filename, friendly, names):
    try:
        h=codecs.open(filename, 'rU', 'latin1')
        for line in h:
            line=line.strip()
            if not line or line[0] in [';', '#']:
                continue
            uid=line.split()[0].lower()
            if len(uid)!=32 or not isalnum(uid):
                continue
            name=asciify(line[33:].strip())
            if not name in names:
                friendly[uid]=name
                name[names]=True
        h.close()
    except:
        pass


# read Rwy12 UID mappings
class friendlyxml:

    def __init__(self, filename, friendly, names):
        self.friendly=friendly
        self.names=names
        h=file(filename, 'rU')
        try:
            parser=xml.parsers.expat.ParserCreate()
            parser.StartElementHandler = self.start_element
            parser.ParseFile(h)
        except:
            pass
        h.close()

    def start_element(self, name, attrs):
        if name=='obj' and attrs['guid'] and attrs['name']:
            name=asciify(attrs['name'])
            if not name in self.names:
                self.friendly[str(attrs['guid']).lower()]=name
                self.name[names]=True

