# Utils for concat cholla output

import h5py
import numpy as np
import os

def parse(argv):
  # Determine prefix
  if 'h5' in argv:
    preprefix = argv.split('.h5')[0]
    prefix = preprefix +'.h5'

  else:
    prefix = './{}.h5'.format(argv)

  # Check existing
  firstfile = prefix+'.0'
  if not os.path.isfile(firstfile):
    print(firstfile,' is missing')
    exit()

  # Set dirnames
  dnamein = os.path.dirname(firstfile)+'/'
  dnameout = os.path.dirname(firstfile) + '/'
  return dnamein,dnameout

def hydro(n,dnamein,dnameout):
  fileout = h5py.File(dnameout+str(n)+'.h5', 'a')

  i = -1
  # loops over all files
  while True:
    i += 1

    fileinname = dnamein+str(n)+'.h5.'+str(i)

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
      nx = head['dims'][0]
      ny = head['dims'][1]
      nz = head['dims'][2]
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
          fileout.create_dataset(key, (nx, ny, nz), chunks=(128,128,128))
          #fileout.create_dataset(key, (nx, ny, nz))

    # write data from individual processor file to
    # correct location in concatenated file
    nxl = head['dims_local'][0]
    nyl = head['dims_local'][1]
    nzl = head['dims_local'][2]
    xs = head['offset'][0]
    ys = head['offset'][1]
    zs = head['offset'][2]
    for key in keys:
      if key in filein:
        fileout[key][xs:xs+nxl,ys:ys+nyl,zs:zs+nzl] = filein[key]
    filein.close()

  # end loop over all files
  fileout.close()


def projection(n,dnamein,dnameout):
  # open the output file for writing
  fileout = h5py.File(dnameout+str(n)+'_proj.h5', 'w')
  i = -1
  while True:
    i += 1

    fileinname = dnamein+str(n)+'_proj.h5.'+str(i)

    if not os.path.isfile(fileinname):
      break

    print(fileinname)
    # open the input file for reading
    filein = h5py.File(fileinname,'r')
    # read in the header data from the input file
    head = filein.attrs

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

      dxy = np.zeros((nx,ny))
      dxz = np.zeros((nx,nz))
      Txy = np.zeros((nx,ny))
      Txz = np.zeros((nx,nz))

    # write data from individual processor file to
    # correct location in concatenated file
    nxl = head['dims_local'][0]
    nyl = head['dims_local'][1]
    nzl = head['dims_local'][2]
    xs = head['offset'][0]
    ys = head['offset'][1]
    zs = head['offset'][2]

    dxy[xs:xs+nxl,ys:ys+nyl] += filein['d_xy']
    dxz[xs:xs+nxl,zs:zs+nzl] += filein['d_xz']
    Txy[xs:xs+nxl,ys:ys+nyl] += filein['T_xy']
    Txz[xs:xs+nxl,zs:zs+nzl] += filein['T_xz']

    filein.close()

  # write out the new datasets
  fileout.create_dataset('d_xy', data=dxy)
  fileout.create_dataset('d_xz', data=dxz)
  fileout.create_dataset('T_xy', data=Txy)
  fileout.create_dataset('T_xz', data=Txz)

  fileout.close()
  return

