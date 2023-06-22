import numpy as n
import pylab as p
import h5py


def get_cloudy_cooling(path):
    # returns net cooling
    ln,lt,ll,lh = n.loadtxt(path,unpack=True,dtype=n.float64)

    shape = (121,81)

    ln = n.reshape(ln,shape)
    lt = n.reshape(lt,shape)
    ll = n.reshape(ll,shape)
    lh = n.reshape(lh,shape)
    number_density = 10**ln
    
    return (number_density**2) * (10**ll - 10**lh), ln, lt

def get_photoelectric_heating(ln, lt, n_av):
    number_density = 10**ln
    mask = lt < 4.0
    return number_density * n_av * 1.0e-26 * mask

def equilibrium_line(path, pe_bool = True, mesh_bool=False):
    cloudy_cooling, ln, lt = get_cloudy_cooling(path)
    pe = get_photoelectric_heating(ln, lt, 100.0)

    if pe_bool:
        net_cooling = cloudy_cooling - pe
    else:
        net_cooling = cloudy_cooling
    
    mask = net_cooling > 0

    locs = n.argmax(mask,axis=1)
    if mesh_bool:
        p.pcolormesh(ln,lt,mask,vmin=-1,vmax=1,cmap='seismic')

    # the reason I generate these instead of directly using the table is because the table is 2-D
    density_x = n.linspace(-6,6,121)
    temperature_y = n.linspace(1,9,81)
    p.plot(density_x,temperature_y[locs])


def calc_log_n_T(filename):
    
    with h5py.File(filename,'r') as f:
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
    log_T = n.log10(temperature)
    log_n = n.log10(n_cgs)
    return log_n, log_T

def arr_to_bin_edges(arr):
    # 10 bins per decade    
    return n.arange(n.floor(n.min(arr)), n.ceil(n.max(arr)) + 0.1, 0.1)

def calc_histogram(x, y):
    bins0 = [arr_to_bin_edges(x), arr_to_bin_edges(y)]
    return n.histogram2d(x.reshape(-1), y.reshape(-1), bins=bins0)

def make_phase_diagram(filename, cloudy_path):
    log_n, log_T = calc_log_n_T(filename)
    counts, x_edges, y_edges = calc_histogram(log_n, log_T)

    p.pcolormesh(x,y,z.transpose(),shading='flat')
    
    equilibrium_line(cloudy_path)
    
    p.xlabel('log10 n (cm-3)')
    p.ylabel('log10 T (K)')
    p.colorbar(label='Cells')
