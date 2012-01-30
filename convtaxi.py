from math import sin, cos, pi, radians, degrees
from os.path import join
from sys import maxint

from OpenGL.GL import GL_LINE_LOOP, GL_TRUE
from OpenGL.GLU import *
try:
    # apparently older PyOpenGL version didn't define gluTessVertex
    gluTessVertex
except NameError:
    from OpenGL import GLU
    gluTessVertex = GLU._gluTessVertex

from convutil import AptNav, Point

twopi=pi+pi

# Runway, taxiway & helipad surfaces
surfaces={'ASPHALT':1, 'BITUMINOUS':1, 'MACADAM':1,
          'OIL_TREATED':1, 'TARMAC':1, 
          'BRICK':2, 'CEMENT':2, 'CONCRETE':2, 'STEEL_MATS':2,
          'GRASS':3,
          'DIRT':4, 'PLANKS':4,
          'SHALE':5, 'CORAL':5, 'GRAVEL':5,
          'CLAY':12, 'SAND':12,
          'WATER':13,
          'ICE':14, 'SNOW':14,
          'UNKNOWN':15}

designators={'C':'C', 'CENTER':'C', 'L':'L', 'LEFT':'L', 'R':'R', 'RIGHT':'R'}

# member var is defined
def D(c, v):
    return getattr(c,v,None)

# member var is defined and true
def T(c, v):
    return getattr(c,v,None)=='TRUE'

class Node:
    parking={'E_PARKING':'East ',  'NE_PARKING':'North East ',
             'N_PARKING':'North ', 'NW_PARKING':'North West ',
             'SE_PARKING':'South East ', 'S_PARKING':'South ',
             'SW_PARKING':'South West ', 'W_PARKING':'West ',
             'PARKING':''}
    types={'RAMP_CARGO':'Cargo ',
           'RAMP_GA':'GA ',        'RAMP_GA_LARGE':'GA ',
           'RAMP_GA_MEDIUM':'GA ', 'RAMP_GA_SMALL':'GA ',
           'RAMP_MIL_CARGO':'Mil Cargo ', 'RAMP_MIL_COMBAT':'Military '}
    gates=['GATE_A', 'GATE_B', 'GATE_C', 'GATE_D', 'GATE_E', 'GATE_F',
           'GATE_G', 'GATE_H', 'GATE_I', 'GATE_J', 'GATE_K', 'GATE_L',
           'GATE_M', 'GATE_N', 'GATE_O', 'GATE_P', 'GATE_Q', 'GATE_R',
           'GATE_S', 'GATE_T', 'GATE_U', 'GATE_V', 'GATE_W', 'GATE_X',
           'GATE_Y', 'GATE_Z']

    def __init__(self, point):
        self.type=point.type
        if D(point, 'orientation') and point.orientation=='REVERSE':
            self.reverse=True
        else:
            self.reverse=False
        self.loc=Point(float(point.lat), float(point.lon))
        self.links=[]
        self.donecross=[[]]
        if D(point, 'name'):	# TaxiwayParking
            self.parking=True
        else:
            self.parking=False
        
        if self.parking and self.type not in ['VEHICLE','FUEL']:
            # Plane parking spot
            self.heading=float(point.heading)
            
            # type appears to be secondary to name
            if point.name in Node.gates:
                self.startup='Gate '+point.name[5]
            elif point.name=='GATE':
                self.startup='Gate'
            elif point.name=='DOCK':
                self.startup='Dock'
            elif point.name in Node.parking:
                self.startup=Node.parking[point.name]
                if point.type in Node.types:
                    self.startup+=Node.types[point.type]
                self.startup+='Ramp'
            # No name
            elif point.type.startswith('GATE'):
                self.startup='Gate'
            elif point.type=='DOC_GA':
                self.startup='Dock'
            elif point.type in Node.types:
                self.startup=Node.types[point.type]+'Ramp'
            # wtf
            else:
                self.startup='Ramp'
                
            if int(point.number):
                self.startup="%s %2d" % (self.startup, int(point.number))
        else:
            self.startup=None

    def __str__(self):
        return 'Node: %s %s %s' % (self.type, self.startup, self.loc)


class Link:	# TaxiwayPath or TaxiwayParking
    def __init__(self, path, parkingoffset, taxinames):
        self.type=path.type
        self.width=float(path.width)
        if self.type=='PARKING':
            self.type='PATH'
            self.nodes=[int(path.start),int(path.end)+parkingoffset]
        else:
            self.nodes=[int(path.start),int(path.end)]
        if self.type=='RUNWAY':
            # We don't draw anything at all for runway paths
            self.draw=self.centreline=self.centrelights=False
            self.lines=['NONE','NONE']
            self.lights=[False,False]
            self.name='Runway '+path.number
            if path.designator in designators:
                self.name+=designators[path.designator]
        else:
            if self.type in ['PATH','PARKING']:
                self.draw=False	# No surface for apron paths
            else:
                # drawSurface & drawDetail ignored in FSX and mostly in FS9
                self.draw=True	# not D(path, 'drawSurface') or T(path, 'drawSurface') or not D(path, 'drawDetail') or T(path, 'drawDetail')
            self.centreline=T(path, 'centerLine')
            self.centrelights=T(path, 'centerLineLighted')
            self.lines=[path.rightEdge,path.leftEdge]
            self.lights=[T(path,'rightEdgeLighted'), T(path,'leftEdgeLighted')]
            self.name=self.type[0]+self.type[1:].lower()
            if taxinames[int(path.name)].name:
                self.name+=' '+taxinames[int(path.name)].name
        if self.draw:
            self.surface=surfaces[path.surface]
        else:
            self.surface=15
        self.done=0
        self.intersect=[[None,None],[None,None]]	# start right left, end right left

    def __str__(self):
        return 'Link: %s %.2dm "%s" [%s, %s] %s' % (
            self.type, self.width, self.name, self.nodes[0], self.nodes[1], self.intersect)

    def findlinked(self, searchspace, found):
        for n in [self.nodes[0],self.nodes[1]]:
            for link in n.links:
                if link.type=='RUNWAY':
                    break	# split graph at runways for easier editing
            else:
                for link in n.links:
                    if link.surface==self.surface and link in searchspace:
                        searchspace.remove(link)
                        found.append(link)
                        link.findlinked(searchspace, found)


