from math import sin, cos
from os import unlink
from os.path import exists, join
from StringIO import StringIO
import struct
from struct import pack, unpack
from sys import maxint
from tempfile import gettempdir
import xml.parsers.expat

import convbgl
from convutil import d2r, r2d, m2f, NM2m, complexity, AptNav, Object, Point, Matrix
from convobjs import makeapronlight, maketaxilight, maketaxisign


apronlightspacing=60.96	# [m] = 200ft
taxilightspacing=30.48	# [m] = 100ft


# member var is defined
def D(c, v):
    return (v in dir(c) and eval("c.%s" % v))

# member var is defined and true
def T(c, v):
    return (v in dir(c) and eval("c.%s" % v)=='TRUE')

# Runway & taxiway (but not helipad) surfaces
surfaces={'ASPHALT':1, 'BITUMINOUS':1, 'MACADAM':1,
          'OIL_TREATED':1, 'TARMAC':1, 
          'BRICK':2, 'CEMENT':2, 'CONCRETE':2, 'STEEL_MATS':2,
          'GRASS':3,
          'DIRT':4, 'SAND':4, 'SHALE':4, 'UNKNOWN':4,
          'CORAL':5, 'GRAVEL':5,
          'CLAY':12, 'PLANKS':12,
          'ICE':13, 'SNOW':13, 'WATER':13}

# Set up XML parser for new-style scenery

class SceneryObject:
    def __init__(self, attrs):
        for k, v in attrs.iteritems():
            exec("self.%s=v" % k)
        self.biasxyz=[]
        self.genericbuilding=[]
        self.libraryobject=[]
        self.windsock=[]
        self.beacon=[]
    
    class BiasXYZ:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class GenericBuilding:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)
            self.multisidedbuilding=[]
            self.pyriamidalbuilding=[]
            self.rectangularbuilding=[]

        class MultiSidedBuilding:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)

        class PyramidalBuilding:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)

        class RectangularBuilding:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)

    class LibraryObject:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class Windsock:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class Beacon:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    def export(self, output):
        loc=Point(float(self.lat), float(self.lon))
        alt=float(self.alt)
        pitch=0
        bank=0
        heading=0
        cmplx=1
        if D(self, 'pitch'): pitch=float(self.pitch)
        if D(self, 'bank'): bank=float(self.bank)
        if D(self, 'heading'): heading=float(self.heading)
        cmplxm={'VERY_SPARSE':1,'SPARSE':2,'NORMAL':3,'DENSE':4,'VERY_DENSE':5}
        if D(self, 'imageComplexity') and self.imageComplexity in cmplxm:
            cmplx=complexity(cmplxm[self.imageComplexity])
        for bias in self.biasxyz:
            if D(bias, 'biasX') and D(bias, 'biasZ'):
                loc=loc.biased(float(bias.biasX), float(bias.biasZ))
            if D(bias, 'biasY'):
                alt=alt+float(bias.biasY)

        if self.genericbuilding:
            # XXX Implement me!
            output.log('Unsupported generic building at [%10.6f, %11.6f] in %s' % (loc.lat, loc.lon, self.filename))

        for l in self.libraryobject:
            scale=1.0
            if D(l, 'scale'): scale=round(float(l.scale),2)
            if D(self, 'altitudeIsAgl') and not T(self, 'altitudeIsAgl'):
                output.log('Absolute altitude (%sm) for object %s at [%10.6f, %11.6f] in %s' % (round(alt,2), l.name, loc.lat, loc.lon, self.filename))
            elif alt!=0:
                output.log('Non-zero altitude (%sm) for object %s at [%10.6f, %11.6f] in %s' % (round(alt,2), l.name, loc.lat, loc.lon, self.filename))
            if pitch or bank:
                output.log('Non-zero pitch/bank (%s/%s) for object %s at [%10.6f, %11.6f] in %s' % (pitch, bank, l.name, loc.lat, loc.lon, self.filename))
            output.objplc.append((loc, heading, cmplx, l.name.lower(), scale))

        for w in self.windsock:
            lit=0
            if T(w, 'lighted'): lit=1
            output.misc.append((19, loc, lit))
            
        for b in self.beacon:
            if D(b, 'type') and b.type=='MILITARY':
                lit=4
            elif D(b, 'baseType') and b.baseType=='SEA_BASE':
                lit=2
            elif D(b, 'baseType') and b.baseType=='HELIPORT':
                lit=3
            else:	# civilian land airport
                lit=1
            output.misc.append((18, loc, lit))


