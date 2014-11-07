from convutil import AptNav, D, T, E

def atclayout(allnodes, alllinks, runways, helipads, coms, aptdat, ident):

    if not runways: return	# no runways!

    # Assign ids to used nodes
    nextid=1
    for l in alllinks:
        if l.type in ['RUNWAY','TAXI','PATH']:
            for n in l.nodes:
                if not n.id:
                    n.id=nextid
                    nextid+=1

    # Try to find arrival and departure com frequencies
    comapp=comdep=comtwr=comany=None
    for com in coms:
        if com.type=='APPROACH' and not comapp:
            comapp=int(float(com.frequency)*100)
        elif com.type=='DEPARTURE' and not comdep:
            comdep=int(float(com.frequency)*100)
        elif com.type=='TOWER' and not comtwr:
            comtwr=int(float(com.frequency)*100)
        else:
            comany=int(float(com.frequency)*100)
    comapp=comapp or comtwr or comany or '11800'
    comdep=comdep or comtwr or comany or '11800'

    aptdat.append(AptNav(1000, 'Default Flow'))
    aptdat.append(AptNav(1001, '%s 000 359 999' % ident))	# wind
    aptdat.append(AptNav(1002, '%s 0' % ident))			# ceiling min
    aptdat.append(AptNav(1003, '%s 0' % ident))			# visibility min
    aptdat.append(AptNav(1004, '0000 2400'))			# Zulu hours

    # Find a VFR pattern. Choose first operational runway.
    for runway in runways:
        if T(runway, 'primaryLanding') and T(runway, 'primaryTakeoff'):
            aptdat.append(AptNav(1101, '%s %s' % (
                        runway.numbers[0], runway.primaryPattern.lower())))
            break
        elif T(runway, 'secondaryLanding') and T(runway, 'secondaryTakeoff'):
            aptdat.append(AptNav(1101, '%s %s' % (
                        runway.numbers[1], runway.secondaryPattern.lower())))
            break
        
    for runway in runways:
        number=['XXX','XXX']
        operations=[None,None]
        names=[None,None]
        coms=[None,None]
        if T(runway, 'primaryLanding') and T(runway, 'primaryTakeoff'):
            operations[0]='arrivals|departures'
            names[0]='Runway'
            coms[0]=comapp
        elif T(runway, 'primaryLanding'):
            operations[0]='arrivals'
            names[0]='Arrivals'
            coms[0]=comapp
        elif T(runway, 'primaryTakeoff'):
            operations[0]='departures'
            names[0]='Departures'
            coms[0]=comdep
        if T(runway, 'secondaryLanding') and T(runway, 'secondaryTakeoff'):
            operations[1]='arrivals|departures'
            names[1]='Runway'
            coms[1]=comapp
        elif T(runway, 'secondaryLanding'):
            operations[1]='arrivals'
            names[1]='Arrivals'
            coms[1]=comapp
        elif T(runway, 'secondaryTakeoff'):
            operations[1]='departures'
            names[1]='Departures'
            coms[1]=comdep
        for end in [0,1]:
            if operations[end]:
                aptdat.append(AptNav(1100, '%s %s %s heavy|jets|turboprops|props 000359 000359 %s %s' % (
                            runway.numbers[end], coms[end], operations[end], names[end], runway.numbers[end])))

    # Helipads
    if False:	# According to WED we don't do this
        hno=0
        for helipad in helipads:
            hno+=1
            if not T(helipad, 'closed'):
                aptdat.append(AptNav(1100, 'H%0d %s %s helos 000359 000359 %s %0d' % (
                            hno, comapp, 'arrivals|departures', 'Helipad', hno)))

    # Node list
    aptdat.append(AptNav(1200, ''))
    for n in allnodes:
        if n.id:
            # XXX TODO: What is the type field for?
            aptdat.append(AptNav(1201, "%12.8f %13.8f %s %4d %s" % (
                        n.loc.lat, n.loc.lon, 'both', n.id, n.name)))

    for t in ['RUNWAY','TAXI','PATH']:
        for l in alllinks:
            if l.type==t:
                name=' '.join(l.name.split(' ')[1:])
                aptdat.append(AptNav(1202, "%4d %4d %s %s %s" % (
                            l.nodes[0].id, l.nodes[1].id, 'twoway', t=='RUNWAY' and 'runway' or 'taxiway', name)))
                if l.hotness:
                    aptdat.append(AptNav(1204, "departure %s" % l.hotness))
                    aptdat.append(AptNav(1204, "arrival   %s" % l.hotness))