# returns taxiway signs for debugging
def bezpt(out, this, next, ratio, brat, code, deb):
    brat=brat*ratio/3.0
    out.append(AptNav(112, "%10.6f %11.6f %10.6f %11.6f %s" % (
        this.lat+ratio*(next.lat-this.lat), this.lon+ratio*(next.lon-this.lon),
        this.lat+brat *(next.lat-this.lat), this.lon+brat *(next.lon-this.lon),
        code)))
    return [AptNav(20, "%10.6f %11.6f 0 0 5 {@R}%s" % (
        this.lat+ratio*(next.lat-this.lat), this.lon+ratio*(next.lon-this.lon),
        deb)),
            AptNav(20, "%10.6f %11.6f 0 0 5 {@Y}%s" % (
        this.lat+brat *(next.lat-this.lat), this.lon+brat *(next.lon-this.lon),
        deb))]


def edgefeature(link1, side1, link2=None, side2=None):
    if not link2:
        link2=link1
        side2=side1
    code=''
    if link1.type!='VEHICLE' and link2.type!='VEHICLE':
        if link1.lines[side1]=='SOLID' or link2.lines[side2]=='SOLID':
            code='53'
        elif link1.lines[side1]=='SOLID_DASHED' or link2.lines[side2]=='SOLID_DASHED':
            code='55'	# ?
        elif link1.lines[side1]=='DASHED' or link2.lines[side2]=='DASHED':
            code='59'
    else:	# vehicle
        if link1.lines[side1]=='SOLID' or link2.lines[side2]=='SOLID':
            code='20'
        elif link1.lines[side1]=='SOLID_DASHED' or link2.lines[side2]=='SOLID_DASHED':
            code='21'	# Use chequerboard
        elif link1.lines[side1]=='DASHED' or link2.lines[side2]=='DASHED':
            code='21'	# Displayed as chequerboard in MSFS
    if link1.lights[side1] or link2.lights[side2]:
        if code:
            code=code+' 102'
        else:
            code='102'
    return code


# --------------------------------------------------------------------------

def tessbegin(datatype, data):
    if datatype!=GL_LINE_LOOP: raise GLUerror	# can't happen
    (points, debez)=data
    points.append([])
    #if __debug__: print "Begin"
    
def tessend(data):
    (points, debez)=data
    #if __debug__: print "End"

def tessvertex(vertex, data):
    (points, debez)=data
    # just accumulate points
    #if __debug__:
    #    (loc1, cnt1, blank1, dummy1, code1)=vertex
    #    print loc1, cnt1, blank1, dummy1, code1
    points[-1].append(vertex)

def tesscombine(coords, vertex, weight, data):
    (points, debez)=data
    if weight[2]==0 and vertex[0][0].equals(vertex[1][0]):
        # normal join
        (loc1, cnt1, blank1, dummy1, code1)=vertex[0]
        (loc2, cnt2, blank2, dummy2, code2)=vertex[1]
        #if __debug__: print "Join", Point(coords[2], coords[0]), cnt1, cnt2, blank1, blank2, '"%s" "%s"' % (code1, code2)
        if code1==None or code2==None:
            code=''	# override
        else:
            code=code1 or code2
        return (loc1, cnt1 and cnt2, blank1|blank2, 0, code)
    #if __debug__:
    #    print "Combine", Point(coords[2], coords[0])
    #    for i in range(len(weight)):
    #        if weight[i]:
    #            (loc, cnt, blank, dummy, code)=vertex[i]
    #            print loc, cnt, blank, dummy, code, round(weight[i],3)
    loc=Point(round(coords[2],6), round(coords[0],6))
    code=''
    for i in range(len(weight)):
        if weight[i]:
            (loc1, cnt1, blank1, dummy1, code1)=vertex[i]
            code=code or code1
            if abs(loc.lat-loc1.lat)<=0.0000025 and abs(loc.lon-loc1.lon)<=0.0000025:
                # dangerously close with rounding
                loc=loc1
                code=code1
                break
    debez.append(loc)
    return (loc, None, 0, 0, code)


# --------------------------------------------------------------------------

