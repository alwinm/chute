# Run cholla on text, render text

# Compile scalar
# Set up restart file
# Launch cholla with read_grid
# Run cholla
# Make movie from scalar
import matplotlib
matplotlib.use('agg')
import pylab as p
import numpy as n

import h5py

import os
import sys
import time
import chute.cat as cc

time.t0 = time.time()

OKCYAN = '\033[96m'
ENDC = '\033[0m'


def timer(string):
    print(string,time.time() - time.t0,' seconds')
    time.t0 = time.time()

def printf(*args,**kwargs):
    print(*args,**kwargs,flush=True)

def render(string=r'$128\sqrt{\rm{e}980}$'):
    p.text(0.5,0.5,string,fontdict={'size':64,'family':'sans-serif','color': 'black', 'weight':'heavy', 'ha':'center', 'va':'center'})
    p.axis('off')
    p.tight_layout()
    #p.ylim([0.25,0.75])
    #p.xlim([-1.0,2.0])
    p.gca().set_aspect('equal')
    
    fig = p.gcf()

    fig.canvas.draw()

    width,height = fig.canvas.get_width_height()
    array = n.fromstring(fig.canvas.tostring_rgb(),dtype=n.uint8).reshape((height,width,3))[:,:,0]
    return array

def make_hdf5(string=r'$128\sqrt{\rm{e}980}$',dnameout='temp/'):
    fileout = h5py.File(dnameout+'/0.h5.0', 'a')
    fileout.attrs['gamma'] = [5./3.]
    fileout.attrs['t'] = [0.0]
    fileout.attrs['dt'] = [1e-3]
    fileout.attrs['n_step'] = [0]
    dtype = n.float64

    array = render(string)

    nx,ny = array.shape

    ones = n.ones(array.shape)
    zeros = n.zeros(array.shape)

    mom_x = zeros.copy()

    mom_x[:,ny//2:] = 1.0
    
    density = ones
    ge = ones
    
    fileout.create_dataset('density', (nx, ny), dtype=dtype, data=density)
    fileout.create_dataset('momentum_x', (nx, ny), dtype=dtype, data=mom_x)    
    fileout.create_dataset('momentum_y', (nx, ny), dtype=dtype, data=zeros)
    fileout.create_dataset('momentum_z', (nx, ny), dtype=dtype, data=zeros)
    fileout.create_dataset('GasEnergy', (nx, ny), dtype=dtype, data=ge)

    fileout.create_dataset('Energy', (nx, ny), dtype=dtype, data= ge + 0.5 * mom_x**2 / density)    

    fileout.close()
    return nx,ny

    

def make_scalar():
    # creates the make type scalar if it does not exist
    infile = 'builds/make.type.hydro'
    outfile = 'builds/make.type.scalar'
    with open(infile,'r') as ofile:
        data = ofile.readlines()

    with open(outfile,'w') as ofile:

        for line in data:
            ofile.write(line)
        ofile.write('DFLAGS += -DSCALAR \n')
        ofile.write('DFLAGS += -DBASIC_SCALAR \n')        

    if not os.path.isdir('temp'):
        os.mkdir('temp')
    
    typename = 'scalar'
    os.system('make clean')
    os.system('make -j TYPE={}'.format(typename))
    os.system('mv bin/* temp/.')        


def run_read_grid(nx,ny):
    typename = 'scalar'
    bins = os.listdir('temp')
    match = [string for string in bins if typename in string]
    if not match:
        return

    testargs = ['tout=2.0',
                'outstep=2.0',
                f'nx={nx}',
                f'ny={ny}',
                'nz=1',
                'init=Read_Grid',
                'nfile=0',
                'indir=temp/']
    # periodic in x and y directions
    test = ['/2D/KH_discontinuous_2D.txt',' '.join(testargs),'kh_text']
    run_test(f'temp/{match[0]}','out_'+typename,test)    

def plotfile(filename):
    f = h5py.File(filename,'r')
    p.imshow(f['scalar0'][:])
    p.savefig(filename+'.png')
    

def main():
    make_scalar()
    nx,ny = make_hdf5()
    run_read_grid(nx,ny)
    plotfile('temp/0.h5.1')
    # read and plot
    
# default behavior:
# runs tests
# cats tests
# runs hdiff on tests

#run_tests()
#cat()
#hdiff()
#timer('run_tests finished:')
