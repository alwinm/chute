# Code for processing values in shells, split by blocks for memory footprint

import h5py
import numpy as n
import itertools
import time
import resource



size = 512

time.t0 = time.time()

def timer(string):
    t = time.time()
    dt = t - time.t0
    print(string,dt,flush=True)
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f'{mem}KB\n{mem/1024}MB\n{mem/1024/1024}GB',flush=True)
    time.t0 = t
    return dt

def mem():
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(f'{mem}KB\n{mem/1024}MB\n{mem/1024/1024}GB',flush=True)

def cie_cool(rho,t):
    # dE_cgs = cool * dt * TIME_UNIT
    # cool = de/dt in cgs units
    # t_cool = de/cool = n*kb*T/(gamma-1.0) / cool

    lt = n.log10(t)
    result = n.zeros(t.shape)

    mask = (lt >= 4.0) & (lt < 5.9)
    if n.any(mask):
        result[mask] = 10**(-1.3*(lt[mask]-5.25)**2 - 21.25)

    mask = (lt >= 5.9) & (lt < 7.4)
    if n.any(mask):
        result[mask] = 10**(0.7*(lt[mask]-7.1)**2 - 22.8)

    mask = (lt >= 7.4)
    if n.any(mask):
        result[mask] = 10**(0.45*lt[mask] - 26.065)

    return rho*rho*result


def processblock(f,center,dx,rbins,x,y,z):
    length_unit_cgs = 3.086e21
    time_unit_cgs = 3.154e10
    mass_unit_cgs = 1.989e33
    density_unit_cgs = (mass_unit_cgs/(length_unit_cgs)**3)
    velocity_unit_cgs = length_unit_cgs/time_unit_cgs
    energy_density_unit_cgs = density_unit_cgs * (velocity_unit_cgs)**2

    # Create chunk selection

    # Infer shape
    shape = f['density'].shape

    # Set xmin and xmax and selection
    xmin = x*size
    xmax = min((x+1)*size,shape[0])
    ymin = y*size
    ymax = min((y+1)*size,shape[1])
    zmin = z*size
    zmax = min((z+1)*size,shape[2])
    maxs = [xmax,ymax,zmax]
    select = tuple((slice(xmin,xmax),slice(ymin,ymax),slice(zmin,zmax)))

    density = f['density'][select]#.reshape(-1)
    gase = f['GasEnergy'][select]#.reshape(-1)
    raw_temp = gase/density

    # Compute temperature conversion
    gamma = f.attrs['gamma'][0]
    mu = 0.6
    kelvin = 1.15831413e14 # proton mass * (kpc/kyr)^2 / boltzmann constant
    tconvert = (mu*(gamma-1.0)*kelvin)
    temperature = raw_temp * tconvert

    values_cgs = {}
    density_cgs = density * density_unit_cgs
    values_cgs['density'] = density_cgs
    values_cgs['cooling'] = cie_cool(density_cgs,temperature)
    values_cgs['energy_density'] = gase * energy_density_unit_cgs
    values_cgs['cells'] = 1.0

    # Compute distance
    centerx,centery,centerz = center
    cx = (dx*(n.arange(xmin,xmax) - centerx))**2
    cy = (dx*(n.arange(ymin,ymax) - centery))**2
    cz = (dx*(n.arange(zmin,zmax) - centerz))**2
    distance = n.sqrt(cx[:,None,None] + cy[None,:,None] + cz[None,None,:])#.reshape(-1)

    masks = {}
    above = (cz[None,None,:] > 1)
    polar = (cz[None,None,:] > n.sqrt(3)*(cx[:,None,None] + cy[None,:,None]))
    masks['cold'] = above & (density > 0) & (temperature < 2e4)
    masks['hot'] = above & (density > 0) & (temperature > 5e5)
    masks['cold_polar'] = masks['cold'] & polar
    masks['hot_polar'] = masks['hot'] & polar




    output = {}
    for key1 in values_cgs:
        for key2 in masks:
            output[key1+'_'+key2] = n.histogram(distance,bins=rbins,weights=values_cgs[key1]*masks[key2])[0]
    return output

def process(filename,center,dx,rbins):
    # calculate radius in units of cells
    # in a [256,256,256] array, center would be (256-1)/2
    f = h5py.File(filename,'r')
    mastershape = f['density'].shape

    xl = int((mastershape[0]+size-1)/size)
    yl = int((mastershape[1]+size-1)/size)
    zl = int((mastershape[2]+size-1)/size)

    result = {}
    timer('Init')
    for x,y,z in itertools.product(range(xl),range(yl),range(zl)):
        output = processblock(f,center,dx,rbins,x,y,z)
        timer('Block: {} {} {} Seconds: '.format(x,y,z))
        for key in output:
            if key not in result:
                result[key] = output[key]
            else:
                result[key] += output[key]
    result['distance'] = rbins
    return result