def taxilayout(allnodes, alllinks, surfaceheading, output, aptdat=None, ident="unknown"):

    # Edges ----------------------------------------------------------------

    if output.debug:
        output.debug.write("Layout %s\n" % ident)
        if __debug__:
            nodesfile=open(join(output.xppath, ident+"_nodes.txt"), "wt")
            interfile=open(join(output.xppath, ident+"_inter.txt"), "wt")
            pointfile=open(join(output.xppath, ident+"_point.txt"), "wt")

    # First find intersection & bezier points between every pair of links.
    # Then just join the dots.

    # First find all intersections
    for n in allnodes:
        elinks=[]	# (other node, heading, link) = links from this node, sorted CCW
        for link in n.links:
            for end in [0,1]:
                o=link.nodes[end]
                if o!=n: continue
                o=link.nodes[1-end]
                h=radians(n.loc.headingto(o.loc))
                elinks.append((o,h,link))
        elinks.sort(lambda (o1,h1,l1),(o2,h2,l2): cmp(h2,h1)) # CCW
        
        if __debug__:
            if output.debug:
                nodesfile.write("%.6f\t%.6f\n" % (n.loc.lon, n.loc.lat))
                output.debug.write("%s node %d links\n" % (n.loc, len(elinks)))

        for i in range(len(elinks)):
            (n1,h1,link1)=elinks[i]
            for end1 in [0,1]:
                if link1.nodes[end1]==n: break
            if len(elinks)==1:
                # n is a stub
                w=link1.width/2
                if link1.type=='RUNWAY':
                    loc1=n.loc.biased(cos(h1)*w, -sin(h1)*w).round()
                    loc2=n.loc.biased(-cos(h1)*w, sin(h1)*w).round()
                else:
                    loc1=n.loc.biased((cos(h1)-sin(h1))*w, (-sin(h1)-cos(h1))*w).round()
                    loc2=n.loc.biased((-cos(h1)-sin(h1))*w, (sin(h1)-cos(h1))*w).round()
                link1.intersect[end1]=[(loc1,None,0), (loc2,None,0)]
                if __debug__:
                    if output.debug:
                        output.debug.write("%s stub %d\n" % (loc1, i))
                        output.debug.write("%s stub %d\n" % (loc2, i))
                        interfile.write("%.6f\t%.6f\n" % (loc1.lon, loc1.lat))
                        interfile.write("%.6f\t%.6f\n" % (loc2.lon, loc2.lat))
                break
            (n2,h2,link2)=elinks[(i+1)%len(elinks)]
            for end2 in [0,1]:
                if link2.nodes[end2]==n: break
            angle=(h1-pi-h2)%twopi
            if angle<0.1 or angle>twopi-0.1 or abs(h1-h2)<0.1:
                # straight - arbitrary ~5degrees
                w=(link1.width+link2.width)/4
                # not quite average but close enough
                intersect=n.loc.biased(-w*(cos(h1)+cos(h2-pi))/2,
                                       w*(sin(h1)+sin(h2-pi))/2).round()
                link1.intersect[end1][1]=(intersect,None,0)
                link2.intersect[end2][0]=(intersect,None,0)
                if __debug__:
                    if output.debug: output.debug.write("%s straight %d %d %d\n" % (intersect, i, int(degrees(h1)), int(degrees(h2))))
            else:
                ratio=0.5/sin((h1-pi)%twopi-h2)
                intersect=n.loc.biased(-sin(h1)*link2.width*ratio - sin(h2)*link1.width*ratio,
                                       -cos(h1)*link2.width*ratio - cos(h2)*link1.width*ratio).round()
                link1.intersect[end1][1]=(intersect,True,0)
                link2.intersect[end2][0]=(intersect,True,0)
                if __debug__:
                    if output.debug: output.debug.write("%s intersect %d %d %d\n" % (intersect, i, int(degrees(h1)), int(degrees(h2))))
            if __debug__:
                if output.debug: interfile.write("%.6f\t%.6f\n" % (intersect.lon, intersect.lat))
            
    # Fill in bezier points. Can't do bezier control points yet
    if __debug__:
        if output.debug: output.debug.write("Beziers\n")
    for link in alllinks:
        #if not link.intersect[0][0]: continue	# unlinked link!
        for end in [0,1]:
            (loc1,bez1,bad1)=link.intersect[end][0]
            (loc2,bez2,bad2)=link.intersect[1-end][1]
            # check whether intersections cross  ie link length is too short
            # for curves
            # http://astronomy.swin.edu.au/~pbourke/geometry/lineline2d
            # p1=link.nodes[end], p2=loc1, p3=link.nodes[1-end], p4=loc2
            p1=link.nodes[end].loc
            p3=link.nodes[1-end].loc
            d=(loc2.lat-p3.lat)*(loc1.lon-p1.lon)-(loc2.lon-p3.lon)*(loc1.lat-p1.lat)
            if d==0:
                c=0
                a=b=5
            else:
                a=((loc2.lon-p3.lon)*(p1.lat-p3.lat)-(loc2.lat-p3.lat)*(p1.lon-p3.lon))/d
                b=((loc1.lon-p1.lon)*(p1.lat-p3.lat)-(loc1.lat-p1.lat)*(p1.lon-p3.lon))/d
            if a>=0 and a<=1 and b>=0 and b<=1:
                # link is too small and intersection points cross so beziers
                # will loop weirdly. Just let tessellator sort it out.
                # Also make other links' intersections with this link not bez.
                for l2 in link.nodes[end].links:
                    for e2 in [0,1]:
                        if l2.nodes[e2]==link.nodes[end]:
                            for side in [0,1]:
                                if l2.intersect[e2][side][0].equals(loc1):
                                    (loc1,bez1,bad1)=l2.intersect[e2][side]
                                    l2.intersect[e2][side]=(loc1,None,bad1)
                for l2 in link.nodes[1-end].links:
                    for e2 in [0,1]:
                        if l2.nodes[e2]==link.nodes[1-end]:
                            for side in [0,1]:
                                if l2.intersect[e2][side][0].equals(loc2):
                                    (loc2,bez2,bad2)=l2.intersect[e2][side]
                                    l2.intersect[e2][side]=(loc2,None,bad2)
                bad1=bad2=1
                bez1=bez2=None
                if __debug__:
                    if output.debug:
                        output.debug.write("%s %s %s degenerate1\n" % (loc1, bez1, bad1))
                        output.debug.write("%s %s %s degenerate2\n" % (loc2, bez2, bad2))

            # eg KBJC
            d=loc1.distanceto(loc2)
            if (bez1 or bez2) and d<2.04*link.width:	# small fudge factor for safety
                # Would like to use a single point, but then
                # tessellator will merge in some circumstances (eg
                # adjacent taxiways off runway) and we lose the code.
                # So only make a single point if all adjacent links
                # are of the same surface -> will be in same pavement
                if bez1: bez1=(loc1+(loc2-loc1)*0.5).round()
                if bez2: bez2=(loc1+(loc2-loc1)*0.5).round()
                if __debug__:
                    if output.debug:
                        output.debug.write("%s %s %s shorten1\n" % (loc1, bez1, bad1))
                        output.debug.write("%s %s %s shorten2\n" % (loc2, bez2, bad2))
            else:
                if bez1: bez1=(loc1+(loc2-loc1)*link.width/d).round()
                if bez2: bez2=(loc2+(loc1-loc2)*link.width/d).round()
                if __debug__:
                    if output.debug:
                        output.debug.write("%s %s %s\n" % (loc1, bez1, bad1))
                        output.debug.write("%s %s %s\n" % (loc2, bez2, bad2))
                    
            if bez1 and abs(bez1.lat-loc1.lat)<0.00001 and abs(bez1.lon-loc1.lon)<0.00001:
                bez1=None	# collapses to a point
                #if __debug__: print "collapse1"
            link.intersect[end][0]=(loc1,bez1,bad1)
            if bez2 and abs(bez2.lat-loc2.lat)<0.00001 and abs(bez2.lon-loc2.lon)<0.00001:
                bez1=None	# collapses to a point
                #if __debug__: print "collapse2"
            link.intersect[1-end][1]=(loc2,bez2,bad2)
            if __debug__:
                if output.debug:
                    if bez1:
                        pointfile.write("%.6f\t%.6f\n" % (bez1.lon, bez1.lat))
                    else:
                        pointfile.write("%.6f\t%.6f\n" % (loc1.lon, loc1.lat))
                    if bez2:
                        pointfile.write("%.6f\t%.6f\n" % (bez2.lon, bez2.lat))
                    else:
                        pointfile.write("%.6f\t%.6f\n" % (loc2.lon, loc2.lat))
                    
    tessObj = gluNewTess()
    gluTessNormal(tessObj, 0, -1, 0)
    gluTessProperty(tessObj,GLU_TESS_WINDING_RULE,GLU_TESS_WINDING_NONZERO)
    gluTessProperty(tessObj,GLU_TESS_BOUNDARY_ONLY,GL_TRUE)
    gluTessCallback(tessObj,GLU_TESS_BEGIN_DATA,   tessbegin)
    gluTessCallback(tessObj,GLU_TESS_VERTEX_DATA,  tessvertex)
    #gluTessCallback(tessObj,GLU_TESS_END_DATA,     tessend)
    gluTessCallback(tessObj,GLU_TESS_COMBINE_DATA, tesscombine)

    # Candidates
    for surface in range(1,16):
        for (t,name) in [('TAXI','Taxiway'), ('CLOSED','Closed taxiway'), ('PATH','Apron path'), ('VEHICLE','Road')]:
            newpoints=[]
            debez=[]
            gluTessBeginPolygon(tessObj, (newpoints, debez))

            # links
            for link in alllinks:
                if link.type==t and link.surface==surface and link.width>1 and (link.draw or link.lights[0] or link.lights[1] or link.lines[0]!='NONE' or link.lines[1]!='NONE') and (not aptdat or not (output.excluded(link.nodes[0].loc) and output.excluded(link.nodes[1].loc))):
                    gluTessBeginContour(tessObj)
                    if __debug__:
                        if output.debug: output.debug.write("Link\n")
                    for end in [0,1]:
                        (loc,bez,bad)=link.intersect[end][1]	# left
                        if bad:
                            (loc,bez,bad)=link.intersect[1-end][0]	# right
                        code=''
                        if bez and not output.excluded(link.nodes[end].loc):
                            cnt=(bez+(loc-bez)*(2.0/3)).round()
                            gluTessVertex(tessObj, [bez.lon, 0, bez.lat],
                                          (bez, cnt, 0, bad, code))
                            if __debug__:
                                if output.debug: output.debug.write("%s %s %s\n" % (bez, cnt, code))
                        else:
                            gluTessVertex(tessObj, [loc.lon, 0, loc.lat],
                                          (loc, None, 0, bad, code))
                            if __debug__:
                                if output.debug: output.debug.write("%s %s\n" % (loc, code))

                        (loc,bez,bad)=link.intersect[end][0]	# right
                        if bad:
                            (loc,bez,bad)=link.intersect[1-end][1]	# left
                            code=''
                        else:
                            code=edgefeature(link, end)
                        if bez and not output.excluded(link.nodes[end].loc):
                            cnt=(bez+(bez-loc)*(2.0/3)).round()
                            gluTessVertex(tessObj, [bez.lon, 0, bez.lat],
                                          (bez, cnt, 0, bad, code))
                            if __debug__:
                                if output.debug: output.debug.write("%s %s %s\n" % (bez, cnt, code))
                        else:
                            gluTessVertex(tessObj, [loc.lon, 0, loc.lat],
                                          (loc, None, 0, bad, code))
                            if __debug__:
                                if output.debug: output.debug.write("%s %s\n" % (loc, code))
                            
                    gluTessEndContour(tessObj)

            # nodes
            for node in allnodes:
                if aptdat and output.excluded(node.loc): continue
                if len(node.links)<=1: continue	# nothing to do for stubs
                for link in node.links:
                    if link.type==t and link.surface==surface and link.width>1 and (link.draw or link.lights[0] or link.lights[1] or link.lines[0]!='NONE' or link.lines[1]!='NONE'):
                        break
                else:
                    continue

                elinks=[]
                for link in node.links:
                    for end in [0,1]:
                        o=link.nodes[end]
                        if o!=node: continue
                        o=link.nodes[1-end]
                        h=radians(node.loc.headingto(o.loc))
                        elinks.append((o,h,link,end))
                elinks.sort(lambda (o1,h1,l1,e1),(o2,h2,l2,e2): cmp(h2,h1)) # CCW

                if len(node.links)==2:
                    (n1,h1,link1,end1)=elinks[0]
                    (n2,h2,link2,end2)=elinks[1]
                    angle=(h1-pi-h2)%twopi
                    if angle<0.1 or angle>twopi-0.1 or abs(h1-h2)<0.1:
                        # straight - nothing to do
                        continue
                    
                # Points at this node
                gluTessBeginContour(tessObj)
                n=len(elinks)
                if __debug__:
                    if output.debug: output.debug.write("node@ %s #links=%d %s %s)\n" % (node.loc, n,t,surface))
                for i in range(n):
                    (n0,h0,link0,end0)=elinks[(i-1)%n]
                    (n1,h1,link1,end1)=elinks[i]	# this one
                    (n2,h2,link2,end2)=elinks[(i+1)%n]
                    if __debug__:
                        if output.debug: output.debug.write("link to %s %s %s\n" % (link1.nodes[1-end1].loc, link1.type, link1.surface))
                    (loc1,bez1,bad1)=link1.intersect[end1][0]	# right
                    (loc2,bez2,bad2)=link1.intersect[end1][1]	# left
                    code1=edgefeature(link1, end1, link0, 1-end0)
                    code2=edgefeature(link1, 1-end1, link2, end2)
                    blank1=blank2=0

                    if link1.type!=t or link1.surface!=surface:
                        # link to another pavement
                        if link1.draw or link1.type=='RUNWAY' or surface==15:
                            # do fillets
                            code1=''
                            blank1=1	# start of blank
                            blank2=2	# end of blank
                            if surface==15:
                                if link0.surface!=15:
                                    loc1=node.loc
                                    bez1=None
                                    code1=''
                                if link2.surface!=15:
                                    loc2=node.loc
                                    bez2=None
                                    code2=''
                        else:
                            # do simplified pavement
                            (loc0,bez0,bad0)=link0.intersect[end0][1]	# left
                            if bez0:
                                gluTessVertex(tessObj, [bez0.lon, 0, bez0.lat],
                                              (bez0, None, 0, 0, None))
                            else:	# straight
                                gluTessVertex(tessObj, [loc0.lon, 0, loc0.lat],
                                              (loc0, None, 0, 0, None))
                            (loc3,bez3,bad3)=link2.intersect[end2][0]	# right
                            if bez3: debez.append(loc2)
                            bez1=bez2=None
                            code1=code2=''
                            
                    if bez1:
                        if (h0-h1)%twopi>pi:
                            cnt1=(bez1+(loc1-bez1)*(2.0/3)).round()
                            gluTessVertex(tessObj, [cnt1.lon, 0, cnt1.lat],
                                          (cnt1, None, 0, 1, code1))	# dummy
                            if __debug__:
                                if output.debug: output.debug.write("%s dummy1 %d\n" % (cnt1, int(degrees((h0-h1)%twopi))))
                        cnt1=(bez1+(bez1-loc1)*(2.0/3)).round()
                        gluTessVertex(tessObj, [bez1.lon, 0, bez1.lat],
                                      (bez1, cnt1, blank1, 0, code1))
                        if __debug__:
                            if output.debug: output.debug.write("%s %s %d %s\n" % (bez1, cnt1, int(degrees(h1-h2)%360), code1))
                    elif loc1:
                        gluTessVertex(tessObj, [loc1.lon, 0, loc1.lat],
                                      (loc1, None, blank1, 0, code1))
                        if __debug__:
                            if output.debug: output.debug.write("%s %s\n" % (loc1, code1))

                    if bez2:
                        cnt2=(bez2+(loc2-bez2)*(2.0/3)).round()
                        gluTessVertex(tessObj, [bez2.lon, 0, bez2.lat],
                                      (bez2, cnt2, blank2, 0, code2))
                        if __debug__:
                            if output.debug: output.debug.write("%s %s %d %s\n" % (bez2, cnt2, int(degrees(h1-h2)%360), code2))
                        if (h1-h2)%twopi>pi:
                            gluTessVertex(tessObj, [cnt2.lon, 0, cnt2.lat],
                                          (cnt2, None, 0, 1, code2))	# dummy
                            if __debug__:
                                if output.debug: output.debug.write("%s dummy2 %d\n" % (cnt2, int(degrees((h1-h2)%twopi))))
                    elif loc2:
                        gluTessVertex(tessObj, [loc2.lon, 0, loc2.lat],
                                      (loc2, None, blank2, 0, code2))
                        if __debug__:
                            if output.debug: output.debug.write("%s %s\n" % (loc2, code2))
                gluTessEndContour(tessObj)

            gluTessEndPolygon(tessObj)
            if not newpoints: continue

            # Turn any intersected bezier curves in to straight lines
            for points in newpoints:
                n=len(points)
                for i in range(n):
                    (loc,cnt,blank,dummy,code)=points[i]
                    if loc in debez:
                        # Make any adjacent dummies real
                        j=1
                        while True:
                            (loc,cnt,blank,dummy,code)=points[(i-j)%n]
                            points[(i-j)%n]=(loc,None,blank,0,code)
                            if not dummy: break
                            j+=1
                        j=1
                        while True:
                            (loc,cnt,blank,dummy,code)=points[(i+j)%n]
                            points[(i+1)%n]=(loc,None,blank,0,code)
                            if not dummy: break
                            j+=1

            # Tessellator spits out points in any order - first split out exteriors
            if __debug__:
                if output.debug: output.debug.write("After tessellation:\n")
            outpoints=[]
            j=0
            while j<len(newpoints):
                points=newpoints[j]
                n=len(points)
                area2=0
                i=0
                while i<n:
                    (loc,cnt,blank,dummy,code)=points[i]
                    (loc1,cnt1,blank1,dummy1,code1)=points[(i+1)%n]
                    area2+=(loc.lon * loc1.lat - loc1.lon * loc.lat)
                    i+=1
    
                if area2>=0:	# exterior
                    p=newpoints.pop(j)
                    if area2>=1e-8:	# crappy exterior - arbitrary (eg ESSA, KLAS)
                        outpoints.append([p])
                elif area2>-1e-8:	# crappy interior - arbitrary
                    newpoints.pop(j)
                else:
                    j+=1
                if __debug__:
                    if output.debug:
                        if area2>=0: output.debug.write("exterior %3d %s %s\n" % (n, area2, area2>=1e-8))
                        else: output.debug.write("interior %3d %s %s\n" % (n, area2, area2<=-1e-8))
    
            # Attach interiors to enclosing exterior. Assumes no intersections
            # http://local.wasp.uwa.edu.au/~pbourke/geometry/insidepoly/ Sln 2
            #if __debug__: if newpoints: print "Assign interiors:"
            for e in outpoints:
                opoints=e[0]	# the exterior polygon
                n=len(opoints)
                #if __debug__: print "Exterior", len(opoints)
                j=0
                while j<len(newpoints):
                    points=newpoints[j]	# candidate interior polygon
                    for (loc,cnt,blank,dummy,code) in points:
                        #if __debug__: print len(points), j, loc,
                        angle=0
                        for i in range(n):
                            if loc.equals(opoints[i][0]):
                                # try another point in the candidate
                                #if __debug__: print "Coincident", loc,
                                break
                            # sum angles between exterior points
                            thisangle=loc.angleto(opoints[i][0])-loc.angleto(opoints[(i+1)%n][0])
                            if thisangle>pi: thisangle-=twopi
                            if thisangle<-pi: thisangle+=twopi
                            #print opoints[i][0], opoints[(i+1)%n][0], round(thisangle,6)
                            angle+=thisangle
                        else:
                            # angle is 0 (outside) or twopi (inside)
                            if angle>pi:
                                #if __debug__: print "Inside", angle
                                # interior polygon point is inside exterior
                                e.append(newpoints.pop(j))
                            else:
                                #if __debug__: print "Outside", angle
                                j+=1
                            break
                    else:
                        # wtf - all interior points were coincident with exterior
                        #if __debug__: print "wtf", angle
                        newpoints.pop(j)
            if __debug__:
                if output.debug and newpoints:
                    output.debug.write("Unassigned interiors!\n")
                    for points in newpoints: output.debug.write("%d %s\n" % (len(points), points[0][0]))
            
            # Finally output the polygons
            out=[]
            for tw in outpoints:
                out.append(AptNav(110, "%02d %4.2f %6.2f %s" % (
                    surface, 0.25, surfaceheading, name)))
                for points in tw:
                    n=len(points)
                    for i in range(n):
                        (pt,bez,blank,dummy,code)=points[i]
                        if dummy: continue
                        if blank==3:
                            # was joined, eg adjacent taxiways off runway
                            (pt0,bez0,blank0,dummy0,code0)=points[(i-1)%n]
                            (pt2,bez2,blank2,dummy2,code2)=points[(i+1)%n]
                            if blank0 or blank2:
                                bez=None
                                code=''
                            blank=0
                            
                        if blank==2 and bez:	# end of blank
                            out.append(AptNav(111, "%10.6f %11.6f" % (pt.lat, pt.lon)))
                        if bez:
                            out.append(AptNav(112, "%10.6f %11.6f %10.6f %11.6f %s" % (pt.lat, pt.lon, bez.lat, bez.lon, code)))
                        else:
                            out.append(AptNav(111, "%10.6f %11.6f %s" % (pt.lat, pt.lon, code)))
                        if blank==1 and bez:	# start of blank
                            out.append(AptNav(111, "%10.6f %11.6f" % (pt.lat, pt.lon)))
                    assert(out[-1].code!=110)
                    out[-1].code+=2		# Terminate last

            if not outpoints:
                pass	# only exterior was too crappy
            elif aptdat:
                aptdat.extend(out)
            else:
                output.misc.append((110, outpoints[0][0][0][0], out))

        #break	# XXX

    gluDeleteTess(tessObj)


    # Centre lines ---------------------------------------------------------

    # Candidates - have at least one link with a centre line or lights
    links=[l for l in alllinks if (l.centreline or l.centrelights) and (not aptdat or (not output.excluded(l.nodes[0].loc) and not output.excluded(l.nodes[1].loc)))]
    for n in allnodes:
        n.donecross=[[True for i in n.links] for i in n.links]
        if aptdat and output.excluded(n.loc): continue
        for i in range(len(n.links)):
            for j in range(len(n.links)):
                if i!=j and (n.links[i].centreline or n.links[i].centrelights):
                    if n.links[j].type=='RUNWAY':
                        for end in [0,1]:
                            if n!=n.links[j].nodes[end] and len(n.links[j].nodes[end].links)>1: break	# no cross for runway end
                        else:
                            continue
                    n.donecross[i][j]=n.donecross[j][i]=False

    # First do proper links, opportunistically adding crosses
    while links:
        stuff=[]

        # Look for a real end link - no other links at all from end node
        for link in links:
            for startend in [0,1]:
                if len(link.nodes[startend].links)==1:
                    break	# found one
            else:
                continue
            break
        else:
            # Look for an end link - no other valid links from end node
            for link in links:
                for startend in [0,1]:
                    for l in link.nodes[startend].links:
                        if link!=l and l in links and link.name==l.name and link.centreline==l.centreline and link.centrelights==l.centrelights:
                            break	# valid continuation - no good - goto A
                    else:
                        break	# found one - goto B
                else:
                    continue	# A
                break		# B
            else:
                # Only loops left - just pick first link
                link=links[0]
                startend=0

        if link.centreline:
            out=[AptNav(120,"Centreline for %s"  %link.name)]
            if link.type=='VEHICLE':
                code="22"
            else:
                code="51"
            if link.centrelights:
                code=code+" 101"
        else:
            out=[AptNav(120,"Centrelights for %s"%link.name)]
            code="101"

        # Control points are min(width, length/2)   along
        # Bezier  points are min(width, length/2)/3 along

        # Look for a cross before first node
        n=link.nodes[startend]	# start node
        i=n.links.index(link)
        for j in range(len(n.links)):
            if not n.donecross[i][j] and (link.centreline or not n.links[j].centreline) and (link.centrelights or not n.links[j].centrelights):
                n.donecross[i][j]=n.donecross[j][i]=True
                for end in [0,1]:
                    o=n.links[j].nodes[end]	# end node
                    if o!=n: break
                length=n.loc.distanceto(o.loc)
                if len(o.links)==1:
                    if length<link.width:
                        ctrl=1
                    else:
                        ctrl=link.width/length
                elif length>2*n.links[j].width:
                    ctrl=n.links[j].width/length
                else:
                    ctrl=0.5
                stuff.extend(bezpt(out, n.loc, o.loc, ctrl, 1,code,"0"))
                break

        # Follow path
        while True:
            n=link.nodes[startend]	# start node
            o=link.nodes[1-startend]	# next node
            length=n.loc.distanceto(o.loc)
            if len(n.links)==len(o.links)==1:
                out.append(AptNav(111, "%10.6f %11.6f %s" % (
                    n.loc.lat, n.loc.lon, code)))
                stuff.append(AptNav(20, "%10.6f %11.6f 0 0 5 %s" % (
                    n.loc.lat, n.loc.lon, "{@R}1")))
                out.append(AptNav(111, "%10.6f %11.6f %s" % (
                    o.loc.lat, o.loc.lon, code)))
                stuff.append(AptNav(20, "%10.6f %11.6f 0 0 5 %s" % (
                    o.loc.lat, o.loc.lon, "{@R}2")))
            elif len(n.links)==1:
                if length>link.width:
                    out.append(AptNav(111, "%10.6f %11.6f %s" % (
                        n.loc.lat, n.loc.lon, code)))
                    stuff.append(AptNav(20, "%10.6f %11.6f 0 0 5 %s" %(
                        n.loc.lat, n.loc.lon, "{@R}3")))
                stuff.extend(bezpt(out, o.loc, n.loc, min(1,link.width/length), 1, code, "4"))
            elif len(o.links)==1:
                stuff.extend(bezpt(out, n.loc, o.loc, min(1,link.width/length), 5, code, "5"))
                if length>link.width:
                    out.append(AptNav(111, "%10.6f %11.6f %s" % (
                        o.loc.lat, o.loc.lon, code)))
                    stuff.append(AptNav(20, "%10.6f %11.6f 0 0 5 %s" %(
                        o.loc.lat, o.loc.lon, "{@R}6")))
            elif length>2*link.width:
                stuff.extend(bezpt(out, n.loc, o.loc, link.width/length, 5, code, "7"))
                stuff.extend(bezpt(out, o.loc, n.loc, link.width/length, 1, code, "8"))
            else:
                stuff.extend(bezpt(out, n.loc, o.loc, 0.5, 5, code,"9"))
            links.remove(link)

            # Look for next link - greedy
            for l in o.links:
                if l in links and link.name==l.name and link.type==l.type and link.centreline==l.centreline and link.centrelights==l.centrelights:
                    i=o.links.index(link)
                    j=o.links.index(l)
                    o.donecross[i][j]=o.donecross[j][i]=True
                    link=l
                    for startend in [0,1]:
                        if link.nodes[startend]==o: break
                    break	# found one
            else:
                break	# didn't find one

        # Look for a cross at end node
        n=o		# start node
        i=n.links.index(link)
        for j in range(len(n.links)):
            if not n.donecross[i][j] and (link.centreline or not n.links[j].centreline) and (link.centrelights or not n.links[j].centrelights):
                n.donecross[i][j]=n.donecross[j][i]=True
                for end in [0,1]:
                    o=n.links[j].nodes[end]	# end node
                    if o!=n: break
                length=n.loc.distanceto(o.loc)
                if len(o.links)==1:
                    if length<link.width:
                        ctrl=1
                    else:
                        ctrl=link.width/length
                elif length>2*n.links[j].width:
                    ctrl=n.links[j].width/length
                else:
                    ctrl=0.5
                stuff.extend(bezpt(out, n.loc, o.loc, ctrl, 5,code,"-"))
                break

        # Terminate last
        if out[-1].code==111:
            out[-1].code=115
            out[-1].text=out[-1].text[:22]
        else:
            out[-1].code=116
            out[-1].text=out[-1].text[:45]
        if aptdat:
            aptdat.extend(out)
        else:
            output.misc.append((120, n.loc, out))

        if False:	# debug
            stuff[0].text=stuff[0].text[:31]+'B'+stuff[0].text[32:]
            stuff[-1].text=stuff[-1].text[:31]+'L'+stuff[-1].text[32:]
            if aptdat:
                aptdat.extend(stuff)
            else:
                output.misc.append((120, n.loc, stuff))

    # Fill in rest of the crosses
    for n in allnodes:
        for i in range(len(n.links)):
            for j in range(len(n.links)):
                if n.donecross[i][j]:
                    continue
                stuff=[]
                n.donecross[i][j]=n.donecross[j][i]=True
                if n.links[i].centreline or n.links[j].centreline:
                    name="Centreline"
                    if n.links[i].type!='VEHICLE' and n.links[j].type!='VEHICLE':
                        code="51"
                    else:
                        code="22"
                    if n.links[i].centrelights or n.links[j].centrelights:
                        code=code+" 101"
                else:
                    name="Centrelights"
                    code="101"
                if n.links[i].name==n.links[j].name or n.links[j].name.startswith("Runway"):
                    out=[AptNav(120,"%s for %s"  % (name, n.links[i].name))]
                elif n.links[i].name.startswith("Runway"):
                    out=[AptNav(120,"%s for %s"  % (name, n.links[j].name))]
                else:
                    out=[AptNav(120,"%s for Taxi join" % name)]

                a=b=n
                for end in [0,1]:
                    if a==n: a=n.links[i].nodes[end]
                    if b==n: b=n.links[j].nodes[end]

                for (link,o,z) in [(n.links[i],a,1),(n.links[j],b,5)]:
                    length=n.loc.distanceto(o.loc)
                    if len(o.links)==1:
                        if length<link.width:
                            ctrl=1
                        else:
                            ctrl=link.width/length
                    elif length>2*link.width:
                        ctrl=link.width/length
                    else:
                        ctrl=0.5
                    stuff.extend(bezpt(out, n.loc, o.loc, ctrl, z, code, "X"))
                # Terminate last
                out[-1].code=116
                out[-1].text=out[-1].text[:45]
                if aptdat:
                    aptdat.extend(out)
                else:
                    output.misc.append((120, n.loc, out))

                if False:	# debug
                    if aptdat:
                        aptdat.extend(stuff)
                    else:
                        output.misc.append((20, n.loc, stuff))


    # Startup and hold marks -----------------------------------------------
    for n in allnodes:
        if aptdat and output.excluded(n.loc): continue
        if n.type in ['HOLD_SHORT','ILS_HOLD_SHORT']:
            if not n.links: continue
            # Find a link that starts at this node
            for link in n.links:
                if link.nodes[0]==n:
                    h=radians(n.loc.headingto(link.nodes[1].loc))
                    #if __debug__: print n.loc, n.type, "forward", h,
                    break
            else:	# No link starts at this node - reverse
                link=n.links[0]
                h=radians(link.nodes[0].loc.headingto(n.loc))
                #if __debug__: print n.loc, n.type, "backward", h,
            out=[AptNav(120, "%s hold short" % link.name)]
            #if __debug__: print "reverse=", n.reverse
            if n.reverse: h=(h+pi)%twopi
            w=max(1, link.width/2-0.5)
            if n.type=='HOLD_SHORT':
                code="54"
            else:
                code="56 103"
            loc=n.loc.biased(-cos(h)*w, sin(h)*w)
            out.append(AptNav(111, "%10.6f %11.6f %s" % (
                loc.lat, loc.lon, code)))
            loc=n.loc.biased(cos(h)*w, -sin(h)*w)
            out.append(AptNav(115, "%10.6f %11.6f" % (
                loc.lat, loc.lon)))
            if aptdat:
                aptdat.extend(out)
            else:
                output.misc.append((120, n.loc, out))            
            
        elif n.parking:	# TaxiwayParking
            for link in n.links:
                if not link.centreline: continue
                if n.startup:
                    out=[AptNav(120, n.startup)]
                else:
                    out=[AptNav(120, link.name)]
                for end in [0,1]:
                    o=link.nodes[end]
                    if o!=n: break
                h=radians(n.loc.headingto(o.loc))
                w=link.width/4
                if n.type=='VEHICLE':
                    code="22"	# not sure what to do
                else:
                    code="51"
                loc=n.loc.biased(-cos(h)*w, sin(h)*w)
                out.append(AptNav(111, "%10.6f %11.6f %s" % (
                    loc.lat, loc.lon, code)))
                loc=n.loc.biased(cos(h)*w, -sin(h)*w)
                out.append(AptNav(115, "%10.6f %11.6f" % (
                    loc.lat, loc.lon)))
                if aptdat:
                    aptdat.extend(out)
                else:
                    output.misc.append((120, n.loc, out))            

