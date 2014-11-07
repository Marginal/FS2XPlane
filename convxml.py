from math import sin, cos, atan, radians
from os import unlink
from os.path import basename, exists, join
from sys import maxint
import xml.parsers.expat
from tempfile import gettempdir

from convutil import m2f, NM2m, complexity, asciify, AptNav, Object, Point, Matrix, FS2XError, D, T, E
from convobjs import makegenquad, makegenmulti
from convtaxi import apronlayout, designators, surfaces, taxilayout, Node, Link
from convatc  import atclayout


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
        self.attachedobject=[]

    class BiasXYZ:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class GenericBuilding:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)
            self.multisidedbuilding=[]
            self.pyramidalbuilding=[]
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

    class AttachedObject:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)
            self.beacon=[]

        class Beacon:
            def __init__(self, attrs):
                for k, v in attrs.iteritems():
                    exec("self.%s=v" % k)


    def export(self, parser, output, aptdat=None):
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
                alt += float(bias.biasY)

        # Unattached beacon
        for b in self.beacon:
            if E(b, 'baseType', 'SEA_BASE'):
                lit=2
            elif E(b, 'baseType', 'HELIPORT'):
                lit=3
            elif E(b, 'type', 'MILITARY'):
                lit=4
            else:	# civilian land airport
                lit=1
            a=AptNav(18, '%12.8f %13.8f %d Beacon' % (loc.lat, loc.lon, lit))
            if aptdat:
                aptdat.append(a)
            else:
                output.misc.append((18, loc, [a]))

        for w in self.windsock:
            lit=0
            if T(w, 'lighted'): lit=1
            a=AptNav(19, '%12.8f %13.8f %d Windsock' %(loc.lat, loc.lon, lit))
            if aptdat:
                aptdat.append(a)
            else:
                output.misc.append((19, loc, [a]))

        # Don't add placements if we're doing a second round of apt.dat
        if output.doingexcfac: return
        
        for l in self.genericbuilding:
            scale=1.0
            if D(l, 'scale'): scale=round(float(l.scale),2)
            if D(self, 'altitudeIsAgl') and not T(self, 'altitudeIsAgl'):
                output.log('Absolute altitude (%sm) for generic building at (%12.8f, %13.8f) in file %s' % (round(alt,2), loc.lat, loc.lon, parser.filename))
            elif abs(alt)>0.1:
                output.log('Non-zero altitude (%sm) for generic building at (%12.8f, %13.8f) in file %s' % (round(alt,2), loc.lat, loc.lon, parser.filename))
            if pitch or bank:
                output.log('Non-zero pitch/bank (%s/%s) for generic building at (%12.8f, %13.8f) in file %s' % (pitch, bank, loc.lat, loc.lon, parser.filename))
            texs=(int(l.bottomTexture), int(l.windowTexture),
                  int(l.topTexture), int(l.roofTexture))

            for m in l.multisidedbuilding:
                key=(int(m.buildingSides),
                     scale*float(m.sizeX), scale*float(m.sizeZ),
                     (scale*float(m.sizeBottomY),
                      scale*float(m.sizeWindowY),
                      scale*float(m.sizeTopY),
                      scale*float(m.sizeRoofY)),
                     texs)
                if key in parser.genmulticache:
                    name=parser.genmulticache[key]
                else:
                    parser.gencount += 1
                    name="%s-generic-%d" % (asciify(parser.filename[:-4]), parser.gencount)
                    obj=makegenmulti(name, output, *key)
                    parser.genmulticache[key]=name
                    output.objdat[name]=[obj]
                output.objplc.append((loc, heading, cmplx, name, 1))
                                
            for m in l.pyramidalbuilding:
                h2=2*(float(m.sizeBottomY)+float(m.sizeWindowY)+
                      float(m.sizeTopY))
                key=(scale*float(m.sizeX), scale*float(m.sizeZ),
                     atan((float(m.sizeX)-float(m.sizeTopX))/h2),
                     atan((float(m.sizeZ)-float(m.sizeTopZ))/h2),
                     (scale*float(m.sizeBottomY),
                      scale*float(m.sizeWindowY),
                      scale*float(m.sizeTopY)),
                     texs, 0)
                if key in parser.genquadcache:
                    name=parser.genquadcache[key]
                else:
                    parser.gencount += 1
                    name="%s-generic-%d" % (asciify(parser.filename[:-4]), parser.gencount)
                    obj=makegenquad(name, output, *key)
                    parser.genquadcache[key]=name
                    output.objdat[name]=[obj]
                output.objplc.append((loc, heading, cmplx, name, 1))
            for m in l.rectangularbuilding:
                heights=[scale*float(m.sizeBottomY),
                         scale*float(m.sizeWindowY),
                         scale*float(m.sizeTopY)]
                rtexs=list(texs)
                roof=0
                if m.roofType=="FLAT":
                    roof=0
                elif m.roofType=="PEAKED":
                    roof=1
                    heights.append(scale*float(m.sizeRoofY))
                elif m.roofType=="RIDGE":
                    roof=2
                    heights.append(scale*float(m.sizeRoofY))
                    rtexs.append(int(m.gableTexture))
                elif m.roofType=="SLANT":
                    roof=3
                    heights.append(scale*float(m.sizeRoofY))
                    rtexs.extend([int(m.gableTexture), int(m.faceTexture)])
                else:
                    continue
                key=(scale*float(m.sizeX), scale*float(m.sizeZ),
                     0, 0, tuple(heights), tuple(rtexs), roof)
                if key in parser.genquadcache:
                    name=parser.genquadcache[key]
                else:
                    parser.gencount += 1
                    name="%s-generic-%d" % (asciify(parser.filename[:-4]), parser.gencount)
                    obj=makegenquad(name, output, *key)
                    parser.genquadcache[key]=name
                    output.objdat[name]=[obj]
                output.objplc.append((loc, heading, cmplx, name, 1))
                
        for l in self.libraryobject:
            scale=1.0
            if D(l, 'scale'): scale=round(float(l.scale),2)
            name=l.name.lower()
            if name in output.friendly:
                friendly=output.friendly[name]
            elif name in output.stock:
                friendly=output.stock[name]
            else:
                friendly=name
            if friendly in output.subst:
                (name, biasX, biasZ, biasH)=output.subst[friendly]
                h1=radians(heading)
                loc=loc.biased(cos(h1)*biasX+sin(h1)*biasZ,
                               cos(h1)*biasZ-sin(h1)*biasX)
                heading=(heading+biasH)%360

            # Attached beacon
            for a in self.attachedobject:
                for b in a.beacon:
                    if E(b, 'baseType', 'SEA_BASE'):
                        lit=2
                    elif E(b, 'baseType', 'HELIPORT'):
                        lit=3
                    elif E(b, 'type', 'MILITARY'):
                        lit=4
                    else:	# civilian land airport
                        lit=1
                    a=AptNav(18, '%12.8f %13.8f %d Beacon' % (loc.lat, loc.lon, lit))
                    if aptdat:
                        aptdat.append(a)
                    else:
                        output.misc.append((18, loc, [a]))

            if D(self, 'altitudeIsAgl') and not T(self, 'altitudeIsAgl'):
                output.log('Absolute altitude (%sm) for object %s at (%12.8f, %13.8f) in file %s' % (round(alt,2), friendly, loc.lat, loc.lon, parser.filename))
            elif abs(alt)>0.1:
                output.log('Non-zero altitude (%sm) for object %s at (%12.8f, %13.8f) in file %s' % (round(alt,2), friendly, loc.lat, loc.lon, parser.filename))
            if pitch or bank:
                output.log('Non-zero pitch/bank (%s/%s) for object %s at (%12.8f, %13.8f) in file %s' % (pitch, bank, friendly, loc.lat, loc.lon, parser.filename))
            output.objplc.append((loc, heading, cmplx, name, scale))