def slice(n,dnamein,dnameout):
  # open the output file for writing
  fileout = h5py.File(dnameout+str(n)+'_slice.h5', 'w')

  i = -1
  while True:
  # loop over files for a given output time
    i += 1

    fileinname = dnamein+str(n)+'_slice.h5.'+str(i)
    if not os.path.isfile(fileinname):
      break

    print(fileinname)
    # open the input file for reading
    filein = h5py.File(fileinname,'r')
    # read in the header data from the input file
    head = filein.attrs

    # Detect DE
    DE = 'GE_xy' in filein
    SCALAR = 'scalar_xy' in filein

    # if it's the first input file, write the header attributes
    # and create the datasets in the output file
    if (i == 0):
      gamma = head['gamma']
      t = head['t']
      dt = head['dt']
      n_step = head['n_step']
      nx = head['dims'][0]
      ny = head['dims'][1]
      nz = head['dims'][2]
      fileout.attrs['gamma'] = gamma
      fileout.attrs['t'] = t
      fileout.attrs['dt'] = dt
      fileout.attrs['n_step'] = n_step
      fileout.attrs['dims'] = [nx, ny, nz]

      d_xy = np.zeros((nx,ny))
      d_xz = np.zeros((nx,nz))
      d_yz = np.zeros((ny,nz))
      mx_xy = np.zeros((nx,ny))
      mx_xz = np.zeros((nx,nz))
      mx_yz = np.zeros((ny,nz))
      my_xy = np.zeros((nx,ny))
      my_xz = np.zeros((nx,nz))
      my_yz = np.zeros((ny,nz))
      mz_xy = np.zeros((nx,ny))
      mz_xz = np.zeros((nx,nz))
      mz_yz = np.zeros((ny,nz))
      E_xy = np.zeros((nx,ny))
      E_xz = np.zeros((nx,nz))
      E_yz = np.zeros((ny,nz))
      if DE:
       GE_xy = np.zeros((nx,ny))
       GE_xz = np.zeros((nx,nz))
       GE_yz = np.zeros((ny,nz))
      if SCALAR:
       scalar_xy = np.zeros((nx,ny))
       scalar_xz = np.zeros((nx,nz))
       scalar_yz = np.zeros((ny,nz))

    # write data from individual processor file to
    # correct location in concatenated file
    nxl = head['dims_local'][0]
    nyl = head['dims_local'][1]
    nzl = head['dims_local'][2]
    xs = head['offset'][0]
    ys = head['offset'][1]
    zs = head['offset'][2]

    d_xy[xs:xs+nxl,ys:ys+nyl] += filein['d_xy']
    d_xz[xs:xs+nxl,zs:zs+nzl] += filein['d_xz']
    d_yz[ys:ys+nyl,zs:zs+nzl] += filein['d_yz']
    mx_xy[xs:xs+nxl,ys:ys+nyl] += filein['mx_xy']
    mx_xz[xs:xs+nxl,zs:zs+nzl] += filein['mx_xz']
    mx_yz[ys:ys+nyl,zs:zs+nzl] += filein['mx_yz']
    my_xy[xs:xs+nxl,ys:ys+nyl] += filein['my_xy']
    my_xz[xs:xs+nxl,zs:zs+nzl] += filein['my_xz']
    my_yz[ys:ys+nyl,zs:zs+nzl] += filein['my_yz']
    mz_xy[xs:xs+nxl,ys:ys+nyl] += filein['mz_xy']
    mz_xz[xs:xs+nxl,zs:zs+nzl] += filein['mz_xz']
    mz_yz[ys:ys+nyl,zs:zs+nzl] += filein['mz_yz']
    E_xy[xs:xs+nxl,ys:ys+nyl] += filein['E_xy']
    E_xz[xs:xs+nxl,zs:zs+nzl] += filein['E_xz']
    E_yz[ys:ys+nyl,zs:zs+nzl] += filein['E_yz']
    if DE:
      GE_xy[xs:xs+nxl,ys:ys+nyl] += filein['GE_xy']
      GE_xz[xs:xs+nxl,zs:zs+nzl] += filein['GE_xz']
      GE_yz[ys:ys+nyl,zs:zs+nzl] += filein['GE_yz']
    if SCALAR:
      scalar_xy[xs:xs+nxl,ys:ys+nyl] += filein['scalar_xy']
      scalar_xz[xs:xs+nxl,zs:zs+nzl] += filein['scalar_xz']
      scalar_yz[ys:ys+nyl,zs:zs+nzl] += filein['scalar_yz']

    filein.close()

  # wrte out the new datasets
  fileout.create_dataset('d_xy', data=d_xy)
  fileout.create_dataset('d_xz', data=d_xz)
  fileout.create_dataset('d_yz', data=d_yz)
  fileout.create_dataset('mx_xy', data=mx_xy)
  fileout.create_dataset('mx_xz', data=mx_xz)
  fileout.create_dataset('mx_yz', data=mx_yz)
  fileout.create_dataset('my_xy', data=my_xy)
  fileout.create_dataset('my_xz', data=my_xz)
  fileout.create_dataset('my_yz', data=my_yz)
  fileout.create_dataset('mz_xy', data=mz_xy)
  fileout.create_dataset('mz_xz', data=mz_xz)
  fileout.create_dataset('mz_yz', data=mz_yz)
  fileout.create_dataset('E_xy', data=E_xy)
  fileout.create_dataset('E_xz', data=E_xz)
  fileout.create_dataset('E_yz', data=E_yz)
  if DE:
    fileout.create_dataset('GE_xy', data=GE_xy)
    fileout.create_dataset('GE_xz', data=GE_xz)
    fileout.create_dataset('GE_yz', data=GE_yz)
  if SCALAR:
    fileout.create_dataset('scalar_xy', data=scalar_xy)
    fileout.create_dataset('scalar_xz', data=scalar_xz)
    fileout.create_dataset('scalar_yz', data=scalar_yz)

  fileout.close()
  return