# --------------------------------------------------------------------------

def aproncombine(coords, vertex, weight):
    return Point(coords[2], coords[0])

def apronlayout(points, surface, surfaceheading, output, aptdat=None, ident="unknown"):

    tessObj = gluNewTess()
    gluTessNormal(tessObj, 0, -1, 0)
    gluTessProperty(tessObj,GLU_TESS_WINDING_RULE,GLU_TESS_WINDING_NONZERO)
    gluTessProperty(tessObj,GLU_TESS_BOUNDARY_ONLY,GL_TRUE)
    gluTessCallback(tessObj,GLU_TESS_BEGIN_DATA,   tessbegin)
    gluTessCallback(tessObj,GLU_TESS_VERTEX_DATA,  tessvertex)
    #gluTessCallback(tessObj,GLU_TESS_END_DATA,     tessend)
    gluTessCallback(tessObj,GLU_TESS_COMBINE, aproncombine)

    newpoints=[]
    gluTessBeginPolygon(tessObj, (newpoints, None))
    gluTessBeginContour(tessObj)
    for pt in points:
        gluTessVertex(tessObj, [pt.lon, 0, pt.lat], pt)
    gluTessEndContour(tessObj)
    gluTessEndPolygon(tessObj)
    gluDeleteTess(tessObj)

    # Tessellator spits out points in any order - first split out exteriors
    outpoints=[]
    j=0
    while j<len(newpoints):
        points=newpoints[j]
        n=len(points)
        area2=0
        i=0
        while i<n:
            loc=points[i]
            loc1=points[(i+1)%n]
            area2+=(loc.lon * loc1.lat - loc1.lon * loc.lat)
            i+=1
    
        if area2>=0:	# exterior
            p=newpoints.pop(j)
            if area2>=1e-8:	# crappy exterior - arbitrary
                outpoints.append([p])
        elif area2>-1e-8:	# crappy interior - arbitrary
            newpoints.pop(j)
        else:
            j+=1
    
    # Attach interiors to enclosing exterior. Assumes no intersections
    # http://local.wasp.uwa.edu.au/~pbourke/geometry/insidepoly/ Sln 2
    if __debug__:
        if newpoints: print "Assign interiors:"
    for e in outpoints:
        opoints=e[0]	# the exterior polygon
        n=len(opoints)
        if __debug__: print "Exterior", len(opoints)
        j=0
        while j<len(newpoints):
            points=newpoints[j]	# candidate interior polygon
            for loc in points:
                if __debug__: print len(points), j, loc,
                angle=0
                for i in range(n):
                    if loc.equals(opoints[i]):
                        # try another point in the candidate
                        if __debug__: print "Coincident", loc,
                        break
                    # sum angles between exterior points
                    thisangle=loc.angleto(opoints[i])-loc.angleto(opoints[(i+1)%n])
                    if thisangle>pi: thisangle-=twopi
                    if thisangle<-pi: thisangle+=twopi
                    angle+=thisangle
                else:
                    # angle is 0 (outside) or twopi (inside)
                    if angle>pi:
                        if __debug__: print "Inside", angle
                        # interior polygon point is inside exterior
                        e.append(newpoints.pop(j))
                    else:
                        if __debug__: print "Outside", angle
                        j+=1
                    break
            else:
                # wtf - all interior points were coincident with exterior
                if __debug__: print "wtf", angle
                newpoints.pop(j)
    if __debug__:
        if output.debug and newpoints:
            output.debug.write("Unassigned interiors!\n")
            for points in newpoints: output.debug.write("%d %s\n" % (len(points), points[0]))
            
    # Finally output the polygons
    out=[]
    for tw in outpoints:
        out.append(AptNav(110, "%02d %4.2f %6.2f Apron" % (
            surface, 0.25, surfaceheading)))
        for points in tw:
            n=len(points)
            for i in range(n):
                out.append(AptNav(111, "%10.6f %11.6f" % (points[i].lat, points[i].lon)))
            assert(out[-1].code!=110)
            out[-1].code+=2		# Terminate last

    if not outpoints:
        pass	# only exterior was too crappy
    elif aptdat:
        aptdat.extend(out)
    else:
        output.misc.append((110, outpoints[0][0][0], out))
