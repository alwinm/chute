# Utils for concat cholla output

import h5py
import numpy as np
import os
import itertools

verbose = True
to_kelvin = 1.15831413e14 # proton mass * (kpc/kyr)^2 / boltzmann constant
mu = 0.6

def binner(array,binfactor):
  for size in array.shape:
    if size%binfactor:
      print("Array size was {} but binfactor is {}")

  def resolve(tup):
    select = tuple(slice(x,None,binfactor) for x in tup)
    return array[select]
      
  return sum(resolve(tup) for tup in itertools.product(range(binfactor),repeat=len(array.shape)))/float(binfactor**len(array.shape))
      


def hydro_mask_bin(n_file,dnamein,dnameout,double=True,binfactor=1):
  fileout = h5py.File(dnameout+str(n_file)+'.maskbin.h5', 'a')

  i = -1
  # loops over all files
  while True:
    i += 1

    fileinname = dnamein+str(n_file)+'.h5.'+str(i)

    if not os.path.isfile(fileinname):
      break
    print('Load:',fileinname,flush=True)

    # open the input file for reading
    filein = h5py.File(fileinname,'r')

    # read in the header data from the input file
    head = filein.attrs

    # if it's the first input file, write the header attributes
    # and create the datasets in the output file
    if (i == 0):
      nx = head['dims'][0]//binfactor
      ny = head['dims'][1]//binfactor
      nz = head['dims'][2]//binfactor
      nxl = head['dims_local'][0]//binfactor
      nyl = head['dims_local'][1]//binfactor
      nzl = head['dims_local'][2]//binfactor
      fileout.attrs['dims'] = [nx, ny, nz]
      fileout.attrs['gamma'] = [head['gamma'][0]]
      fileout.attrs['t'] = [head['t'][0]]
      fileout.attrs['dt'] = [head['dt'][0]]
      fileout.attrs['n_step'] = [head['n_step'][0]]

      units = ['time_unit', 'mass_unit', 'length_unit', 'energy_unit', 'velocity_unit', 'densit\
y_unit']
      for unit in units:
        fileout.attrs[unit] = [head[unit][0]]
      keys = list(filein.keys())
      #['density','momentum_x','momentum_y','momentum_z','Energy','GasEnergy','scalar0']

      for key in keys:
        if key not in fileout:
          # WARNING: If you don't set dataset dtype it will default to 32-bit, but CHOLLA likes to be 64-bit
          if double:
            dtype = filein[key].dtype
          else:
            dtype = None
          if nz > 1:
            fileout.create_dataset(key, (nx, ny, nz), chunks=(nxl,nyl,nzl), dtype=dtype)
          elif ny > 1:
            fileout.create_dataset(key, (nx, ny), chunks=(nxl,nyl), dtype=dtype)
          elif nx > 1:
            fileout.create_dataset(key, (nx,), chunks=(nxl,), dtype=dtype)
          #fileout.create_dataset(key, (nx, ny, nz))

    # write data from individual processor file to
    # correct location in concatenated file
    nxl = head['dims_local'][0]//binfactor
    nyl = head['dims_local'][1]//binfactor
    nzl = head['dims_local'][2]//binfactor
    xs = head['offset'][0]//binfactor
    ys = head['offset'][1]//binfactor
    zs = head['offset'][2]//binfactor

    gamma = head['gamma'][0]
    temperature =  (mu*(gamma-1.0)*to_kelvin)*(filein['GasEnergy'][:]/filein['density'][:])
    mask = (temperature < 2e4)

    # each individual cell obeys the mask so the average obeys the mask
    # sum(A_valid + A_invalid) / sum(B_valid + B_invalid) = sum(A_valid)/sum(B_valid) < sum((mask A/B)*B_valid)/sum(B_valid) = mask(A/B)
    def process(key):
      return binner(filein[key][:] * mask,binfactor)

    for key in keys:
      if key in filein:
        if nz > 1:
          fileout[key][xs:xs+nxl,ys:ys+nyl,zs:zs+nzl] = process(key)
        elif ny > 1:
          fileout[key][xs:xs+nxl,ys:ys+nyl] = process(key)
        elif nx > 1:
          fileout[key][xs:xs+nxl] = process(key)
    filein.close()

  # end loop over all files
  fileout.close()