class ExclusionRectangle:
    def __init__(self, attrs):
        for k, v in attrs.iteritems():
            exec("self.%s=v" % k)
    
    def export(self, parser, output):
        bl=Point(float(self.latitudeMinimum), float(self.longitudeMinimum))
        tr=Point(float(self.latitudeMaximum), float(self.longitudeMaximum))
        if (T(self, 'excludeAllObjects') or
            T(self, 'excludeGenericBuildingObjects') or
            T(self, 'excludeLibraryObjects')):
            output.exc.append(('obj', bl, tr))


class Ndb:
    def __init__(self, attrs):
        for k, v in attrs.iteritems():
            exec("self.%s=v" % k)

    # Export to nav.dat
    def export(self, parser, output):
        if D(self, 'name'):
            name=asciify(self.name, False)
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
        output.nav.append(AptNav(2, "%12.8f %13.8f %6d %-5d %3d %11.3f %-5s %s" % (
            float(self.lat), float(self.lon),
            m2f*float(self.alt), float(self.frequency), rng,
            0, self.ident, name)))
        

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
        self.taxiname=[]
        self.ndb=[]
        self.taxiwaysign=[]
        self.aprons=[]
        self.apronedgelights=[]
        self.boundaryfence=[]

    class Tower:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)
            self.sceneryobject=[]

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
            self.numbers=['XXX','XXX']

            nos={'EAST':9, 'NORTH':36, 'NORTHEAST':4, 'NORTHWEST':31,
                 'SOUTH':18, 'SOUTHEAST':13, 'SOUTHWEST':22, 'WEST':27}
            opp={'C':'C', 'CENTER':'C', 'L':'R', 'LEFT':'R', 'R':'L', 'RIGHT':'L'}
            if nos.has_key(self.number):
                self.numbers[0]=("%02d" % nos[self.number])
                self.numbers[1]=("%02d" % ((18+nos[self.number])%36))
            else:
                self.numbers[0]=("%02d" % int(self.number))
                self.numbers[1]=("%02d" % ((18+int(self.number))%36))
            if self.numbers[0]=='00': self.numbers[0]='36'
            if self.numbers[1]=='00': self.numbers[1]='36'
            if D(self, 'designator'):
                if self.designator in designators:
                    self.numbers[0]+=designators[self.designator]
                    self.numbers[1]+=opp[self.designator]
            else:
                if D(self, 'primaryDesignator') and self.primaryDesignator in designators:
                    self.numbers[0]+=designators[self.primaryDesignator]
                if D(self, 'secondaryDesignator') and self.secondaryDesignator in designators:
                    self.numbers[1]+=designators[self.secondaryDesignator]

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

    class TaxiName:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)

    class Ndb(Ndb):
        pass

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

    # XXX TODO: BoundaryFence
    #class BoundaryFence:
    #    def __init__(self, attrs):
    #        for k, v in attrs.iteritems():
    #            exec("self.%s=v" % k)
    #        self.vertex=[]
    #
    #    class Vertex:
    #        def __init__(self, attrs):
    #            for k, v in attrs.iteritems():
    #                exec("self.%s=v" % k)


    # Export airport to apt.dat and nav.dat
    def export(self, parser, output):

        airloc=Point(float(self.lat), float(self.lon))
        ident=self.ident
        if len(self.ident)>4:
            if ident[:4] not in output.apt:
                ident=ident[:4]
            else:
                ident=ident[:3]+ident[-1]
            output.log('Shortened ICAO airport code from "%s" to "%s"' % (
                self.ident, ident))
            
        if ident not in output.apt:
            output.apt[ident]=(airloc,[])
        elif self.runway or self.helipad or self.taxiwaypoint:
            # Duplicate
            raise FS2XError('Found duplicate definition of airport %s in file %s' % (self.ident, parser.filename))

        aptdat=output.apt[ident][1]

        # X-Plane 10 ATC expects every airport with ATC to have a tower frequency
        atc=[]
        havetwr=True
        for com in self.com:
            if com.type=='TOWER':
                break
        else:
            # promote ground to tower if tower is missing
            for com in self.com:
                if com.type=='GROUND':
                    com.type='TOWER'
                    break
            else:
                havetwr=False
        if havetwr:
            for com in self.com:
                name=asciify(com.name, False)
                if com.type in ['CLEARANCE', 'CLEARANCE_PRE_TAXI']:
                    if not (name, 'del', com.frequency) in atc:
                        atc.append((name, 'del', com.frequency))
                elif com.type=='GROUND':
                    atc.append((name, 'gnd', com.frequency))
                elif com.type=='TOWER':
                    atc.append((name, 'twr', com.frequency))
            if ident in output.atc:
                output.atc[ident].extend(atc)
            else:
                output.atc[ident]=atc

        # Might just be a placeholder - only create header if it has a name
        if D(self, 'name') :
            # airport type may be changed to sea or heli base later on
            aptdat.append(AptNav(1, "%5d %d 0 %s %s" % (
                        float(self.alt)*m2f, havetwr, ident, asciify(self.name, False))))

        # Runways
        for runway in self.runway:
            # Data in X-Plane apt.dat order (distances in ft)
            cloc=Point(float(runway.lat), float(runway.lon))
            heading=float(runway.heading)
            length=float(runway.length)	# includes displaced threshold
            displaced=[0,0]
            overrun=[0,0]
            width=float(runway.width)
            surface=1
            shoulder=0
            smoothing=0.25
            centrelights=0
            edgelights=0
            distance=0
            loc=[None,None]
            angle=[3,3]
            markings=[0,0]
            lights=[0,0]
            tdzl=[0,0]
            reil=[0,0]

            loc[0]=cloc.biased(-sin(radians(heading))*length/2,
                               -cos(radians(heading))*length/2)
            loc[1]=cloc.biased( sin(radians(heading))*length/2,
                                cos(radians(heading))*length/2)

            for off in runway.offsetthreshold:
                if off.end=='PRIMARY':
                    end=0
                else:
                    end=1
                displaced[end]=float(off.length)

            for bp in runway.blastpad + runway.overrun:
                if bp.end=='PRIMARY':
                    end=0
                else:
                    end=1
                overrun[end]+=float(bp.length)

            surface=surfaces[runway.surface]

            for light in runway.lights:
                if not E(light, 'center', 'NONE'):
                    centrelights=1
                if D(light, 'edge'):
                    if light.edge=='NONE':
                        edgelights=0
                    else:
                        edgelights=2
                    if output.xpver>8:
                        if light.edge=='LOW':
                            edgelights=1	# not supported in 8.50
                        elif light.edge=='HIGH':
                            edgelights=3	# not supported in 8.50

            for app in runway.approachlights:
                sys={'ALSF1':1, 'ALSF2':2,
                     'CALVERT':3, 'CALVERT2':4,
                     'MALS':10,
                     'MALSF':9,
                     'MALSR':8,
                     'ODALS':11,
                     'RAIL':12,
                     'SALS':7, 'SSALS':7,
                     'SALSF':6, 'SSALF':6,
                     'SSALR':5, }
                if app.end=='PRIMARY':
                    end=0
                else:
                    end=1
                if D(app, 'system') and app.system in sys:
                    lights[end]=sys[app.system]
                else:
                    lights[end]=0
                #if D(app, 'strobes') and int(app.strobes)>0 and lights[end][1]<3:
                #    lights[end][1]=3
                if T(app, 'reil'):
                    #if edgelights:	# X-Plane draws threshhold lighting
                    #    reil[end]=2	# unidirectional
                    #else:
                    #    reil[end]=1	# omnidirectional
                    reil[end]=1		# omnidirectional
                if T(app, 'touchdown'):
                    tdzl[end]=1

            for m in runway.markings:
                if T(m, 'fixedDistance'):
                    distance=1
                    
                if T(m, 'edgePavement') and surface<=2:
                    shoulder=surface	# asphalt or concrete

                if T(m, 'precision') or T(m, 'touchdown'):
                    if lights[0] in [3,4] or lights[1] in [3,4]:
                        markings[0]=markings[1]=5	# UK
                    else:
                        markings[0]=markings[1]=3
                elif T(m, 'threshold'):			# non-precision
                    if lights[0] in [3,4] or lights[1] in [3,4]:
                        markings[0]=markings[1]=4	# UK
                    else:
                        markings[0]=markings[1]=2
                elif T(m, 'ident') or T(m, 'dashes'):	# visual
                    markings[0]=markings[1]=1
                #elif T(m, 'edges'):	# not supported in 8.50
                #    markings[0]=markings[1]=6		# dashes (grass)
                        
                if T(m, 'singleEnd'): markings[1]=0	# no markings
                if T(m, 'primaryClosed'):		# closed
                    #markings[0]=7	# not supported in 8.50
                    markings[0]=0
                if T(m, 'secondaryClosed'):		# closed
                    #markings[1]=7	# not supported in 8.50
                    markings[0]=0

            for ils in runway.ils:
                if ils.end=='PRIMARY':
                    end=0
                else:
                    end=1
                if D(ils, 'name'):
                    name=("%s %s" % (self.ident, asciify(ils.name, False)))
                else:
                    name=('%s %s ILS' % (self.ident, runways.numbers[end]))
                if D(ils, 'range'):
                    rng=float(ils.range)/NM2m
                else:
                    rng=18
                output.nav.append(AptNav(4, "%12.8f %13.8f %6d %05d %3d %11.3f %-5s %s" % (
                    float(ils.lat), float(ils.lon), m2f*float(ils.alt), float(ils.frequency)*100, rng,
                    float(ils.heading), ils.ident, name)))
                
                for gs in ils.glideslope:
                    angle[end]=float(gs.pitch)
                    if D(ils, 'name'):
                        name=("%s %s" % (self.ident, asciify(ils.name, False)))
                    else:
                        name=('%s %s GS' % (self.ident, runway.numbers[end]))
                    if D(gs, 'range'):
                        rng=float(gs.range)/NM2m
                    else:
                        rng=10
                    output.nav.append(AptNav(6, "%12.8f %13.8f %6d %05d %3d %11.3f %-5s %s" % (
                        float(gs.lat), float(gs.lon), m2f*float(gs.alt), float(ils.frequency)*100, rng,
                        float(ils.heading)+100000*round(float(gs.pitch),2),
                        '---', name)))

                for dme in ils.dme:
                    if D(ils, 'name'):
                        name=("%s %s" % (self.ident, asciify(ils.name, False)))
                    else:
                        name=('%s %s DME-ILS' % (self.ident, runway.numbers[end]))
                    if D(dme, 'range'):
                        rng=float(dme.range)/NM2m
                    else:
                        rng=18
                    output.nav.append(AptNav(12, "%12.8f %13.8f %6d %05d %3d %11.3f %-5s %s" % (
                        
                        float(dme.lat), float(dme.lon), m2f*float(dme.alt), float(ils.frequency)*100, rng,
                        0, ils.ident, name)))

            if length<11 or width<11:
                # X-Plane considers size<1m to be an error. Also some "XWind"
                # hacks for FSX ATC involve creating spurious 10m runways.
                continue
                    
            #if len(number)<3: number+='x'
            # XXX
            #for a in aptdat:
            #    if a.code==100 and a.text[0:3]==number:
            #        raise FS2XError('Found duplicate definition of runway %s in %s' % (number.replace('x',''), parser.filename))

            if runway.surface=='WATER':
                txt="%5.2f %d" %(width, distance or markings[0] or markings[1])
                for end in [0,1]:
                    txt += " %-3s %12.8f %13.8f" % (
                        runway.numbers[end], loc[end].lat, loc[end].lon)
                aptdat.append(AptNav(101, txt))
            else:
                if output.excluded(cloc):
                    # Make X-Plane happy by creating runways
                    surface=15	# transparent
                    shoulder=centrelights=edgelights=distance=markings[0]=markings[1]=tdzl[0]=tdzl[1]=reil[0]=reil[1]=0 #lights[0]=lights[1]
                
                txt="%5.2f %2d %d %4.2f %d %d %d" % (width, surface, shoulder, smoothing, centrelights, edgelights, distance)
                for end in [0,1]:
                    txt += " %-3s %12.8f %13.8f %5.1f %5.1f %d %2d %d %d" % (
                    runway.numbers[end], loc[end].lat, loc[end].lon, displaced[end], overrun[end], markings[end],
                    lights[end], tdzl[end], reil[end])
                aptdat.append(AptNav(100, txt))
                
            # VASIs
            for vasi in runway.vasi:
                if vasi.type=='PAPI4':
                    if vasi.side=='RIGHT':
                        vtype=3
                    else:
                        vtype=2
                elif vasi.type in ['TRICOLOR', 'TVASI']:
                    vtype=5
                else:
                    vtype=1
                vangle=float(vasi.pitch)
                if vasi.end=='PRIMARY':
                    vheading=heading
                    end=0
                else:
                    vheading=(heading+180)%360
                    end=1
                x=float(vasi.biasX)
                z=float(vasi.biasZ)
                # location in MSFS is of rear innermost light
                if vtype==1:
                    z += 75
                    x += 1
                else:
                    x += 12
                if vasi.side=='RIGHT': x=-x
                h=radians(vheading)
                vloc=cloc.biased(-cos(h)*x-sin(h)*z, sin(h)*x-cos(h)*z)
                # was: not output.excluded(vloc), but keep VASI info
                aptdat.append(AptNav(21, '%12.8f %13.8f %d %6.2f %3.1f %s %s' % (
                    vloc.lat, vloc.lon, vtype, vheading, vangle, runway.numbers[end], vasi.type)))

        # Helipads
        hno=0
        for h in self.helipad:
            loc=Point(float(h.lat), float(h.lon))
            heading=float(h.heading)
            length=float(h.length)
            width=float(h.width)
            if h.type=='NONE':
                surface=15	# in 8.50 nothing displayed (no H)
            else:
                surface=surfaces[h.surface]
            markings=0		# in 8.50 yellow circle and H if surface!=15
            if h.type in ['CIRCLE','SQUARE','MEDICAL']:
                lights=1	# yellow: other colours not supported in 8.50
            else:
                lights=0

            # helpad marking and lights codes not supported in 8.50
            #if T(h, 'transparent'):
            #    surface=15	# in 8.50 nothing displayed (no H)
            #else:
            #    surface=surfaces[h.surface]
            #if h.type=='NONE':
            #    markings=10
            #    lights=0
            #elif h.type=='MEDICAL':
            #    markings=12	# not supported in 8.50
            #    lights=3
            #else:
            #    markings=10	# not supported in 8.50
            #    lights=1

            shoulder=0
            smoothing=0.25

            # X-Plane considers size<1m to be an error.
            if length<=1: length=20
            if  width<=1: width =20
            hno+=1

            #for a in aptdat:
            #    if a.code==10 and a.text[0:3]==number:
            #        raise FS2XError('Found duplicate definition of helipad %s in %s' % (number.replace('x',''), parser.filename))
            if output.excluded(loc):
                # Make X-Plane happy by creating runways
                surface=15	# transparent
                markings=shoulder=lights=0
            aptdat.append(AptNav(102, "H%0d %12.8f %13.8f %6.2f %4.2f %4.2f %02d %02d %02d %4.2f %d" % (
                hno, loc.lat, loc.lon, heading, length, width,
                surface, markings, shoulder, smoothing, lights)))

        # Align aprons and taxiway grain with main (first) runway
        if self.runway:
            surfaceheading=float(self.runway[0].heading)%180
        else:
            surfaceheading=0
        
        # Taxiways - build arrays for easier access
        allnodes = [Node(t) for t in self.taxiwaypoint]
        parkingoffset=len(allnodes)
        allnodes.extend([Node(t) for t in self.taxiwayparking])
        alllinks = [Link(p, parkingoffset, self.taxiname, self.runway) for p in self.taxiwaypath]
        # replace indices with references, and setup node links
        i=0
        while i<len(alllinks):
            l=alllinks[i]
            # Layout assumes no degenerate links (eg node 355 in AIG KSEA)
            if l.nodes[0]==l.nodes[1]:
                alllinks.pop(i)
                continue
            for j in [0,1]:
                l.nodes[j]=allnodes[l.nodes[j]]
                # Layout assumes no duplicate links between nodes (eg FS9 EGKA)
                for l2 in l.nodes[j].links:
                    if l2.nodes==[l.nodes[0], l.nodes[1]] or l2.nodes==[l.nodes[1], l.nodes[0]]:
                        #print "duplicate", ident, l.nodes[0].loc, l.nodes[1].loc
                        break
                else:
                    continue
                break
            else:
                for j in [0,1]: l.nodes[j].links.append(l)
                i+=1
                continue
            alllinks.pop(i)

        # Try and detect and eliminate bogus ATC hacks documented at
        # http://www.scruffyduck.org.uk/filemanager/navega.php?dir=.%2FTutorials%2FAirport%20Design
        # First look for "Overlay" - a node on a runway with exactly two taxi links, both of whose
        # opposite nodes are hold shorts and link directly together, eg node 678 in AIG KSEA
        i=0
        while i<len(allnodes):
            n=allnodes[i]
            isrunway=False
            links=[]
            for l in n.links:
                if l.type=='RUNWAY':
                    isrunway=True
                elif l.type=='TAXI':
                    links.append(l)
            if not isrunway or len(links)!=2:
                i+=1
                continue
            n0=links[0].othernode(n)
            n1=links[1].othernode(n)
            if ('HOLD_SHORT' not in n0.type) or ('HOLD_SHORT' not in n1.type):
                i+=1
                continue
            for l in n0.links:
                if l.nodes[0]==n1 or l.nodes[1]==n1:
                    if output.debug: output.debug.write('Removed ATC hack "Overlay" link over %s\n' % n)
                    n0.links.remove(l)
                    n1.links.remove(l)
                    alllinks.remove(l)
                    break
            else:
                i+=1
                continue

        # Next look for "Diamond" - a node not on a runway, with two links, both of which lead within
        # 2 nodes to a hold short, and where both hold shorts are also connected together via
        # 2 sets of links which include runway nodes. , eg nodes 651 (simple) & 648 (extra nodes) in AIG KSEA
        for n in allnodes:
            if len(n.links)!=2 or 'HOLD_SHORT' in n.type or n.links[0].type!='TAXI' or n.links[1].type!='TAXI': continue
            n0=n.links[0].othernode(n)
            n1=n.links[1].othernode(n)
            if not (len(n0.links)==len(n1.links)==4): continue
            for l in n0.links:
                h0=l.othernode(n0)
                if 'HOLD_SHORT' in h0.type:
                    break
            else:
                continue
            for l in n1.links:
                h1=l.othernode(n1)
                if 'HOLD_SHORT' in h1.type:
                    break
            else:
                continue
            # So both n0 and n1 have 4 links, 1 link each points to the common node n, and 1 link each
            # points to a hold short. Now test that the remaing 2 links each meet each other at a runway.
            for l0 in n0.links:
                if l0.othernode(n0) not in [n,h0]: break	# find 1 of the 2 remaining links

            # Find first runway node
            (o,m)=n0.follow(l0, 3)
            if not o: continue
            isrunway=False
            links=[]
            for l in o.links:
                if l.type=='RUNWAY':
                    isrunway=True
                elif l.type=='TAXI':
                    links.append(l)
                    if l!=m: l1=l
            if not isrunway or len(links)!=2:
                continue
            r0=o

            # Find n1
            (o,m)=r0.follow(l1, 3)
            if not o or o!=n1: continue
            for l2 in n1.links:
                if l2.othernode(n1) not in [n,h1] and l2!=m: break	# find remaining link

            # Find second runway node
            (o,m)=n1.follow(l2, 3)
            if not o: continue
            runwaylink=None
            links=[]
            for l in o.links:
                if l.type=='RUNWAY' and l.othernode(o)==r0:
                    runwaylink=l
                elif l.type=='TAXI':
                    links.append(l)
                    if l!=m: l3=l
            if not runwaylink or len(links)!=2:
                continue
            r1=o

            # Back to n0
            (o,m)=r1.follow(l3, 3)
            if not o or o!=n0: continue

            if output.debug: output.debug.write('Removed ATC hack "Diamond" link over %s\n' % n)
            if False:	# This tends to render badly
                # Now do it again, marking each taxi link as closed
                n0.follow(l0, cb=lambda o,l: setattr(l,'closed',True))
                r0.follow(l1, cb=lambda o,l: setattr(l,'closed',True))
                n1.follow(l2, cb=lambda o,l: setattr(l,'closed',True))
                r1.follow(l3, cb=lambda o,l: setattr(l,'closed',True))

                # Move the original Node onto the runway centreline
                # http://paulbourke.net/geometry/pointline/
                dlat=(r1.loc.lat-r0.loc.lat)
                dlon=(r1.loc.lon-r0.loc.lon)
                m = dlat*dlat + dlon*dlon
                if m==0:
                    n.loc=r0.loc
                else:
                    u = ((n.loc.lat-r0.loc.lat)*dlat + (n.loc.lon-r0.loc.lon)*dlon) / m
                    n.loc=Point(r0.loc.lat + u*dlat, r0.loc.lon + u*dlon)

                # Split the runway centreline to add this point
                newlink=runwaylink.copy()
                alllinks.append(newlink)
                n.links.extend([runwaylink,newlink])
                r1.links.remove(runwaylink)
                r1.links.append(newlink)
                if newlink.nodes[0]==r0:
                    newlink.nodes[0]=n
                    runwaylink.nodes[1]=n
                else:
                    newlink.nodes[1]=n
                    runwaylink.nodes[0]=n
            else:
                # Delete the original Node and the links that skip the runway
                allnodes.remove(n)
                alllinks.remove(n.links[0])
                n0.links.remove(n.links[0])
                alllinks.remove(n.links[1])
                n1.links.remove(n.links[1])
                # Relabel surviving links for better ATC directions
                n0.follow(l0, cb=lambda o,l: setattr(l,'name',n.links[0].name))
                r0.follow(l1, cb=lambda o,l: setattr(l,'name',n.links[1].name))
                n1.follow(l2, cb=lambda o,l: setattr(l,'name',n.links[1].name))
                r1.follow(l3, cb=lambda o,l: setattr(l,'name',n.links[0].name))


        # Find closest runway to each hold short, and label intervening links as 'hot'.
        for n in allnodes:
            if not n.holdshort: continue
            distance=16000
            runway=None
            for l in alllinks:
                if l.type=='RUNWAY':
                    d=min(n.loc.distanceto(l.nodes[0].loc), n.loc.distanceto(l.nodes[1].loc))
                    if d<distance:
                        runway=l
                        distance=d
            if distance>=16000:
                if output.debug:
                    output.debug.write("Can't find a runway for hold short at (%12.8f, %13.8f)\n" % (n.loc.lat, n.loc.lon))
                continue	# WTF - ignore
            else:
                n.name="%s hold short" % runway.name.split()[1]
            # Find and mark intervening links between hold short and corresponding runway nodes.
            # In FSX hold shorts must be within ~70m of runway *edge* to function reliably
            # (but can be further depending on angle relative to runway).
            # We'll cut off search at (arbitrary) 150m from runway *node*.
            hotlinks=n.runwaylinks(n, runway.hotness, [l for l in alllinks if l.type in ['TAXI','PATH']], 150)
            if output.debug and not hotlinks:
                output.debug.write("Can't find links to runway %s for hold short at (%12.8f, %13.8f)\n"  % (runway.hotness, n.loc.lat, n.loc.lon))
            #if output.debug:	#XXX
            #    print runway.hotness, n
            #    for l in hotlinks:
            #        print l
            #    print
            for l in hotlinks:
                l.hotness=runway.hotness


        # XXX TODO: BoundaryFence
        #for b in self.boundaryfence:
        #    if len(b.vertex)>1:
        #        vert=[Point(v.lat, v.lon) for v in b.vertex]
        #        if vert[0]==vert[-1]:
        #            output.facplc.append('opensceneryx/facades/fences/chainlink/1/closed.fac', vert[0:-1])
        #        else:
        #            output.facplc.append('opensceneryx/facades/fences/chainlink/1/open.fac', vert)

        # Tower view location
        if D(self, 'name'):
            view=asciify(self.name, False)+' Tower'
        else:
            view='Tower Viewpoint'
        for tower in self.tower:
            # tower altitude not particularly reliable
            if float(tower.alt)>2+float(self.alt):
                alt=(float(tower.alt)-float(self.alt))*m2f
            else:
                alt=6	# arbitrary
            aptdat.append(AptNav(14, "%12.8f %13.8f %4d 0 %s" % (
                float(tower.lat), float(tower.lon), alt, view)))

        # Ramp startup positions
        startups=[]
        if output.doatc:
            for n in allnodes:
                if n.startup:
                    startups.append(AptNav(1300, "%12.8f %13.8f %6.2f %s %s %s" % (
                                n.loc.lat, n.loc.lon, n.heading,
                                n.startuptype, n.startuptraffic, n.startup)))
            startups.sort(lambda x,y: cmp(x.text.split()[3],y.text.split()[3]) or cmp(x.text[34:].split(' ')[2:], y.text[34:].split(' ')[2:]))	# gate before misc
        else:	# X-Plane<=9
            for n in allnodes:
                if n.startup:
                    startups.append(AptNav(15, "%12.8f %13.8f %6.2f %s" % (
                                n.loc.lat, n.loc.lon, n.heading, n.startup)))
            startups.sort(lambda x,y: cmp(x.text[34:], y.text[34:]))
        aptdat.extend(startups)

        # Tower attached objects, beacons and windsocks
        for tower in self.tower:
            for obj in tower.sceneryobject:
                obj.export(parser, output, aptdat)

        # Taxiway signs
        for t in self.taxiwaysign:
            loc=Point(float(t.lat), float(t.lon))
            if output.excluded(loc): continue
            if t.justification=='LEFT':
                heading=(float(t.heading)-90) % 360
            else:
                heading=(float(t.heading)+90) % 360
            size=2
            smap={'SIZE1':1,'SIZE2':2,'SIZE3':3,'SIZE4':4,'SIZE5':5}
            tmap={'l':'{@L}', 'd':'{@Y}', 'm':'{@R}', 'r':'{@R}'}
            lmap={' ':'_', '>':'{^r}', '^':'{^u}', "'":'{^ru}', '<':'{^l}', 'v':'{^d}', '`':'{^lu}', '/':'{^ld}', '\\':'{^rd}', '[':'', ']':'', 'x':'{no-entry}', '#':'{critical}', '=':'{safety}', '.':'*', '|':'|', '{':'[', '}':']'}
            if D(t, 'size') and t.size in smap: size=smap[t.size]
            label=t.label
            text=''
            while label:
                # type
                if label[0] in tmap:
                    text+=tmap[label[0]]
                else:
                    text+='{@Y}'	# information: should be black on white
                label=label[1:]
                while label:
                    if label.startswith(']['):
                        text+='|'
                        label=label[2:]
                    elif label[0] in 'ldmiru':
                        break		# expect new type
                    elif label.startswith('&gt;'):
                        text+='{^r}'
                        label=label[4:]
                    elif label.startswith('&lt;'):
                        text+='{^l}'
                        label=label[4:]
                    elif label.startswith('&apos;'):
                        text+='{^ru}'
                        label=label[6:]
                    elif label[0] in lmap:
                        text+=lmap[label[0]]
                        label=label[1:]
                    else:
                        text+=label[0]
                        label=label[1:]
                
            aptdat.append(AptNav(20, "%12.8f %13.8f %6.2f %d %d %s" % (
                loc.lat, loc.lon, heading, 0, size, text)))

        # Radio
        codes={'AWOS':50, 'ASOS':50, 'ATIS':50, 'FSS':50,
               'UNICOM':51, 'MULTICOM':51, 'CTAF':51,
               'CLEARANCE':52, 'CLEARANCE_PRE_TAXI':52, 'REMOTE_CLEARANCE_DELIVERY':52,
               'GROUND':53,
               'TOWER':54, 'CENTER':54,
               'APPROACH':55,
               'DEPARTURE':56}
        abrvs={'CLEARANCE':'CLNC DEL', 'CLEARANCE_PRE_TAXI':'PRE TAXI CLNC', 'REMOTE_CLEARANCE_DELIVERY':'CLNC DEL',
               'GROUND':'GND',
               'TOWER':'TWR',
               'CENTER':'CNTR',
               'APPROACH':'APP',
               'DEPARTURE':'DEP'}
        coms={}
        for com in self.com:
            code=codes[com.type]
            if com.type in abrvs:
                abrv=abrvs[com.type]
            else:
                abrv=com.type
            if (code,com.frequency) in coms:
                coms[(code,com.frequency)].append(abrv)
            else:
                coms[(code,com.frequency)]=[abrv]
        coms=coms.items()
        coms.sort()	 # Python 2.3 doesn't support sorted()
        comsout=[]
        for (code,freq),abrv in coms:
            if code==52 and 'CLNC DEL' in abrv and 'PRE TAXI CLNC' in abrv:
                abrv.remove('CLNC DEL')
            comsout.append(AptNav(code, "%5d %s" % (
                        float(freq)*100, '/'.join(abrv))))
        aptdat.extend(comsout)

        for n in self.ndb:
            # Call top-level Ndb class
            ndb.export(parser, output)

        # Doit
        if output.doatc and havetwr:
            atclayout(allnodes, alllinks, self.runway, self.helipad, self.com, output, aptdat, ident)

        # Doit
        taxilayout(allnodes, alllinks, surfaceheading, output, aptdat, ident)

        # Aprons - come after taxiways so that taxiways overlay them
        for a in self.aprons:
            for apron in a.apron:
                if True: # T(apron, 'drawSurface') or T(apron, 'drawDetail'):
                    # drawSurface & drawDetail ignored in FSX and mostly in FS9
                    surface=surfaces[apron.surface]
                    smoothing=0.25
                    l=[]
                    for v in apron.vertex:
                        if D(v, 'lat') and D(v, 'lon'):
                            loc=Point(float(v.lat), float(v.lon))
                        elif D(v, 'biasX') and D(v, 'biasZ'):
                            loc=airloc.biased(float(v.biasX), float(v.biasZ))
                        if output.excluded(loc): break
                        l.append(loc)
                    else:
                        apronlayout(l, surface, surfaceheading, output, aptdat, ident)

        # ApronEdgeLights
        for a in self.apronedgelights:
            for e in a.edgelights:
                l=[]
                for v in e.vertex:
                    if D(v, 'lat') and D(v, 'lon'):
                        loc=Point(float(v.lat), float(v.lon))
                    elif D(v, 'biasX') and D(v, 'biasZ'):
                        loc=airloc.biased(float(v.biasX), float(v.biasZ))
                    if output.excluded(loc): break
                    l.append(loc)
                else:
                    aptdat.append(AptNav(120, "Apron edge"))
                    for loc in l:
                        aptdat.append(AptNav(111, "%12.8f %13.8f %03d" % (
                            loc.lat, loc.lon, 102)))
                    aptdat[-1].code=115
                    aptdat[-1].text=aptdat[-1].text[:26]


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
    def export(self, parser, output):
        if self.dme:
            dtype='VOR-DME'
        else:
            dtype='VOR'
        if D(self, 'name'):
            name=asciify(self.name, False)
            if name[-3:].upper()!=dtype: name+=(' '+dtype)
        else:
            name=self.ident+' '+dtype
        if D(self, 'range'):
            rng=float(self.range)/NM2m
        elif self.type in ['VOT', 'TERMINAL']:
            rng=25
        elif self.type=='HIGH':
            rng=100
        else: # 'LOW'
            rng=40
        if (not D(self, 'nav') or T(self, 'nav')) and not T(self, 'dmeOnly'):
            output.nav.append(AptNav(3, "%12.8f %13.8f %6d %05d %3d %11.3f %-5s %s" % (
                float(self.lat), float(self.lon),
                m2f*float(self.alt), float(self.frequency)*100, rng,
                0, self.ident, name)))

        for dme in self.dme:
            if D(self, 'range'):
                rng=float(dme.range)/NM2m
            output.nav.append(AptNav(12, "%12.8f %13.8f %6d %05d %3d %11.3f %-5s %s" % (
                float(dme.lat), float(dme.lon),
                m2f*float(dme.alt), float(self.frequency)*100, rng,
                0, self.ident, name)))
           