class ModelData:
    def __init__(self, attrs):
        for k, v in attrs.iteritems():
            exec("self.%s=v" % k)
    
    def export(self, output):
        mdlname=join(gettempdir(), self.sourceFile)
        if int(self.fileOffset):
            output.log("Can't parse object %s in %s" % (
                self.name, self.filename))
            if exists(mdlname): unlink(mdlname)
            return
        
        data=''
        bgldata=''
        tbldata=''
        scen=None
        tran=None
        try:
            mdl=file(mdlname, 'rb')
        except IOError:
            output.log("Can't read object %s in %s" % (
                self.name, self.filename))
            return
        try:
            if mdl.read(4)!='RIFF': raise IOError
            (mdlsize,)=unpack('<I', mdl.read(4))
            if mdl.read(4)!='MDL9': raise IOError
            while mdl.tell()<mdlsize:
                c=mdl.read(4)
                (size,)=unpack('<I', mdl.read(4))
                if c=='EXTE':
                    end=size+mdl.tell()
                    while mdl.tell()<end:
                        c=mdl.read(4)
                        (size,)=unpack('<I', mdl.read(4))
                        if c in ['TEXT','MATE','VERT']:
                            data+=mdl.read(size-2)	# strip return
                            if mdl.read(2)!='\x22\0':	raise IOError
                        elif c=='BGL ':
                            bgldata+=mdl.read(size)
                            bgldata+='\0\0'		# add EOF
                        elif c in ['TRAN', 'ANIP', 'ANIC', 'SCEN']:
                            # Need to maintain offsets between ANIC and SCEN
                            if c=='TRAN':
                                tran=len(tbldata)+8
                            elif c=='SCEN':
                                scen=len(tbldata)+8
                            tbldata+=pack('<I',size)+c+mdl.read(size)
                        else:
                            mdl.seek(size,1)
                else:
                    mdl.seek(size,1)
            data+=bgldata	# BGL section must be after other instructions
            if scen: scen+=len(data)	# Offset from first instruction
            if tran: tran+=len(data)	# Offset from first instruction
            data+=tbldata	# Table data must be last so not interpreted
            if not data: raise IOError
        except (IOError, struct.error):
            output.log("Can't parse object %s in %s" % (
                self.name, self.filename))
            mdl.close()
            if exists(mdlname): unlink(mdlname)
            return
        mdl.close()
        unlink(mdlname)

        # Write a bgl library file
        bgl=StringIO()
        for i in range(15):
            bgl.write(pack('<I',0))
        bgl.write(pack('<2H', 0, 0x80))		# offset to section 10
        for i in range(16):
            bgl.write(pack('<I',0))
        # min and max uids should be at 0x56 and 0x5e
        bgl.write(pack('<I',0x18))		# section 10: offset to obj
        for i in range(0,32,8):
            bgl.write(pack('<I', int(self.name[i:i+8],16)))
        bgl.write(pack('<I',0))
        for i in range(0,32,8):
            bgl.write(pack('<I', int(self.name[i:i+8],16)))
        bgl.write(pack('<B',0))			# pwr
        bgl.write(pack('<2I',0x29,len(data)+0x29))	# sizes (no name)
        bgl.write(pack('<4I',1,65536,0x400,0))	# size, scale, type(?), prop
        bgl.write(data)
        bgl.seek(0)

        # XXX Write out for debugging
        #f=file(join(gettempdir(), self.sourceFile[:-4]+'.bgl'), 'wb')
        #f.write(bgl.read())
        #f.close()
        #bgl.seek(0)
        
        convbgl.Parse(bgl, "object %s in %s" % (self.name, self.filename),
                      self.srcfile, output, scen, tran)
        bgl.close()


class ExclusionRectangle:
    def __init__(self, attrs):
        for k, v in attrs.iteritems():
            exec("self.%s=v" % k)
    
    def export(self, output):
        if (T(self, 'excludeAllObjects') or
            T(self, 'excludeGenericBuildingObjects') or
            T(self, 'excludeLibraryObjects')):
            output.exc.append((Point(float(self.latitudeMinimum),
                                     float(self.longitudeMinimum)),
                               Point(float(self.latitudeMaximum),
                                     float(self.longitudeMaximum))))


