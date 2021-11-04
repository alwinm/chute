# Process cholla stdout


import numpy as n

import pylab as p

def tracker(filename):
    with open(filename,'r') as ofile:
        data = ofile.readlines()
    llist = [line[8:].split() for line in data if line[:8] == 'Tracker:']

    return n.array(llist).astype(float)

def cooling(filename):
    key = 'cooling energy:'
    with open(filename,'r') as ofile:
        data = ofile.readlines()
    llist = [line.split(key)[1].split() for line in data if line.startswith(key)]
    return n.array(llist).astype(float)

def energyplot(filename):
    cdata = cooling(filename)
    tdata = tracker(filename)

    total_cool = cdata[:,0]
    semi_cool = cdata[:,1]

    sne_energy = tdata[:,3]

    time = tdata[:,0]
    cti = min(len(time),len(cdata))
    p.plot(time[:cti],total_cool[:cti],label='Total Cool')
    p.plot(time[:cti],semi_cool[:cti],label='Near')
    p.plot(time,sne_energy,label='SNe')
    p.legend()
    p.yscale('log')
    p.show()
    
def dtplot(filename):
    data = tracker(filename)
    t = data[:,0]
    dt = data[:,1]
    p.subplot(1,2,1)
    p.plot(t,dt)
    p.yscale('log')
    p.subplot(1,2,2)
    p.plot(t,dt,'.')
    p.yscale('log')
    p.show()