def rot_proj(n,dnamein,dnameout):
  fileout = h5py.File(dnameout+str(n)+'_rot_proj.h5', 'w')
  i = -1
  
  while True:
  # loop over files for a given output time
    i += 1
    fileinname = dnamein+str(n)+'_rot_proj.h5.'+str(i)
    if not os.path.isfile(fileinname):
      break

    print(fileinname)

    filein = h5py.File(dnamein+fileinname,'r')
    head = filein.attrs
    # if it's the first input file, write the header attributes
    # and create the arrays to hold the output data
    if (i == 0):

      nxr = int(head['nxr'])
      nzr = int(head['nzr'])
      Lx = head['Lx']
      Lz = head['Lz']
      delta = head['delta']
      theta = head['theta']
      phi = head['phi']
      gamma = head['gamma']
      t = head['t']
      dt = head['dt']
      n_step = head['n_step']
      fileout.attrs['nxr'] = nxr
      fileout.attrs['nzr'] = nzr
      fileout.attrs['Lx'] = Lx
      fileout.attrs['Lz'] = Lz
      fileout.attrs['delta'] = delta
      fileout.attrs['theta'] = theta
      fileout.attrs['phi'] = phi
      fileout.attrs['gamma'] = gamma
      fileout.attrs['t'] = t
      fileout.attrs['dt'] = dt
      fileout.attrs['n_step'] = n_step

      d_xzr  = np.zeros((nxr, nzr))
      vx_xzr = np.zeros((nxr, nzr))
      vy_xzr = np.zeros((nxr, nzr))
      vz_xzr = np.zeros((nxr, nzr))
      T_xzr  = np.zeros((nxr, nzr))

    # end first input file
    
    # write data from individual processor file to
    # correct location in concatenated file
    nx_min = int(head['nx_min'])
    nx_max = int(head['nx_max'])
    nz_min = int(head['nz_min'])
    nz_max = int(head['nz_max'])

    d_xzr[nx_min:nx_max,nz_min:nz_max]  += filein['d_xzr'][:]
    vx_xzr[nx_min:nx_max,nz_min:nz_max] += filein['vx_xzr'][:]
    vy_xzr[nx_min:nx_max,nz_min:nz_max] += filein['vy_xzr'][:]
    vz_xzr[nx_min:nx_max,nz_min:nz_max] += filein['vz_xzr'][:]
    T_xzr[nx_min:nx_max,nz_min:nz_max]  += filein['T_xzr'][:]

    filein.close()
  # end while loop
  
  # write out the new datasets
  fileout.create_dataset("d_xzr", data=d_xzr)
  fileout.create_dataset("vx_xzr", data=vx_xzr)
  fileout.create_dataset("vy_xzr", data=vy_xzr)
  fileout.create_dataset("vz_xzr", data=vz_xzr)
  fileout.create_dataset("T_xzr", data=T_xzr)

  fileout.close()
