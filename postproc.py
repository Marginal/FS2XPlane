from os.path import join, pardir, dirname, normpath
from sys import argv

h=open(argv[1], 'rU')
outpath=normpath(join(dirname(argv[1]), pardir))
edges=bezpt=None
taxiway=False

for line in h:
    c=line.split()
    if not c: continue
    if c[0]=='I': continue
    code=int(c[0])
    
    if code==1:
        ident=c[4]
        print ident
        if edges: edges.close()
        if bezpt: bezpt.close()
        edges=bezpt=None
        taxiway=False

    elif code==110 and c[-1]=='Taxiway':	# exclude Aprons
        taxiway=True

    elif taxiway and code in range(111,115):
        if not edges: edges=open(join(outpath, ident+"_edges.txt"), 'at')
        edges.write("%s\t%s\n" % (c[2], c[1]))
        if code>=113: edges.write("\n")
        if code in [112,114]:
            if not bezpt: bezpt=open(join(outpath, ident+"_bezier.txt"), 'at')
            bezpt.write("%s\t%s\n" % (c[4], c[3]))
            if code==114: bezpt.write("\n")

    else:
        taxiway=False
    
if edges: edges.close()
if bezpt: bezpt.close()
h.close()
