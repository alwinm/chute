import os
import numpy as n
import h5py
import matplotlib.colors as mco
import pylab as p


def plot(i,log_bool=True,field='d',slicedir='./',projdir='./'):
    def panel(array):
        if array is None:
            return
        norm0 = None
        if log_bool:
            norm0 = mco.LogNorm()


        vmax = 10**n.ceil(n.log10(n.max(array)))
        #vmax = n.max(array)
        vmin = 1e-10 * vmax
        p.pcolormesh(array.transpose(),norm=norm0,vmin=vmin,vmax=vmax) 
        p.colorbar()

    def get(hf,key):
        if key in hf:
            return hf[key][:]
        else:
            return None
    
    slicefile = slicedir+str(i)+'_slice.h5'
    projfile = projdir+str(i)+'_proj.h5'

    p_xy = p_xz = s_xy = s_xz = s_yz = None
    
    if os.path.isfile(projfile):
        with h5py.File(projfile,'r') as pfile:
            p_xy = get(pfile,field+'_xy')
            p_xz = get(pfile,field+'_xz')

    if os.path.isfile(slicefile):        
        with h5py.File(slicefile,'r') as sfile:
            s_xy = get(sfile,field+'_xy')
            s_xz = get(sfile,field+'_xz')
            s_yz = get(sfile,field+'_yz')
        
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

    p.subplot(nh,nw,ni)
    ni += 1
    p.title(str(i))
    
    if not os.path.isdir('aurora'):
        os.mkdir('aurora')
    
    savefile = f'aurora/aurora_Field{field}_Log{log_bool}_{i:03d}.png'
    print('Saving:',savefile)
    p.savefig(savefile)
    #if log_bool:
    #    p.savefig(f'aurora_{i:03d}.png')
    #else:
    #    p.savefig(f'boreal_{i:03d}.png')
    p.close()





    

    

    