class Airport:
    def __init__(self, attrs):
        for k, v in attrs.iteritems():
            exec("self.%s=v" % k)
        self.tower=[]
        self.runway=[]
        self.helipad=[]
        self.com=[]
        self.taxiwaypoint=[]
        self.taxiwayparking=[]
        self.taxiwaypath=[]
        self.ndb=[]
        self.taxiwaysign=[]
        self.aprons=[]
        self.apronedgelights=[]
        
    class Tower:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class Com:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class Runway:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)
            self.markings=[]
            self.lights=[]
            self.offsetthreshold=[]
            self.blastpad=[]
            self.overrun=[]
            self.approachlights=[]
            self.vasi=[]
            self.ils=[]

        class Markings:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)
                
        class Lights:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)

        class OffsetThreshold:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)
                
        class BlastPad:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)
                
        class Overrun:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)
                
        class ApproachLights:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)
                
        class Vasi:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)
                
        class Ils:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)
                self.glideslope=[]
                self.dme=[]

            class GlideSlope:
                def __init__(self, attrs):
                    for k, v in attrs.iteritems():
                        exec("self.%s=v" % k)

            class Dme:
                def __init__(self, attrs):
                    for k, v in attrs.iteritems():
                        exec("self.%s=v" % k)
                
    class Helipad:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class TaxiwayPoint:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class TaxiwayParking:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class TaxiwayPath:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class Ndb:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class TaxiwaySign:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class Aprons:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)
            self.apron=[]

        class Apron:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)
                self.vertex=[]

            class Vertex:
                def __init__(self, attrs):
                    for k, v in attrs.iteritems():
                        exec("self.%s=v" % k)

    class ApronEdgeLights:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)
            self.edgelights=[]

        class EdgeLights:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)
                self.vertex=[]

            class Vertex:
                def __init__(self, attrs):
                    for k, v in attrs.iteritems():
                        exec("self.%s=v" % k)

    # Export airport to apt.dat and nav.dat
    def export(self, output):

        airloc=Point(float(self.lat), float(self.lon))

        if output.apt.has_key(self.ident):
            aptdat=output.apt[self.ident]
        else:
            aptdat=[]
            output.apt[self.ident]=aptdat

        # Might just be a placeholder - only create header if it has a name
        if D(self, 'name'):
            txt=("%5d" % (float(self.alt)*m2f))
            if self.tower:
                txt+=" 1"
            else:
                txt+=" 0"
            txt+=(" 0 %s %s" % (self.ident, self.name))
            aptdat.append(AptNav(1, airloc, txt))

        # Runways
        for runway in self.runway:
            # Data in X-Plane apt.dat order (distances in ft)
            loc=Point(float(runway.lat), float(runway.lon))
            number=''
            heading=float(runway.heading)
            length=m2f*float(runway.length)	# including displaced
            displaced=[0,0]
            overrun=[0,0]
            width=m2f*float(runway.width)
            lights=[[1,1,1],[1,1,1]]
            surface=1
            shoulder=0
            markings=0
            smoothing=0.25
            distance=0
            angle=[0,0]

            # X-Plane considers size<10? to be an error.
            if length<10: length=10
            if width<10: width=10

            nos={'EAST':9, 'NORTH':0, 'NORTHEAST':4, 'NORTHWEST':31,
                 'SOUTH':18, 'SOUTHEAST':13, 'SOUTHWEST':22, 'WEST':27}
            if nos.has_key(runway.number):
                number=("%02d" % nos[runway.number])
            else:
                number=("%02d" % int(runway.number))
            if D(runway, 'designator'):
                des={'NONE':'', 'C':'C', 'CENTER':'C', 'L':'L', 'LEFT':'L',
                     'R':'R', 'RIGHT':'R', 'W':'', 'WATER':''}
                number+=des[runway.designator]

            for off in runway.offsetthreshold:
                if off.end=='PRIMARY':
                    end=0
                else:
                    end=1
                displaced[end]=m2f*float(off.length)

            for bp in runway.blastpad:
                if bp.end=='PRIMARY':
                    end=0
                else:
                    end=1
                overrun[end]=m2f*float(bp.length)

            surface=surfaces[runway.surface]
            
            for vasi in runway.vasi:
                vasis={'PVASI':2, 'TRICOLOR':2, 'TVASI':2, 
                       'VASI21':2, 'VASI22':2, 'VASI23':2, 'VASI31':2, 
                       'VASI32':2, 'VASI33':2, 'BALL':2, 
                       'PAPI2':3, 'PAPI4':3, 'APAP':3, 'PANELS':3}
                if vasi.end=='PRIMARY':
                    end=0
                else:
                    end=1
                if vasis.has_key(vasi.type):
                    lights[end][0]=vasis[vasi.type]

            for light in runway.lights:
                if D(light, 'edge') and light.edge!='NONE':
                    lights[0][1]=2
                    lights[1][1]=2
                if D(light, 'center') and light.center!='NONE':
                    # Implies Edge and REILS(strobes) in X-Plane
                    lights[0][1]=4
                    lights[1][1]=4
            for app in runway.approachlights:
                sys={'NONE':1,
                     'SALS':2, 'SSALR':2, 'SSALSR':2, 'MALSR':2, 'RAIL':2,
                     'SSALSF':3, 'MALSF':3,
                     'ALSF1':4,
                     'ALSF2':5,
                     'ODALS':6,
                     'CALVERT':7,
                     'CALVERT2':8}
                if app.end=='PRIMARY':
                    end=0
                else:
                    end=1
                if D(app, 'system'):
                    lights[end][2]=sys[app.system]
                if (D(app, 'strobes') and int(app.strobes)>0 and
                    lights[end][1]<3):
                    lights[end][1]=3
                if T(app, 'touchdown'):
                    lights[end][1]=5

            for m in runway.markings:
                # Hack! Distance markings also add taxiwaysigns in X-Plane
                #if T(m, 'fixedDistance') and not self.taxiwaysign:
                #    distance=1
                if T(m, 'edgePavement') and surface<=2:
                    shoulder=surface	# asphalt or concrete
                if not surface in [6,7,8,9,13]:	# helipads or water
                    # Not sure about these
                    if T(m, 'edges') or T(m, 'dashes') or T(m, 'ident'):
                        markings=1
                    if (T(m, 'threshold') or T(m, 'fixedDistance') or
                        T(m, 'touchdown')):
                        markings=2
                    if T(m, 'precision'):
                        markings=3

            for ils in runway.ils:
                if ils.end=='PRIMARY':
                    end=0
                else:
                    end=1
                if D(ils, 'name'):
                    name=("%s %s" % (self.ident, ils.name))
                else:
                    name=('%s %s ILS' % (self.ident, number))
                if D(ils, 'range'):
                    rng=float(ils.range)/NM2m
                else:
                    rng=18
                output.nav.append(AptNav(4, Point(float(ils.lat),
                                                  float(ils.lon)),
                                         "%6d %05d %3d %11.3f %-5s %s" % (
                    m2f*float(ils.alt), float(ils.frequency)*100, rng,
                    float(ils.heading), ils.ident, name)))
                
                for gs in ils.glideslope:
                    angle[end]=float(gs.pitch)
                    if D(ils, 'name'):
                        name=("%s %s" % (self.ident, ils.name))
                    else:
                        name=('%s %s GS' % (self.ident, number))
                    if D(gs, 'range'):
                        rng=float(gs.range)/NM2m
                    else:
                        rng=10
                    output.nav.append(AptNav(6, Point(float(gs.lat),
                                                      float(gs.lon)),
                                             "%6d %05d %3d %11.3f %-5s %s" % (
                        m2f*float(gs.alt), float(ils.frequency)*100, rng,
                        float(ils.heading)+100000*round(float(gs.pitch),2),
                        '---', name)))

                for dme in ils.dme:
                    if D(ils, 'name'):
                        name=("%s %s" % (self.ident, ils.name))
                    else:
                        name=('%s %s DME-ILS' % (self.ident, number))
                    if D(dme, 'range'):
                        rng=float(dme.range)/NM2m
                    else:
                        rng=18
                    output.nav.append(AptNav(12, Point(float(dme.lat),
                                                       float(dme.lon)),
                                             "%6d %05d %3d %11.3f %-5s %s" % (
                        
                        m2f*float(dme.alt), float(ils.frequency)*100, rng,
                        0, ils.ident, name)))
                    
            if len(number)<3: number+='x'
            for a in aptdat:
                if a.code==10 and a.text[0:3]==number:
                    output.fatal('Found duplicate definition of runway %s in %s' % (number.replace('x',''), self.filename))
            aptdat.append(AptNav(10, loc, "%s %6.2f %6d %04d.%04d %04d.%04d %4d %d%d%d%d%d%d %02d %d %d %4.2f %d %04d.%04d" % (
                number, heading, length,
                displaced[0], displaced[1], overrun[0], overrun[1], width,
                lights[0][0], lights[0][1], lights[0][2],
                lights[1][0], lights[1][1], lights[1][2],
                surface, shoulder, markings, smoothing, distance,
                angle[0]*100, angle[1]*100)))

        # Helipads
        hno=0
        for h in self.helipad:
            loc=Point(float(h.lat), float(h.lon))
            heading=float(h.heading)
            length=m2f*float(h.length)	# including displaced
            width=m2f*float(h.width)
            helisur={'ASPHALT':6, 'BITUMINOUS':6, 'MACADAM':6,
                     'OIL_TREATED':6, 'TARMAC':6,
                     'BRICK':7, 'CEMENT':7, 'CONCRETE':7, 'STEEL_MATS':7,
                     'GRASS':8,
                     'DIRT':9, 'SAND':9, 'SHALE':9, 'UNKNOWN':9,
                     'CORAL':9, 'GRAVEL':9,
                     'CLAY':9, 'PLANKS':9,
                     'ICE':7, 'SNOW':7, 'WATER':7}
            surface=helisur[h.surface]
            hno+=1
            if hno<9:
                number=("H%dx" % hno)
            else:
                number=("H%d" % hno)
            for a in aptdat:
                if a.code==10 and a.text[0:3]==number:
                    output.fatal('Found duplicate definition of helipad %s in %s' % (number.replace('x',''), self.filename))
            aptdat.append(AptNav(10, loc, "%s %6.2f %6d %04d.%04d %04d.%04d %4d 111111 %02d %d %d %4.2f %d %04d.%04d" % (
                number, heading, length, 0, 0, 0, 0, width,
                surface, 0, 0, 0.25, 0, 0, 0)))

        # Taxiways - build array for easier access
        nodes = [None for i in range(len(self.taxiwaypoint)+
                                     len(self.taxiwayparking))]
        for t in self.taxiwayparking:
            nodes[int(t.index)]=t
        for t in self.taxiwaypoint:
            nodes[int(t.index)]=t
        holdshorts=[]

        obj=maketaxilight()
        fname=obj.filename[:-4]
        for t in self.taxiwaypath:
            if (t.type=='TAXI' and
                ((not D(t, 'drawSurface')) or T(t, 'drawSurface'))):
                snode=nodes[int(t.start)]
                enode=nodes[int(t.end)]
                start=Point(float(snode.lat),
                            float(snode.lon))
                end=Point(float(enode.lat),
                          float(enode.lon))
                loc=Point((start.lat+end.lat)/2, (start.lon+end.lon)/2)
                heading=start.headingto(end)
                width=m2f*float(t.width)
                length=0.5*width + m2f*start.distanceto(end)
                surface=surfaces[t.surface]
                
                # X-Plane considers size<1 to be an error. So skip placeholders
                if length<1 or width<1:
                    continue
                dupl=False
                for a in aptdat:
                    if a.code==10 and loc.lat==a.loc.lat and loc.lon==a.loc.lon:
                        output.log('Skipping duplicate of taxiway at [%10.6f, %11.6f] in %s' % (loc.lat, loc.lon, self.filename))
                        dupl=True
                        break
                if dupl:
                    continue

                if T(t, 'leftEdgeLighted') or T(t, 'rightEdgeLighted'):
                    lights=6
                else:
                    lights=1
                # XXX can't get hold points to work
                if (0 and snode.type=='HOLD_SHORT' and
                    surface in [1,2] and not snode in holdshorts):
                    surface+=9
                    if D(snode,'orientation') and snode.orientation=='REVERSE':
                        heading=(heading+180) % 360.0
                aptdat.append(AptNav(10, loc, "%s %6.2f %6d %04d.%04d %04d.%04d %4d 1%d11%d1 %02d %d %d %4.2f %d %04d.%04d" % (
                    'xxx', heading, length, 0, 0, 0, 0, width,
                    lights, lights, surface, 0, 0, 0.25, 0, 0, 0)))

                l=start.distanceto(end)-taxilightspacing/2
                if T(t, 'centerLineLighted') and l>0:
                    output.objdat[fname]=[obj]
                    h=start.headingto(end)*d2r
                    n=1+int(l/taxilightspacing)
                    for j in range(n):
                        l=(j+0.5)*taxilightspacing
                        loc=start.biased(-sin(h)*l*j,cos(h)*l*j)
                        output.objplc.append((loc, 0, 1, fname, 1))


        # Aprons
        # Just do bounding box aligned with main (first) runway
        if self.runway:
            heading=float(self.runway[0].heading)%180
            rot=Matrix().headed(-heading)
            back=Matrix().headed(heading)
        else:
            heading=0
        for a in self.aprons:
            for apron in a.apron:
                if (not D(apron, 'drawSurface')) or T(apron, 'drawSurface'):
                    surface=surfaces[apron.surface]
                    minx=minz=maxint
                    maxx=maxz=-maxint
                    for v in apron.vertex:
                        if D(v, 'lat') and D(v, 'lon'):
                            loc=Point(float(v.lat), float(v.lon))
                            z=airloc.distanceto(loc)
                            (x,y,z)=Matrix().headed(airloc.headingto(
                                loc)).transform(0,0,z)
                        elif D(v, 'biasX') and D(v, 'biasZ'):
                            x=float(v.biasX)
                            z=float(v.biasZ)
                        else:
                            continue
                        # Rotate to be in line with runway
                        if heading:
                            (x,y,z)=rot.transform(x,0,z)
                        minx=min(minx,x)
                        maxx=max(maxx,x)
                        minz=min(minz,z)
                        maxz=max(maxz,z)
                    width =m2f*(maxx-minx)
                    length=m2f*(maxz-minz)
                    if heading:
                        (x,y,z)=back.transform((maxx+minx)/2,0,(maxz+minz)/2)
                        loc=airloc.biased(x,z)
                    else:
                        loc=airloc.biased((maxx+minx)/2, (maxz+minz)/2)
                    dupl=False
                    for a in aptdat:
                        if a.code==10 and loc.lat==a.loc.lat and loc.lon==a.loc.lon:
                            output.log('Skipping duplicate of apron at [%10.6f, %11.6f] in %s' % (loc.lat, loc.lon, self.filename))
                            dupl=True
                            break
                    if dupl:
                        continue
                    aptdat.append(AptNav(10, loc, "%s %6.2f %6d %04d.%04d %04d.%04d %4d 111111 %02d %d %d %4.2f %d %04d.%04d" % (
                        'xxx', heading, length, 0, 0, 0, 0, width,
                        surface, 0, 0, 0.25, 0, 0, 0)))

        # ApronEdgeLights
        for a in self.apronedgelights:
            for e in a.edgelights:
                v=e.vertex
                obj=makeapronlight()
                fname=obj.filename[:-4]
                if len(v)>1:
                    for i in range(len(v)-1):
                        start=Point(float(v[i].lat), float(v[i].lon))
                        end=Point(float(v[i+1].lat), float(v[i+1].lon))
                        l=start.distanceto(end)
                        n=1+int(l/apronlightspacing)
                        (x,y,z)=Matrix().headed(
                            start.headingto(end)).transform(0,0,l/n)
                        for j in range(n):
                            loc=start.biased(x*j,z*j)
                            output.objplc.append((loc, 0, 1, fname, 1))
                # Last one
                if len(v):
                    output.objdat[fname]=[obj]
                    output.objplc.append((Point(float(v[-1].lat),
                                                float(v[-1].lon)),
                                          0, 1, fname, 1))

        # Tower view location
        if D(self, 'name'):
            view=self.name+' Tower'
        else:
            view='Tower Viewpoint'
        for tower in self.tower:
            aptdat.append(AptNav(14, Point(float(tower.lat),float(tower.lon)),
                                 "%6.2f 0 %s" % (
                (float(tower.alt)-float(self.alt))*m2f, view)))

        # Ramp startup positions
        for t in self.taxiwayparking:
            if D(t, 'lat') and D(t, 'lon'):
                loc=Point(float(t.lat), float(t.lon))
            elif D(t, 'biasX') and D(t, 'biasZ'):
                loc=airloc.biased(float(t.biasX), float(t.biasZ))
            else:
                continue
            # type appears secondary to name
            parking={'E_PARKING':'East ',
                     'NE_PARKING':'North East ',
                     'N_PARKING':'North ',
                     'NW_PARKING':'North West ',
                     'SE_PARKING':'South East ',
                     'S_PARKING':'South ',
                     'SW_PARKING':'South West ',
                     'W_PARKING':'West ',
                     'PARKING':''}
            types={'RAMP_CARGO':'Cargo ',
                   'RAMP_GA':'GA ',
                   'RAMP_GA_LARGE':'GA ',
                   'RAMP_GA_MEDIUM':'GA ',
                   'RAMP_GA_SMALL':'GA ',
                   'RAMP_MIL_CARGO':'Mil cargo ',
                   'RAMP_MIL_COMBAT':'Military '}
            if t.name in ['GATE_A', 'GATE_B', 'GATE_C', 'GATE_D', 'GATE_E',
                          'GATE_F', 'GATE_G', 'GATE_H', 'GATE_I', 'GATE_J',
                          'GATE_K', 'GATE_L', 'GATE_M', 'GATE_N', 'GATE_O',
                          'GATE_P', 'GATE_Q', 'GATE_R', 'GATE_S', 'GATE_T',
                          'GATE_U', 'GATE_V', 'GATE_W', 'GATE_X', 'GATE_Y',
                          'GATE_Z']:
                name='Gate '+t.name[5]
            elif t.name=='GATE':
                name='Gate'
            elif t.name=='DOCK':
                name='Dock'
            elif t.name in parking:
                name=parking[t.name]
                if t.type in types:
                    name+=types[t.type]
                name+='Ramp'

            # No name
            elif t.type in ['GATE', 'GATE_HEAVY', 'GATE_MEDIUM', 'GATE_SMALL']:
                name='Gate'
            elif t.type=='DOC_GA':
                name='Dock'
            elif t.type in types:
                name=types[t.type]+' Ramp'

            # wtf
            else:
                name='Ramp'
                
            if int(t.number):
                name=name+(" %d" % int(t.number))
            aptdat.append(AptNav(15, loc, "%6.2f %s" % (
                float(t.heading), name)))
        
        # ATC
        codes={'AWOS':50, 'ASOS':50, 'ATIS':50, 'FSS':50,
               'UNICOM':51, 'MULTICOM':51, 'CTAF':51,
               'CLEARANCE':52,
               'GROUND':53,
               'TOWER':54, 'CENTER':54,
               'APPROACH':55,
               'DEPARTURE':56}
        abbrv={'CLEARANCE':'CLNC',
               'GROUND':'GND',
               'TOWER':'TWR',
               'CENTER':'CTR',
               'APPROACH':'APP',
               'DEPARTURE':'DEP'}
        for com in self.com:
            if abbrv.has_key(com.type):
                type=abbrv[com.type]
            else:
                type=com.type
            aptdat.append(AptNav(codes[com.type], None, "%5d %s %s" % (
                float(com.frequency)*100, com.name, type)))

        for n in self.ndb:
            # Call top-level Ndb class
            attrs={}
            for k in dir(n):
                if k[:1]!='_':
                    attrs[k]=eval('n.'+k)
            ndb=Ndb(attrs)
            ndb.export(output)

        for t in self.taxiwaysign:
            loc=Point(float(t.lat), float(t.lon))
            heading=float(t.heading)
            scale=1
            # Sizes are a guess. What does justification do?
            smap={'SIZE1':0.67,'SIZE2':0.8,'SIZE3':1,'SIZE4':1.25,'SIZE5':1.5}
            if D(t, 'size') and t.size in smap:
                scale=smap[t.size]
            obj=maketaxisign(t.label)
            output.objdat[obj.filename[:-4]]=[obj]
            output.objplc.append((loc, heading, 0, obj.filename[:-4], scale))


