import os
import numpy as n
import h5py
import matplotlib
matplotlib.use('agg')
import matplotlib.colors as mco
import pylab
p = pylab

def threeview(array,nh,nw,ni, function=n.sum, norm=None):
    dims = ['X','Y','Z']
    for i in range(3):
        pylab.subplot(nh,nw,ni+i,aspect='equal')
        pylab.pcolormesh(function(array, axis=i).transpose(),norm=norm)
        pylab.colorbar()
        labels = list(range(3))
        labels.remove(i)
        pylab.xlabel(dims[labels[0]])
        pylab.ylabel(dims[labels[1]])


# Strategy:

# Max density
# Sum density
# Sum mask

def plot(i, griddir='./grid/'):
    gridfile = griddir + str(i) + '.h5'
    outdir = './jericho/'
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    with h5py.File(gridfile,'r') as f:                                          
        density = n.array(f['density'])                                         
        gase = n.array(f['GasEnergy'])                                          
        head = f.attrs                                                          
                                                                                
        gamma = head['gamma'][0]  
    mu = 0.6                                                                    
    to_kelvin = 1.15831413e14 # proton mass * (kpc/kyr)^2 / boltzmann constant  
    # gase/density has units of v^2                                             
    temperature = (mu*(gamma-1.0)*to_kelvin)*(gase/density) 
    to_pcc = 4.04768956e-8                                                      
    #solar mass / (kpc)^3 / proton mass in cm^-3                                
    n_cgs = density * (to_pcc / mu)

    mask = (temperature < 1e3) * (n_cgs < 1.0)

    p.figure(figsize=(8,8))
    nh = 3
    nw = 3
    threeview(n_cgs, nh, nw, 1, function = n.max, norm=mco.LogNorm())
    threeview(n_cgs, nh, nw, 4, norm=mco.LogNorm())
    threeview(mask , nh, nw, 7)
    
    p.tight_layout()





    savefile = f'{outdir}jericho_{i:03d}.png'
    print('Saving:', savefile)    
    p.savefig(savefile)
