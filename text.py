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


outdir = 'out_scalar/kh_text/'

def timer(string):
    print(string,time.time() - time.t0,' seconds')
    time.t0 = time.time()

def printf(*args,**kwargs):
    print(*args,**kwargs,flush=True)

def render(string=r'$128\sqrt{\rm{e}980}$'):
    p.figure(figsize=(10,10))
    p.text(0.5,0.5,string,fontdict={'size':128,'family':'sans-serif','color': 'black', 'weight':'heavy', 'ha':'center', 'va':'center'})
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

def make_hdf5(string=r'$128\sqrt{\rm{e}980}$',dnameout=outdir):
    array = render(string)

    nx,ny = array.shape

    filename = dnameout+'/0.h5.0'

    if os.path.isfile(filename):
        os.remove(filename)

    fileout = h5py.File(filename, 'a')
    fileout.attrs['gamma'] = [5./3.]
    fileout.attrs['t'] = [0.0]
    fileout.attrs['dt'] = [1e-3]
    fileout.attrs['n_step'] = [0]
    dtype = n.float64

    ones = n.ones(array.shape)
    zeros = n.zeros(array.shape)

    mom = zeros.copy()

    
    mom[:nx//2,:] = 1.0
    

    density = ones
    density[nx//2:,:] = 4.0
    
    ge = ones
    ge[:nx//2,:] += 0.2*(array == 0.0)[:nx//2,:]

    fileout.create_dataset('density', (nx, ny), dtype=dtype, data=density)
    fileout.create_dataset('momentum_x', (nx, ny), dtype=dtype, data=zeros)
    fileout.create_dataset('momentum_y', (nx, ny), dtype=dtype, data=mom)
    fileout.create_dataset('momentum_z', (nx, ny), dtype=dtype, data=zeros)
    fileout.create_dataset('GasEnergy', (nx, ny), dtype=dtype, data=ge)

    fileout.create_dataset('Energy', (nx, ny), dtype=dtype, data= ge + 0.5 * mom**2 / density)
    fileout.create_dataset('scalar0', (nx, ny), dtype=dtype, data=array)
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

def run_test(binary,odir,test):
    pdir = 'examples'
    outdir = f'{odir}/{test[2]}/'
    if not os.path.isdir(outdir):
        os.system('mkdir -p ' + outdir)
    command = f'{binary} {pdir}{test[0]} {test[1]} outdir={odir}/{test[2]}/'

    printf(command)
    os.system(command)

def run_read_grid(nx,ny,nfile=0,tout=0.4):
    typename = 'scalar'
    bins = os.listdir('temp')
    match = [string for string in bins if typename in string]
    if not match:
        make_scalar()
        bins = os.listdir('temp')
        match = [string for string in bins if typename in string]

    if not match:
        return

    testargs = [f'tout={tout}',
                'outstep=0.002',
                f'nx={nx}',
                f'ny={ny}',
                'nz=1',
                'init=Read_Grid',
                f'nfile={nfile}',
                f'indir={outdir}']
    # periodic in x and y directions
    test = ['/2D/KH_discontinuous_2D.txt',' '.join(testargs),'kh_text']
    run_test(f'temp/{match[0]}','out_'+typename,test)

def plotfile(filename):
    f = h5py.File(filename,'r')
    p.imshow(f['scalar0'][:],cmap='Blues')
    p.axis('off')


def plots(start=0):
    basedir = outdir
    
    i = start

    while True:
        i += 1
        filename = f'{basedir}{i}.h5.0'
        if os.path.isfile(filename):
            print('Plotting: ',filename)            
            p.clf()
            plotfile(filename)            
            p.savefig(f'{basedir}{i:03}.png')
        else:
            break


def main():

    nx,ny = make_hdf5()
    run_read_grid(nx,ny)
    plots()
    # read and plot

# default behavior:
# runs tests
# cats tests
# runs hdiff on tests

#run_tests()
#cat()
#hdiff()
#timer('run_tests finished:')
#main()
#plots()