class Vor:
    def __init__(self, attrs):
        for k, v in attrs.iteritems():
            exec("self.%s=v" % k)
        self.dme=[]

    class Dme:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    # Export to nav.dat
    def export(self, output):
        if self.dme:
            type='VOR'
        else:
            type='VOR-DME'
        if D(self, 'name'):
            name=self.name
            if name[-3:].upper()!=type: name+=(' '+type)
        else:
            name=self.ident+' '+type
        if D(self, 'range'):
            rng=float(self.range)/NM2m
        elif self.type in ['VOT', 'TERMINAL']:
            rng=25
        elif self.type=='HIGH':
            rng=100
        else: # 'LOW'
            rng=40
        if (not D(self, 'nav') or T(self, 'nav')) and not T(self, 'dmeOnly'):
            output.nav.append(AptNav(3, Point(float(self.lat),float(self.lon)),
                                     "%6d %05d %3d %11.3f %-5s %s" % (
                m2f*float(self.alt), float(self.frequency)*100, rng,
                0, self.ident, name)))

        for dme in self.dme:
            if D(self, 'range'):
                rng=float(dme.range)/NM2m
            output.nav.append(AptNav(12, Point(float(dme.lat),float(dme.lon)),
                                     "%6d %05d %3d %11.3f %-5s %s" % (
                m2f*float(dme.alt), float(self.frequency)*100, rng,
                0, self.ident, name)))
           

