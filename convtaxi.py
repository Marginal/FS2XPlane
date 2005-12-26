from convutil import Object

def maketaxi(label):

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
            ']':(1016,1023)}
            
    row=0	# 0=dir (b on y), 1=rwy (w on r), 2=lcn (y on b)
    addbracket=False
    addspace=False
    width=0
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
                if array:
                    (oldrow, start, end)=array[-1]
                    array[-1]=(oldrow,start-3, end)
            elif c=='[':
                addbracket=True
            elif c==']':
                if array:
                    (oldrow, start, end)=array[-1]
                    if addspace:
                        array[-1]=(oldrow, start, end+9)
                        addspace=False
                    else:
                        array[-1]=(oldrow, start, end+6)
            else:
                if c in '0123456789':
                    start=32*int(c)+838
                elif c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                    start=32*ord(c)-2074
                end=start+20
                if addspace:
                    start=start-3
                    addspace=False
                if addbracket:
                    start=start-6
                    addbracket=False
                array.append((row, start, end))

        elif c in drrmap:
            (start,end)=drrmap[c]
            if addspace:
                start=start-2
                addspace=False
            array.append((row, start, end))
        elif c==' ':
            addspace=True

    width=0
    for (row, start, end) in array:
        width=width+end-start
    height=1.0
    depth=0.15
    pix2m=0.03
    left=width/2

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
            row=3

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

    fname=label
    fname.replace('/',',')
    fname.replace('\\','.')
    for c in ':*?"<>|':
        fname=fname.replace(c,'_')
    fname="TaxiwaySign-%s.obj" % fname
    return Object(fname, "TaxiwaySign "+label,
                  '.\\Taxi2.png', [], [], vt, idx,
                  [([(1,1,1),(0,0,0),(0,0,0)],0,frameilen),
                   ([(1,1,1),(0,0,0),(1,1,1)],frameilen,len(idx)-frameilen)])

