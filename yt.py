import numpy as n
import h5py
import yt
kpc = 3.086e21

def load(filename,
         mu=0.6,
         length_unit_cgs = 3.086e21,
         time_unit_cgs = 3.154e10,
         mass_unit_cgs = 1.989e33,
         cell_size_cgs = 20*kpc/256.,
         metallicity=0.3):
    # Default length unit is kpc
    # Default time unit is kyr
    # Default mass unit is M_sun
    # Cholla has no metallicity so setting 0.3

    # Open HDF5 File Read only
    f = h5py.File(filename,"r")

    keys = ['density','GasEnergy'] 
    shape = f.attrs['dims'] # grid shape
    ndim = len(shape) 
    bbox = n.zeros([ndim,2])
    bbox[:,1] = f.attrs['dims']*cell_size_cgs

    # Density and temperature conversions to cgs
    # Temperature calculation
    density = f['density'][:]
    gamma = f.attrs['gamma'][0]
    k_B_cgs = 1.3807e-16
    m_p_cgs = 1.6726e-24
    to_kelvin = m_p_cgs * (length_unit_cgs/time_unit_cgs)**2 / k_B_cgs
    temperature = (mu*(gamma-1.0)*to_kelvin)*f['GasEnergy'][:]/density
    density_cgs = density * (mass_unit_cgs/(length_unit_cgs)**3)
    data = {}

    # Velocity calculation
    velocity_unit_cgs = length_unit_cgs/time_unit_cgs
    for letter in ['x','y','z']:
        data['velocity_'+letter] = velocity_unit_cgs*f['momentum_'+letter][:]/density

    # Arbitrary metallicity
    data['metallicity'] = n.ones(shape)*metallicity

    data['density'] = density_cgs
    data['temperature'] = temperature
    return yt.load_uniform_grid(data,shape,length_unit='cm',mass_unit='g',bbox=bbox)