class Ndb:
    def __init__(self, attrs):
        for k, v in attrs.iteritems():
            exec("self.%s=v" % k)

    # Export to nav.dat
    def export(self, output):
        if D(self, 'name'):
            name=self.name
            if name[-3:].upper()!='NDB': name+=' NDB'
        else:
            name=self.ident+' NDB'
        if D(self, 'range'):
            rng=float(self.range)/NM2m
        elif self.type=='COMPASS_POINT':
            rng=15
        elif self.type=='MH':
            rng=25
        elif self.type=='HH':
            rng=75
        else:	   # 'H'
            rng=50
        output.nav.append(AptNav(2, Point(float(self.lat), float(self.lon)),
                                 "%6d %-5d %3d %11.3f %-5s %s" % (
            m2f*float(self.alt), float(self.frequency), rng,
            0, self.ident, name)))
        

class Marker:
    def __init__(self, attrs):
        for k, v in attrs.iteritems():
            exec("self.%s=v" % k)

    # Export to nav.dat
    def export(self, output):
        if self.type=='INNER':
            type='IM'
            code=9
        elif self.type=='MIDDLE':
            type='MM'
            code=8
        elif self.type=='OUTER':
            type='OM'
            code=7
        else:	# 'BACKCOURSE'
            return
        if D(self, 'name'):
            name=self.name
            if name[-3:].upper()!=type: name+=(' '+type)
        else:
            name=self.ident+' '+type
        output.nav.append(AptNav(code, Point(float(self.lat),float(self.lon)),
                                 "%6d %05d %3d %11.3f %-5s %s" % (
            m2f*float(self.alt), 0, 0,
            float(self.heading), '---', name)))


class Parse:
    def __init__(self, fd, name, srcfile, output, scen, tran):
        self.name=name
        self.srcfile=srcfile
        self.elems=[]
        self.parents=[]
        self.parname=''	# parent class(es)
        self.output=output

        parser=xml.parsers.expat.ParserCreate()
        parser.StartElementHandler = self.start_element
        parser.EndElementHandler = self.end_element
        parser.ParseFile(fd)
        fd.close()

        # Parsed OK. Now export
        for elem in self.elems:
            elem.export(self.output)

    def start_element(self, name, attrs):
        try:
            attrs['filename']=self.name
            attrs['srcfile']=self.srcfile
            elem=eval('%s%s(attrs)' % (self.parname, name))
        except (NameError, AttributeError):
            return
        if self.parents:
            exec("self.parents[-1].%s.append(elem)" % name.lower())
        else:
            self.elems.append(elem)
        self.parents.append(elem)
        self.parname+=(name+'.')
            
    def end_element(self, name):
        if self.parname[-(len(name)+1):-1]==name:
            self.parents.pop()
            self.parname=self.parname[:-(len(name)+1)]

