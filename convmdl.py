from os import listdir
from os.path import basename, dirname, join, normpath, pardir, splitext
from struct import unpack

from convbgl import findtex, maketexdict
from convutil import asciify, rgb2uv,  Matrix, Object


# handle FSX format library MDL file
class ProcScen:
    def __init__(self, bgl, enda, scale, libname, srcfile, texdir, output, 
                 scen, tran):

        self.old=False	# Old style scenery found and skipped
        self.rrt=False	# Old style runways/roads found and skipped
        self.anim=False	# Animations found and skipped

        assert(scale==1)	# new-style objects are scaled when placed

        comment="object %s in file %s" % (libname,asciify(basename(srcfile),False))

        tex=[]
        mat=[]
        vt=[]
        idx=[]
        matrix=[]
        amap=[]
        scen=[]
        data={}
        
        if bgl.read(4)!='RIFF': raise IOError
        (mdlsize,)=unpack('<I', bgl.read(4))
        endmdl=bgl.tell()+mdlsize
        if bgl.read(4)!='MDLX': raise IOError
        while bgl.tell()<endmdl:
            c=bgl.read(4)
            (size,)=unpack('<I', bgl.read(4))
            if c=='MDLD':
                end=size+bgl.tell()
                while bgl.tell()<end:
                    c=bgl.read(4)
                    (size,)=unpack('<I', bgl.read(4))
                    if c=='TEXT':
                        tex.extend([bgl.read(64).strip('\0').strip() for i in range(0,size,64)])
                    elif c=='MATE':
                        for i in range(0,size,120):
                            (typ,unk,unk,texture,unk,unk,unk,lit,unk,unk,dr,dg,db,da,sr,sg,sb,sa,sp,er,eg,eb,ea,bloomfloor,ambscale,unk,srcblend,dstblend,alphafunc,alphathreshold,zwritealpha)=unpack('<HHfI6I4f4ff4f2ffIIIff', bgl.read(120))
                            # what about alpha blend & func, and emissive blend
                            if typ&0x82:
                                if typ&2:
                                    texture=findtex(tex[texture], texdir, output.addtexdir)
                                else:
                                    texture=None
                                if typ&0x80:
                                    lit=findtex(tex[lit], texdir, output.addtexdir)
                                    (er,eg,eb)=(0,0,0)
                                else:
                                    lit=None
                                
                                # discard diffuse & power - see class Object
                                mat.append(((1.0,1.0,1.0),(sr,sg,sb),(er,eg,eb),0, (texture, lit)))
                            else:
                                mat.append(((dr,dg,db),(sr,sg,sb),(er,eg,eb),0, None))
                        #print "Materials", len(mat)
                        #for i in mat: print i
                    elif c=='INDE':
                        idx=unpack('<%dH' % (size/2), bgl.read(size))
                    elif c=='VERB':
                        endv=size+bgl.tell()
                        while bgl.tell()<endv:
                            c=bgl.read(4)
                            (size,)=unpack('<I', bgl.read(4))
                            if c=='VERT':
                                vt.append([unpack('<8f',bgl.read(32)) for i in range(0,size,32)])
                            else:
                                bgl.seek(size,1)
                    elif c=='TRAN':
                        for i in range(0,size,64):
                            matrix.append(Matrix([unpack('<4f',bgl.read(16)) for j in range(4)]))
                        #print "Matrices", len(matrix)
                        #for i in matrix: print i
                    elif c=='AMAP':
                        for i in range(0,size,8):
                            (a,b)=unpack('<2I',bgl.read(8))
                            amap.append(b)
                        #print "Animation map", len(amap)
                        #for i in amap: print i                        
                    elif c=='SCEN':
                        # Assumed to be after TRAN and AMAP sections
                        count=size/8
                        for i in range(count):
                            (child,peer,offset,unk)=unpack('<4h',bgl.read(8))
                            thismatrix=matrix[amap[offset/8]]
                            scen.append((child,peer,thismatrix,-1))
                        # Invert Child/Peer pointers to get parents
                        for i in range(count):
                            (child, peer, thismatrix, parent)=scen[i]
                            if child!=-1:	# child's parent is me
                                (xchild, xpeer, xmatrix, xparent)=scen[child]
                                scen[child]=(xchild, xpeer, xmatrix, i)
                            if peer!=-1:	# peer's parent is my parent
                                (xchild, xpeer, xmatrix, xparent)=scen[peer]
                                scen[peer]=(xchild, xpeer, xmatrix, parent)
                        #print "Scene Graph", len(scen)
                        #for i in scen: print i
                    elif c=='LODT':
                        endt=size+bgl.tell()
                        partno=0
                        maxlod=0
                        #print "Parts"
                        while bgl.tell()<endt:
                            c=bgl.read(4)
                            (size,)=unpack('<I', bgl.read(4))
                            if c=='LODE':
                                ende=size+bgl.tell()
                                (lod,)=unpack('<I', bgl.read(4))
                                while bgl.tell()<ende:
                                    c=bgl.read(4)
                                    (size,)=unpack('<I', bgl.read(4))
                                    if c=='PART':
                                        (typ,scene,material,verb,voff,vcount,ioff,icount,unk)=unpack('<9I', bgl.read(36))
                                        #print lod, typ,scene,material,verb,voff,vcount,ioff,icount,unk
                                        assert (typ==1)
                                        maxlod=max(lod,maxlod)
                                        (child, peer, finalmatrix, parent)=scen[scene]
                                        while parent!=-1:
                                            (child, peer, thismatrix, parent)=scen[parent]
                                            finalmatrix=finalmatrix*thismatrix
                                        if not lod in data: data[lod]=[]
                                        data[lod].append((mat[material], vt[verb][voff:voff+vcount], idx[ioff:ioff+icount], finalmatrix))
                                        partno+=1
                                    else:
                                        bgl.seek(size,1)
                            else:
                                bgl.seek(size,1)
                    else:
                        bgl.seek(size,1)
            else:
                bgl.seek(size,1)

        # Sort data by texture. Only use highest LOD
        suffix=0
        suffixstr=''
        sorted={}
        libname=asciify(libname)
        for ((d,s,sp,e,texture),vt,idx,matrix) in data[maxlod]:
            # handle multiple objects with same name
            while True:
                if suffix: suffixstr='-%d' % suffix
                if texture:
                    (tex,lit)=texture
                    if tex:
                        (fname,ext)=splitext(basename(tex))
                        fname="%s%s-%s" % (libname, suffixstr, asciify(fname))
                    elif lit:
                        (fname,ext)=splitext(basename(lit))
                        fname="%s%s-%s" % (libname, suffixstr, asciify(fname))
                else:
                    fname="%s%s" % (libname, suffixstr)
                if fname in output.objdat:
                    suffix+=1
                else:
                    break
            if not texture in sorted: sorted[texture]=[]
            sorted[texture].append(((d,s,sp,e),vt,idx,matrix))

        bname=libname+suffixstr
        objs=[]

        for texture in sorted:
            objvt=[]
            objidx=[]
            mattri=[]
            for ((d,s,e,p),vt,idx,matrix) in sorted[texture]:
                vbase=len(objvt)
                ibase=len(objidx)
                if texture:
                    (tex,lit)=texture
                    if tex:
                        (fname,ext)=splitext(basename(tex))
                    else:
                        (fname,ext)=splitext(basename(lit))
                    fname="%s-%s" % (bname, asciify(fname))
                    for (x,y,z, nx,ny,nz, tu,tv) in vt:
                        (x,y,z)=matrix.transform(x,y,z)
                        (nx,ny,nz)=matrix.rotate(nx,ny,nz)
                        objvt.append((x,y,-z, nx,ny,-nz, tu,tv))
                else:
                    tex=output.palettetex
                    lit=None
                    fname=bname
                    (pu,pv)=rgb2uv(d)
                    for (x,y,z, nx,ny,nz, tu,tv) in vt:
                        (x,y,z)=matrix.transform(x,y,z)
                        (nx,ny,nz)=matrix.rotate(nx,ny,nz)
                        objvt.append((x,y,-z, nx,ny,-nz, pu,pv))
                if not vbase:
                    objidx.extend(idx)	# common case
                else:
                    objidx.extend([vbase+i for i in idx])
                mattri.append(((d,s,e,p), ibase, len(objidx)-ibase, False))
                              
            objs.append(Object(fname+'.obj', comment, tex, lit, None, [], [], [], [], objvt, objidx, mattri, 0))

        # Add objs to library with one name
        if objs: output.objdat[libname]=objs
