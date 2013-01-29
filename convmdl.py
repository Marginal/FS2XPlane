from os import listdir
from os.path import basename, dirname, join, normpath, pardir, splitext
from struct import unpack

from convbgl import findtex, maketexdict
from convutil import asciify, rgb2uv, Matrix, Object, Material, Texture


# handle FSX format library MDL file
class ProcScen:
    def __init__(self, bgl, enda, scale, libname, srcfile, texdir, output):

        self.old=False	# Old style scenery found and skipped
        self.rrt=False	# Old style runways/roads found and skipped
        self.anim=False	# Animations found and skipped

        assert(scale==1)	# new-style objects are scaled when placed

        comment="object %s in file %s" % (libname,asciify(basename(srcfile),False))

        tex=[]
        mattex=[]
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
                        # http://www.fsdeveloper.com/wiki/index.php?title=MDL_file_format_(FSX)#MATE
                        for i in range(0,size,120):
                            (flags1,flags2,diffuse,detail,normal,specular,emissive,reflection,fresnel,dr,dg,db,da,sr,sg,sb,sa,sp,ds,normalscale,recflectionscale,po,power,bloomfloor,ambientscale,srcblend,dstblend,alphafunc,alphathreshhold,zwritealpha)=unpack('<9I16f3I2f', bgl.read(120))
                            # Get texture names
                            diffuse   =(flags1 & Material.FSX_MAT_HAS_DIFFUSE) and tex[diffuse] or None
                            emissive  =(flags1 & Material.FSX_MAT_HAS_EMISSIVE) and tex[emissive] or None
                            if output.xpver<=10:
                                normal=specular=reflection=None	# Not supported in<=10, so no point doing lookup
                            else:
                                specular  =(flags1 & Material.FSX_MAT_HAS_SPECULAR) and tex[specular] or None
                                normal    =(flags1 & Material.FSX_MAT_HAS_NORMAL) and tex[normal] or None
                                reflection=(flags1 & Material.FSX_MAT_HAS_REFLECTION) and tex[reflection] or None
                            # Get texture filenames
                            if diffuse:   diffuse   =findtex(diffuse, texdir, output.addtexdir)
                            if emissive:  emissive  =findtex(emissive, texdir, output.addtexdir)
                            if specular:  specular  =findtex(specular, texdir, output.addtexdir)
                            if normal:    normal    =findtex(normal, texdir, output.addtexdir)
                            if reflection:reflection=findtex(reflection, texdir, output.addtexdir)

                            t=(diffuse or emissive) and Texture(output.xpver, diffuse, emissive, specular, normal, reflection) or None
                            m=Material(output.xpver,
                                       (dr,dg,db),
                                       (flags1 & Material.FSX_MAT_SPECULAR) and not specular and ((sr!=sg or sr!=sb or sr<0.9) and (sr,sg,sb)!=(0,0,0)) and [sr,sg,sb] or None,
                                       False,	# Poly
                                       flags2&Material.FSX_MAT_DOUBLE_SIDED != 0,
                                       flags1&Material.FSX_MAT_ZTEST_ALPHA and alphafunc in [Material.FSX_MAT_ALPHA_TEST_GREATER,Material.FSX_MAT_ALPHA_TEST_GREATER_EQUAL] and alphathreshhold/255 or None,
                                       not diffuse and ((flags1 & Material.FSX_MAT_SPECULAR) and (sr,sg,sb)!=(0,0,0)) and True,
                                       flags1&Material.FSX_MAT_NO_SHADOW != 0)
                            mattex.append((m,t))
                        if __debug__:
                            if output.debug:
                                output.debug.write("Materials %d\n" % len(mattex))
                                for i in range(len(mattex)):
                                    output.debug.write("%3d:\t%s\t%s\n" % (i, mattex[i][0], mattex[i][1]))
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
                        if __debug__:
                            if output.debug:
                                output.debug.write("Matrices %d\n" % len(matrix))
                                for i in range(len(matrix)): output.debug.write("%s = %d\n" % (matrix[i], i))
                    elif c=='AMAP':
                        for i in range(0,size,8):
                            (a,b)=unpack('<2I',bgl.read(8))
                            amap.append(b)
                        if __debug__:
                            if output.debug:
                                output.debug.write("Animation map %d\n" % len(amap))
                                for i in range(len(amap)):
                                    output.debug.write("%2d: %2d\n" % (i, amap[i]))
                    elif c=='SCEN':
                        # Assumed to be after TRAN and AMAP sections
                        count=size/8
                        for i in range(count):
                            (child,peer,offset,unk)=unpack('<4h',bgl.read(8))
                            scen.append((child,peer,offset,-1))
                        # Invert Child/Peer pointers to get parents
                        for i in range(count):
                            (child, peer, thisoff, parent)=scen[i]
                            if child!=-1:	# child's parent is me
                                (xchild, xpeer, xoff, xparent)=scen[child]
                                scen[child]=(xchild, xpeer, xoff, i)
                            if peer!=-1:	# peer's parent is my parent
                                (xchild, xpeer, xoff, xparent)=scen[peer]
                                scen[peer]=(xchild, xpeer, xoff, parent)
                        # Replace AMAP offsets with matrix
                        if __debug__:
                            if output.debug: output.debug.write("Scene Graph %d\n" % len(scen))
                        for i in range(count):
                            (child, peer, offset, parent)=scen[i]
                            scen[i]=(child, peer, matrix[amap[offset/8]], parent)
                            if __debug__:
                                if output.debug: output.debug.write("%2d: %2d %2d %2d %2d\n" % (i, child, peer, parent, offset/8))
                    elif c=='LODT':
                        endt=size+bgl.tell()
                        partno=0
                        maxlod=0
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
                                        assert (typ==1)
                                        maxlod=max(lod,maxlod)
                                        (child, peer, finalmatrix, parent)=scen[scene]
                                        if __debug__:
                                            if output.debug:
                                                output.debug.write("LOD %4d: scene %d verb %d material %d tris %d voff %d vcount %d ioff %d icount %d\n" % (lod, scene, verb, material, icount/3, voff, vcount, ioff, icount))

                                        while parent!=-1:
                                            (child, peer, thismatrix, parent)=scen[parent]
                                            finalmatrix=finalmatrix*thismatrix
                                        if not lod in data: data[lod]=[]
                                        data[lod].append((mattex[material][0], mattex[material][1], vt[verb][voff:voff+vcount], idx[ioff:ioff+icount], finalmatrix))
                                        partno+=1
                                    else:
                                        bgl.seek(size,1)
                            else:
                                bgl.seek(size,1)
                    else:
                        bgl.seek(size,1)
            else:
                bgl.seek(size,1)

        # Only interested in highest LOD
        objs={}	# objs by texture
        for (m,t,vt,idx,matrix) in data[maxlod]:
            if __debug__:
                if output.debug: output.debug.write("%s\n%s\n" % (t, matrix))
            objvt=[]
            nrmmatrix=matrix.adjoint()
            if t:
                assert not t.s and not t.n and not t.r	# Bunching scheme will need re-work
                for (x,y,z, nx,ny,nz, tu,tv) in vt:
                    (x,y,z)=matrix.transform(x,y,z)
                    (nx,ny,nz)=nrmmatrix.rotateAndNormalize(nx,ny,nz)
                    objvt.append((x,y,-z, nx,ny,-nz, tu,tv))
            else:
                # replace material with palette texture
                (pu,pv)=rgb2uv(m.d)
                for (x,y,z, nx,ny,nz, tu,tv) in vt:
                    (x,y,z)=matrix.transform(x,y,z)
                    (nx,ny,nz)=nrmmatrix.rotateAndNormalize(nx,ny,nz)
                    objvt.append((x,y,-z, nx,ny,-nz, pu,pv))
            if t in objs:
                obj=objs[t]
                if t and t.e: obj.tex.e=t.e	# Because we don't compare on emissive
            else:
                objs[t]=obj=Object(libname, comment, t, None)
            obj.addgeometry(m, objvt, idx)

        # Add objs to library with one name
        if objs: output.objdat[libname]=objs.values()
