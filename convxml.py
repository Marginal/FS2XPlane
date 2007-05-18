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

from math import sin, cos, atan, radians
from os import unlink
from os.path import basename, exists, join
from sys import maxint
import xml.parsers.expat
from tempfile import gettempdir

from convutil import m2f, NM2m, complexity, asciify, AptNav, Object, Point, Matrix, FS2XError
from convobjs import makegenquad, makegenmulti
from convtaxi import designators, surfaces, taxilayout, Node, Link


# member var is defined
def D(c, v):
    return (v in dir(c) and eval("c.%s" % v))

# member var is defined and true
def T(c, v):
    return (v in dir(c) and eval("c.%s" % v)=='TRUE')

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
                alt=alt+float(bias.biasY)

        for b in self.beacon:
            if D(b, 'baseType') and b.baseType=='SEA_BASE':
                lit=2
            elif D(b, 'baseType') and b.baseType=='HELIPORT':
                lit=3
            elif D(b, 'type') and b.type=='MILITARY':
                lit=4
            else:	# civilian land airport
                lit=1
            a=AptNav(18, '%10.6f %11.6f %d Beacon' % (loc.lat, loc.lon, lit))
            if aptdat:
                aptdat.append(a)
            else:
                output.misc.append((18, loc, [a]))

        for w in self.windsock:
            lit=0
            if T(w, 'lighted'): lit=1
            a=AptNav(19, '%10.6f %11.6f %d Windsock' %(loc.lat, loc.lon, lit))
            if aptdat:
                aptdat.append(a)
            else:
                output.misc.append((19, loc, [a]))

        # Don't add placements if we're doing a second round of apt.dat
        if output.doexcfac: return
        
        for l in self.genericbuilding:
            scale=1.0
            if D(l, 'scale'): scale=round(float(l.scale),2)
            if D(self, 'altitudeIsAgl') and not T(self, 'altitudeIsAgl'):
                output.log('Absolute altitude (%sm) for generic building at (%10.6f, %11.6f) in file %s' % (round(alt,2), loc.lat, loc.lon, parser.filename))
            elif abs(alt)>0.1:
                output.log('Non-zero altitude (%sm) for generic building at (%10.6f, %11.6f) in file %s' % (round(alt,2), loc.lat, loc.lon, parser.filename))
            if pitch or bank:
                output.log('Non-zero pitch/bank (%s/%s) for generic building at (%10.6f, %11.6f) in file %s' % (pitch, bank, loc.lat, loc.lon, parser.filename))
            texs=[int(l.bottomTexture), int(l.windowTexture),
                  int(l.topTexture), int(l.roofTexture)]
            for m in l.multisidedbuilding:
                parser.gencount += 1
                name="%s-generic-%d.obj" % (asciify(parser.filename[:-4]),
                                            parser.gencount)
                obj=makegenmulti(name, int(m.buildingSides),
                                 scale*float(m.sizeX), scale*float(m.sizeZ),
                                 [scale*float(m.sizeBottomY),
                                  scale*float(m.sizeWindowY),
                                  scale*float(m.sizeTopY),
                                  scale*float(m.sizeRoofY)],
                                 texs)
                output.objdat[name]=[obj]
                output.objplc.append((loc, heading, cmplx, name, 1))
                                
            for m in l.pyramidalbuilding:
                h2=2*(float(m.sizeBottomY)+float(m.sizeWindowY)+
                      float(m.sizeTopY))
                parser.gencount += 1
                name="%s-generic-%d.obj" % (asciify(parser.filename[:-4]),
                                            parser.gencount)
                obj=makegenquad(name,
                                scale*float(m.sizeX), scale*float(m.sizeZ),
                                atan((float(m.sizeX)-float(m.sizeTopX))/h2),
                                atan((float(m.sizeZ)-float(m.sizeTopZ))/h2),
                                [scale*float(m.sizeBottomY),
                                 scale*float(m.sizeWindowY),
                                 scale*float(m.sizeTopY)],
                                texs, 0)
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
                parser.gencount += 1
                name="%s-generic-%d.obj" % (asciify(parser.filename[:-4]),
                                            parser.gencount)
                obj=makegenquad(name,
                                scale*float(m.sizeX), scale*float(m.sizeZ),
                                0, 0, heights, rtexs, roof)
                output.objdat[name]=[obj]
                output.objplc.append((loc, heading, cmplx, name, 1))
                
        for l in self.libraryobject:
            scale=1.0
            if D(l, 'scale'): scale=round(float(l.scale),2)
            name=l.name.lower()
            if name in output.friendly:
                friendly=output.friendly[name]
            else:
                friendly=name
            if D(self, 'altitudeIsAgl') and not T(self, 'altitudeIsAgl'):
                output.log('Absolute altitude (%sm) for object %s at (%10.6f, %11.6f) in file %s' % (round(alt,2), friendly, loc.lat, loc.lon, parser.filename))
            elif abs(alt)>0.1:
                output.log('Non-zero altitude (%sm) for object %s at (%10.6f, %11.6f) in file %s' % (round(alt,2), friendly, loc.lat, loc.lon, parser.filename))
            if pitch or bank:
                output.log('Non-zero pitch/bank (%s/%s) for object %s at (%10.6f, %11.6f) in file %s' % (pitch, bank, friendly, loc.lat, loc.lon, parser.filename))
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
        output.nav.append(AptNav(2, "%10.6f %11.6f %6d %-5d %3d %11.3f %-5s %s" % (
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
        
    class Tower:
        def __init__(self, attrs):
            for k, v in attrs.iteritems():
                exec("self.%s=v" % k)
            self.sceneryobject=[]

        class SceneryObject(SceneryObject):
            pass

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

    # Export airport to apt.dat and nav.dat
    def export(self, parser, output):

        airloc=Point(float(self.lat), float(self.lon))
        ident=self.ident
        if len(self.ident)>4:
            ident=ident[0:4]
            
        if ident not in output.apt:
            output.apt[ident]=(airloc,[])
            if ident!=self.ident:
                output.log('Shortened ICAO airport code from "%s" to "%s"' % (
                    self.ident, ident))
        elif self.runway or self.helipad or self.taxiwaypoint:
            # Duplicate
            raise FS2XError('Found duplicate definition of airport %s in %s' % (self.ident, parser.filename))

        aptdat=output.apt[ident][1]
            
        # Might just be a placeholder - only create header if it has a name
        if D(self, 'name') :
            txt=("%5d" % (float(self.alt)*m2f))
            if self.tower:
                txt+=" 1"
            else:
                txt+=" 0"
            txt+=(" 0 %s %s" % (ident, asciify(self.name, True)))
            aptdat.append(AptNav(1, txt))

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
            number=['XXX','XXX']
            angle=[3,3]
            markings=[0,0]
            lights=[0,0]
            tdzl=[0,0]
            reil=[0,0]

            nos={'EAST':9, 'NORTH':36, 'NORTHEAST':4, 'NORTHWEST':31,
                 'SOUTH':18, 'SOUTHEAST':13, 'SOUTHWEST':22, 'WEST':27}
            opp={'C':'C', 'CENTER':'C', 'L':'R', 'LEFT':'R', 'R':'L', 'RIGHT':'L'}
            if nos.has_key(runway.number):
                number[0]=("%02d" % nos[runway.number])
                number[1]=("%02d" % ((18+nos[runway.number])%36))
            else:
                number[0]=("%02d" % int(runway.number))
                number[1]=("%02d" % ((18+int(runway.number))%36))
            if number[1]=='00': number[1]='36'
            if D(runway, 'designator'):
                if runway.designator in designators:
                    number[0]+=designators[runway.designator]
                    number[1]+=opp[runway.designator]
            else:
                if D(runway, 'primaryDesignator') and runway.primaryDesignator in designators:
                    number[0]+=designators[runway.primaryDesignator]
                if D(runway, 'secondaryDesignator') and runway.secondaryDesignator in designators:
                    number[1]+=designators[runway.secondaryDesignator]

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
                if D(light, 'center') and light.center!='NONE':
                    centrelights=1
                if D(light, 'edge'):
                    if light.edge=='NONE':
                        edgelights=0
                    #elif light.edge=='LOW':
                    #    edgelights=1	# not supported in 8.50
                    #elif light.edge=='HIGH':
                    #    edgelights=3	# not supported in 8.50
                    else:
                        edgelights=2

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
                    name=("%s %s" % (self.ident, ils.name))
                else:
                    name=('%s %s ILS' % (self.ident, number))
                if D(ils, 'range'):
                    rng=float(ils.range)/NM2m
                else:
                    rng=18
                output.nav.append(AptNav(4, "%10.6f %11.6f %6d %05d %3d %11.3f %-5s %s" % (
                    float(ils.lat), float(ils.lon), m2f*float(ils.alt), float(ils.frequency)*100, rng,
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
                    output.nav.append(AptNav(6, "%10.6f %11.6f %6d %05d %3d %11.3f %-5s %s" % (
                        float(gs.lat), float(gs.lon), m2f*float(gs.alt), float(ils.frequency)*100, rng,
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
                    output.nav.append(AptNav(12, "%10.6f %11.6f %6d %05d %3d %11.3f %-5s %s" % (
                        
                        float(dme.lat), float(dme.lon), m2f*float(dme.alt), float(ils.frequency)*100, rng,
                        0, ils.ident, name)))

            #if length<=1 or width<=1:
            #    continue	# X-Plane considers size<1m to be an error.
            #        
            #if len(number)<3: number+='x'
            # XXX
            #for a in aptdat:
            #    if a.code==100 and a.text[0:3]==number:
            #        raise FS2XError('Found duplicate definition of runway %s in %s' % (number.replace('x',''), parser.filename))

            if runway.surface=='WATER':
                txt="%5.2f %d" %(width, distance or markings[0] or markings[1])
                for end in [0,1]:
                    txt=txt+(" %-3s %10.6f %11.6f" % (
                        number[end], loc[end].lat, loc[end].lon))
                aptdat.append(AptNav(101, txt))
            else:
                if output.excluded(cloc):
                    # Make X-Plane happy by creating runways
                    surface=15	# transparent
                    shoulder=centrelights=edgelights=distance=markings[0]=markings[1]=tdzl[0]=tdzl[1]=reil[0]=reil[1]=0 #lights[0]=lights[1]
                
                txt="%5.2f %02d %02d %4.2f %d %d %d" % (width, surface, shoulder, smoothing, centrelights, edgelights, distance)
                for end in [0,1]:
                    txt=txt+(" %-3s %10.6f %11.6f %5.1f %5.1f %02d %02d %d %d" % (number[end], loc[end].lat, loc[end].lon, displaced[end], overrun[end], markings[end], lights[end], tdzl[end], reil[end]))
                aptdat.append(AptNav(100, txt))
                
            # VASIs
            for vasi in runway.vasi:
                if vasi.type in ['PAPI2', 'PAPI4', 'APAP', 'PANEL']:
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
                else:
                    vheading=(heading+180)%360
                x=float(vasi.biasX)
                z=float(vasi.biasZ)
                # location in MSFS is of rear innermost light
                if vtype==1:
                    z=z+75
                    x=x+1
                else:
                    x=x+12
                if vasi.side=='RIGHT': x=-x
                h=radians(vheading)
                vloc=cloc.biased(-cos(h)*x-sin(h)*z, sin(h)*x-cos(h)*z)
                # was not output.excluded(vloc):, but keep VASI info
                aptdat.append(AptNav(21, '%10.6f %11.6f %d %6.2f %3.1f' % (
                    vloc.lat, vloc.lon, vtype, vheading, vangle)))

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
            aptdat.append(AptNav(102, "H%0d %10.6f %11.6f %6.2f %4.2f %4.2f %02d %02d %02d %4.2f %d" % (
                hno, loc.lat, loc.lon, heading, length, width,
                surface, markings, shoulder, smoothing, lights)))

        # Align aprons and taxiway grain with main (first) runway
        if self.runway:
            surfaceheading=float(self.runway[0].heading)%180
        else:
            surfaceheading=0
        
        # Old taxiways
        if False:
            for t in self.taxiwaypath:
                if T(t, 'drawSurface') and t.type not in ["PARKING","RUNWAY","PATH"]:
                    snode=self.taxiwaypoint[int(t.start)]
                    enode=self.taxiwaypoint[int(t.end)]
                    start=Point(float(snode.lat),
                                float(snode.lon))
                    end=Point(float(enode.lat),
                              float(enode.lon))
                    if output.excluded(start) or output.excluded(end): continue
                    loc=Point((start.lat+end.lat)/2, (start.lon+end.lon)/2)
                    heading=start.headingto(end)
                    width=round(m2f*float(t.width),0)
                    length=0.5*width + m2f*start.distanceto(end)
                    surface=surfaces[t.surface]
                    surface=3	# grass
                    
                    if length<=1 or width<=1:
                        continue	# X-Plane considers size<1m to be an error.
                    lights=1
                    aptdat.append(AptNav(10, "%10.6f %11.6f %s %6.2f %6d %04d.%04d %04d.%04d %4d 1%d11%d1 %02d %d %d %4.2f %d %04d.%04d" % (
                        loc.lat, loc.lon, 'xxx', heading, length, 0, 0, 0, 0,width,
                        lights, lights, surface, 0, 0, 0.25, 0, 0, 0)))

        # Taxiways - build arrays for easier access
        allnodes = [Node(t) for t in self.taxiwaypoint]
        parkingoffset=len(allnodes)
        allnodes.extend([Node(t) for t in self.taxiwayparking])
        alllinks = [Link(p, parkingoffset, self.taxiname) for p in self.taxiwaypath]
        # replace indices with references, and setup node links
        i=0
        while i<len(alllinks):
            l=alllinks[i]
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

        taxilayout(allnodes, alllinks, surfaceheading, output, aptdat, ident)

        # Aprons - come after taxiways so that taxiways overlay them
        for a in self.aprons:
            for apron in a.apron:
                if T(apron, 'drawSurface') or T(apron, 'drawDetail'):
                    surface=surfaces[apron.surface]
                    smoothing=0.25
                    if self.runway:
                        heading=float(self.runway[0].heading)%180
                    else:
                        heading=0
                    l=[]
                    for v in apron.vertex:
                        if D(v, 'lat') and D(v, 'lon'):
                            loc=Point(float(v.lat), float(v.lon))
                        elif D(v, 'biasX') and D(v, 'biasZ'):
                            loc=airloc.biased(float(v.biasX), float(v.biasZ))
                        if output.excluded(loc): break
                        l.append(loc)
                    else:
                        # sort CCW
                        area2=0
                        count=len(l)
                        for i in range(count):
                            area2+=(l[i].lon * l[(i+1)%count].lat -
                                    l[(i+1)%count].lon * l[i].lat)
                        if area2<0: l.reverse()
                        aptdat.append(AptNav(110, "%02d %4.2f %6.2f Apron" % (
                            surface, smoothing, surfaceheading)))
                        for loc in l:
                            aptdat.append(AptNav(111, "%10.6f %11.6f %d" % (
                                loc.lat, loc.lon, 0)))
                        aptdat[-1].code=113

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
                        aptdat.append(AptNav(111, "%10.6f %11.6f %03d" % (
                            loc.lat, loc.lon, 102)))
                    aptdat[-1].code=115
                    aptdat[-1].text=aptdat[-1].text[:22]

        # Tower view location
        if D(self, 'name'):
            view=self.name+' Tower'
        else:
            view='Tower Viewpoint'
        for tower in self.tower:
            aptdat.append(AptNav(14, "%10.6f %11.6f %6.2f 0 %s" % (
                float(tower.lat), float(tower.lon), (float(tower.alt)-float(self.alt))*m2f, view)))

        # Ramp startup positions
        startups=[]
        for n in allnodes:
            if n.startup:
                startups.append(AptNav(15, "%10.6f %11.6f %6.2f %s" % (
                    n.loc.lat, n.loc.lon, n.heading, n.startup)))
        startups.sort(lambda x,y: cmp(x.text[30:], y.text[30:]))
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
                
            aptdat.append(AptNav(20, "%10.6f %11.6f %6.2f %d %d %s" % (
                loc.lat, loc.lon, heading, 0, size, text)))

        # ATC
        codes={'AWOS':50, 'ASOS':50, 'ATIS':50, 'FSS':50,
               'UNICOM':51, 'MULTICOM':51, 'CTAF':51,
               'CLEARANCE':52, 'CLEARANCE_PRE_TAXI':52, 'REMOTE_CLEARANCE_DELIVERY':52,
               'GROUND':53,
               'TOWER':54, 'CENTER':54,
               'APPROACH':55,
               'DEPARTURE':56}
        abbrv={'CLEARANCE':'CLD', 'CLEARANCE_PRE_TAXI':'CLD PRE-TAXI', 'REMOTE_CLEARANCE_DELIVERY':'CLD',
               'UNICOM':'UNIC',
               'MULTICOM':'MULT',
               'GROUND':'GND',
               'TOWER':'TWR',
               'CENTER':'CNTR',
               'APPROACH':'APP',
               'DEPARTURE':'DEP'}
        coms=[]
        for com in self.com:
            if com.type=='APPROACH' and com.name.endswith(' DIRECTOR'):
                ctype='DIR'
                com.name=com.name[:-9]
            elif com.type=='CLEARANCE' and com.name.endswith(' DELIVERY'):
                ctype='CLD'
                com.name=com.name[:-9]
            elif com.type in abbrv:
                ctype=abbrv[com.type]
            else:
                ctype=com.type
            coms.append(AptNav(codes[com.type], "%5d %s %s" % (
                float(com.frequency)*100, com.name, ctype)))
        coms.sort()
        aptdat.extend(coms)

        for n in self.ndb:
            # Call top-level Ndb class
            ndb.export(parser, output)


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
            name=self.name
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
            output.nav.append(AptNav(3, "%10.6f %11.6f %6d %05d %3d %11.3f %-5s %s" % (
                float(self.lat), float(self.lon),
                m2f*float(self.alt), float(self.frequency)*100, rng,
                0, self.ident, name)))

        for dme in self.dme:
            if D(self, 'range'):
                rng=float(dme.range)/NM2m
            output.nav.append(AptNav(12, "%10.6f %11.6f %6d %05d %3d %11.3f %-5s %s" % (
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
            name=self.name
            if name[-3:].upper()!=mtype: name+=(' '+mtype)
        else:
            name=self.ident+' '+mtype
        output.nav.append(AptNav(code, "%10.6f %11.6f %6d %05d %3d %11.3f %-5s %s" % (
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
        self.filename=basename(srcfile)
        self.elems=[]
        self.parents=[]
        self.parname=''	# parent class(es)
        self.gencount=0

        parser=xml.parsers.expat.ParserCreate()
        parser.StartElementHandler = self.start_element
        parser.EndElementHandler = self.end_element
        parser.ParseFile(fd)
        fd.close()

        # Parsed OK. Now export
        for elem in self.elems:
            elem.export(self, output)

    def start_element(self, name, attrs):
        if name=='FSData':
            return
        try:
            elem=eval('%s%s(attrs)' % (self.parname, name))
            if self.parents:
                exec("self.parents[-1].%s.append(elem)" % name.lower())
            else:
                self.elems.append(elem)
            self.parents.append(elem)
            self.parname+=(name+'.')
        except (NameError, AttributeError):
            #print "Skippping", self.parname, name
            return
            
    def end_element(self, name):
        if self.parname[-(len(name)+1):-1]==name:
            self.parents.pop()
            self.parname=self.parname[:-(len(name)+1)]

