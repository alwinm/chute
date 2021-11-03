#!/usr/bin/env python3
# Example file for concatenating 3D hdf5 datasets

import h5py
import numpy as np
import os
import sys
import resource
#gb = int(1e9)
#limit = int(8*gb)
#resource.setrlimit(resource.RLIMIT_AS,(limit,limit))
if len(sys.argv) < 2:
  print('Command line argument required, either integer or filename to provide prefix')
  exit()
  
argv = sys.argv[1]

# Determine prefix
if 'h5' in argv:
  preprefix = argv.split('.h5')[0]
  ns = int(preprefix.split('/')[-1])
  prefix = preprefix +'.h5'
  
else:
  prefix = './{}.h5'.format(argv)
  ns = int(argv)

# For now only process 1 file
ne = ns

# Check existing 
firstfile = prefix+'.0'
if not os.path.isfile(prefix+'.0'):
  print(prefix+'.0 is missing')
  exit()

# Set dirnames
dnamein = os.path.dirname(firstfile)+'/'
dnameout = os.path.dirname(firstfile) + '/'

print('Prefix: {} ns: {} ne: {} dnamein: {} dnameout: {}'.format(prefix,ns,ne,dnamein, dnameout))

#n_proc = 16 # number of processors that did the calculations
#istart = 0*n_proc
#iend = 1*n_proc

# loop over outputs
for n in range(ns, ne+1):
  
  # open the output file for writing (don't overwrite if exists)
  fileout = h5py.File(dnameout+str(n)+'.h5', 'a')

  i = -1
  # loops over all files
  while True:
    i += 1

    fileinname = dnamein+str(n)+'.h5.'+str(i)
    if not os.path.isfile(fileinname):
      break
    print('Load:',fileinname)

    # open the input file for reading
    filein = h5py.File(dnamein+str(n)+'.h5.'+str(i), 'r')
    # read in the header data from the input file
    head = filein.attrs

    # Detect DE
    DE = 'GasEnergy' in filein
    
    # if it's the first input file, write the header attributes 
    # and create the datasets in the output file
    if (i == 0):
      nx = head['dims'][0]
      ny = head['dims'][1]
      nz = head['dims'][2]
      fileout.attrs['dims'] = [nx, ny, nz]
      fileout.attrs['gamma'] = [head['gamma'][0]]
      fileout.attrs['t'] = [head['t'][0]]
      fileout.attrs['dt'] = [head['dt'][0]]
      fileout.attrs['n_step'] = [head['n_step'][0]]

      units = ['time_unit', 'mass_unit', 'length_unit', 'energy_unit', 'velocity_unit', 'density_unit']
      for unit in units:
        fileout.attrs[unit] = [head[unit][0]]
      keys = ['density','momentum_x','momentum_y','momentum_z','Energy','GasEnergy']

      for key in keys:
        if key in filein:
          if key not in fileout:
            fileout.create_dataset(key, (nx, ny, nz), chunks=(200,200,1))
            
      '''
      d  = fileout.create_dataset("density", (nx, ny, nz), chunks=True)
      mx = fileout.create_dataset("momentum_x", (nx, ny, nz), chunks=True)
      my = fileout.create_dataset("momentum_y", (nx, ny, nz), chunks=True)
      mz = fileout.create_dataset("momentum_z", (nx, ny, nz), chunks=True)
      E  = fileout.create_dataset("Energy", (nx, ny, nz), chunks=True)
      if (DE):
        GE = fileout.create_dataset("GasEnergy", (nx, ny, nz), chunks=True)
      '''
    # write data from individual processor file to
    # correct location in concatenated file
    nxl = head['dims_local'][0]
    nyl = head['dims_local'][1]
    nzl = head['dims_local'][2]
    xs = head['offset'][0]
    ys = head['offset'][1]
    zs = head['offset'][2]
    print('Read head')
    for key in keys:
      if key in filein:
        print(key)

        fileout[key][xs:xs+nxl,ys:ys+nyl,zs:zs+nzl] = filein[key]

    '''
    fileout['density'][xs:xs+nxl,ys:ys+nyl,zs:zs+nzl]  = filein['density']
    fileout['momentum_x'][xs:xs+nxl,ys:ys+nyl,zs:zs+nzl] = filein['momentum_x']
    fileout['momentum_y'][xs:xs+nxl,ys:ys+nyl,zs:zs+nzl] = filein['momentum_y']
    fileout['momentum_z'][xs:xs+nxl,ys:ys+nyl,zs:zs+nzl] = filein['momentum_z']
    fileout['Energy'][xs:xs+nxl,ys:ys+nyl,zs:zs+nzl]  = filein['Energy']
    if (DE):
      fileout['GasEnergy'][xs:xs+nxl,ys:ys+nyl,zs:zs+nzl] = filein['GasEnergy']
    '''
    print('filein close')      
    filein.close()

  fileout.close()
