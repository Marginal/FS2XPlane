ppm=file("palette.ppm","wt")
ppm.write("P3\n64 64\n15\n")
for b1 in range(12,-4,-4):
    for g in range(15,-1,-1):
        for b2 in range(4):
            for r in range(16):
                ppm.write("%d %d %d\t" % (r, g, b1+b2))
        ppm.write("\n")
