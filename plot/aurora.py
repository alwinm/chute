import numpy as n
import h5py
import matplotlib.colors as mco
import pylab as p
def panel(array):
    p.pcolormesh(array.transpose(),norm=mco.LogNorm())
    p.colorbar()

def plot(i):
    slicefile = str(i)+'_slice.h5'
    projfile = str(i)+'_proj.h5'

    with h5py.File(projfile,'r') as pfile:
        p_xy = pfile['d_xy'][:]
        p_xz = pfile['d_xz'][:]


    with h5py.File(slicefile,'r') as sfile:
        s_xy = sfile['d_xy'][:]
        s_xz = sfile['d_xz'][:]
        s_yz = sfile['d_yz'][:]

    sfile = h5py.File(slicefile,'r')
    
    nh = 2
    nw = 3
    ni = 1
    p.figure(figsize=(15,10))
    
    p.subplot(nh,nw,ni)
    ni += 1
    panel(s_xy)
    p.xlabel('X')
    p.ylabel('Y (Slices)')

    p.subplot(nh,nw,ni)
    ni += 1
    panel(s_xz)
    p.xlabel('X')
    p.ylabel('Z')

    p.subplot(nh,nw,ni)
    ni += 1
    panel(s_yz)
    p.xlabel('Y')
    p.ylabel('Z')

    p.subplot(nh,nw,ni)
    ni += 1
    panel(p_xy)
    p.xlabel('X')
    p.ylabel('Y (Projection)')

    p.subplot(nh,nw,ni)
    ni += 1
    panel(p_xz)
    p.xlabel('X')
    p.ylabel('Z')




    
    p.savefig(f'aurora{i:03d}.png')
    





    

    

    