class Marker:
    def __init__(self, attrs):
        for k, v in attrs.iteritems():
            exec("self.%s=v" % k)

    # Export to nav.dat
    def export(self, parser, output):
        if self.type=='INNER':
            mtype='IM'
            code=9
        elif self.type=='MIDDLE':
            mtype='MM'
            code=8
        elif self.type=='OUTER':
            mtype='OM'
            code=7
        else:	# 'BACKCOURSE'
            return
        if D(self, 'name'):
            name=asciify(self.name, False)
            if name[-3:].upper()!=mtype: name+=(' '+mtype)
        else:
            name=self.ident+' '+mtype
        output.nav.append(AptNav(code, "%12.8f %13.8f %6d %05d %3d %11.3f %-5s %s" % (
            float(self.lat), float(self.lon),
            m2f*float(self.alt), 0, 0,
            float(self.heading), '---', name)))


class ModelData:
    def __init__(self, attrs):
        for k, v in attrs.iteritems():
            exec("self.%s=v" % k)

    def export(self, parser, output):
        # Just clean up MDL files in %TMP%
        if D(self, 'sourceFile'):
            tmp=join(gettempdir(), self.sourceFile)
            if exists(tmp): unlink(tmp)


class Parse:
    def __init__(self, fd, srcfile, output):
        if output.debug: output.debug.write('%s\n' % srcfile.encode("latin1"))
        self.filename=basename(srcfile)
        self.output=output
        self.parents=[]
        self.gencount=0
        self.genmulticache={}
        self.genquadcache={}

        parser=xml.parsers.expat.ParserCreate()
        parser.StartElementHandler = self.start_element
        parser.EndElementHandler = self.end_element
        parser.ParseFile(fd)
        fd.close()

    def start_element(self, name, attrs):
        # dump tree
        #if self.output.debug:
        #    self.output.debug.write("%s%s(%s)\n" % ('  '*len(self.parents), name, attrs))
        try:
            if self.parents:
                parent=self.parents[-1]
                elem=getattr(parent, name)(attrs)
                getattr(parent, name.lower()).append(elem)
            else:
                elem=globals()[name](attrs)
            self.parents.append(elem)
        except (KeyError, AttributeError):
            if name=='FSData': return
            if self.output.debug:
                self.output.debug.write("Skipping %s%s(%s)\n" % ('.'*len(self.parents), name, attrs))
            self.parents.append(None)
            
    def end_element(self, name):
        if self.parents:
            elem=self.parents.pop()
            if elem and not self.parents:
                elem.export(self, self.output)

