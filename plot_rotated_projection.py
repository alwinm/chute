import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['mathtext.default']='regular'
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
import matplotlib.cm as cm
from mpi4py import MPI
from sys import exit
from chute.rotate_box import rotate_box

comm = MPI.COMM_WORLD
rank = comm.Get_rank()


istart = rank+0
iend   = rank+0
dnamein='./hdf5/'
dnameout='./rotated_projections/'

# some constants
l_s = 3.086e21 # length scale, centimeters in a kiloparsec
m_s = 1.99e33 # mass scale, g in a solar mass
t_s = 3.154e10 # time scale, seconds in a kyr
d_s = m_s / l_s**3 # density scale, M_sun / kpc^3
v_s = l_s / t_s # velocity scale, kpc / kyr
p_s = d_s*v_s**2 # pressure scale, M_sun / kpc kyr^2
G = 6.67259e-8 # in cm^3 g^-1 s^-2
mp = 1.67e-24 # proton mass in grams
G = G / l_s**3 * m_s * t_s**2 # in kpc^3 / M_sun / kyr^2
KB = 1.3806e-16 # boltzmann constant in cm^2 g / s^2 K
v_to_kmps = l_s/t_s/100000
kmps_to_kpcpkyr = 1.0220122e-6
pscale=2048./10.
fsize=pscale/2.
lwidth=12
fontpath='/ccs/home/evans/.fonts/Helvetica.ttf'
helvetica=matplotlib.font_manager.FontProperties(size=fsize,fname=fontpath)

for i in range(istart,iend+1):
  
  f = h5py.File(dnamein+str(i)+'_rot_proj.h5', 'r')
  head = f.attrs
  t = head['t']
  nx = head['nxr']
  nz = head['nzr']
  Lx = head['Lx']
  Lz = head['Lz']
  theta = head['theta']
  phi = head['phi']
  delta = head['delta']
  pd  = f['d_xzr'][:]
  pT  = f['T_xzr'][:]
  pT  = pT/pd
  log_pd = np.log10(pd)
  log_pT = np.log10(pT)
  ny = nx
  theta = (np.pi/180.)*theta
  phi   = (np.pi/180.)*phi
  delta = (np.pi/180.)*delta

  #pTz = Tz/pdz
  #pTy = Ty/pdy

  #pd_min, pd_max = 4.0, 8.5
  pd_min, pd_max = 4.0, 9.0
  pT_min, pT_max = 3.3, 7.7

  #rho_max = 9.0e9
  #dynrange = 5.0e4
  #rho_min = rho_max/dynrange
  #d_plot = np.clip(d, rho_min, rho_max)
  #d_plot = (np.log10(d_plot) - np.log10(rho_min))/(np.log10(rho_max)-np.log10(rho_min))
  d_plot = np.clip(log_pd, pd_min, pd_max)
  d_plot[np.isnan(d_plot)] = pd_min
  T_plot = np.clip(log_pT, pT_min, pT_max)
  T_plot[np.isnan(T_plot)] = pT_min

  xbb = np.zeros(5)
  ybb = np.zeros(5)
  zbb = np.zeros(5)
  xbt = np.zeros(5)
  ybt = np.zeros(5)
  zbt = np.zeros(5)
  xbb[:] = [-1.,1.,1.,-1.,-1.]
  ybb[:] = [-1.,-1.,1.,1.,-1.]
  zbb[:] = [-1.,-1.,-1.,-1.,-1.]
  xbt[:] = [-1.,1.,1.,-1.,-1.]
  ybt[:] = [-1.,-1.,1.,1.,-1.]
  zbt[:] = [1.,1.,1.,1.,1.]
  # boundaries of the box in pixel units
  xbb *= 5.0*pscale 
  ybb *= 5.0*pscale 
  zbb *= 10.0*pscale 
  xbt *= 5.0*pscale
  ybt *= 5.0*pscale
  zbt *= 10.0*pscale
  xbbp,ybbp,zbbp = rotate_box(xbb,ybb,zbb,theta,phi,delta)
  xbtp,ybtp,zbtp = rotate_box(xbt,ybt,zbt,theta,phi,delta)
  # center the box on the output pixel map
  xbbp += nx/2.
  ybbp += ny/2.
  zbbp += nz/2.
  xbtp += nx/2.
  ybtp += ny/2.
  zbtp += nz/2.


  # make density plots
  fig = plt.figure(figsize=(nx/100.,nz/100.), dpi=100)
  a0 = plt.axes([0.,0.,1.,1.])
  for child in a0.get_children():
    if isinstance(child, matplotlib.spines.Spine):
      child.set_visible(False)  
  #a0.set_xticks(400*np.arange(0.1, 1, 0.1))
  #a0.set_yticks(400*np.arange(0.1, 1, 0.1))
  #a0.tick_params(axis='both', which='both', color='white', length=5, direction='in', top='on', right='on', labelleft='off', labelbottom='off')  
  a0.imshow(d_plot.T, origin='lower', extent=(0, nx, 0, nz), cmap='bone', vmin=pd_min, vmax=pd_max, interpolation='bilinear')
  a0.autoscale(False)
  a0.text(0.97*nx, 0.95*nz, str(int(t/1000))+' Myr', color='white', horizontalalignment='right', fontproperties=helvetica)
  a0.hlines(0.05*nz+0.25*pscale, 0.05*nx, 0.05*nx+pscale, color='white', linewidth=lwidth)
  a0.text(0.05*nx+pscale+0.125*pscale, 0.05*nz, '1 kpc', color='white', fontproperties=helvetica)
  a0.plot(xbtp,zbtp,color='white',linestyle='--',linewidth=4)
  a0.plot(xbbp,zbbp,color='white',linestyle='--',linewidth=4)
  a0.plot([xbbp[1],xbtp[1]],[zbbp[1],zbtp[1]],color='white',linestyle='--',linewidth=4)
  a0.plot([xbbp[2],xbtp[2]],[zbbp[2],zbtp[2]],color='white',linestyle='--',linewidth=4)
  a0.plot([xbbp[3],xbtp[3]],[zbbp[3],zbtp[3]],color='white',linestyle='--',linewidth=4)
  a0.plot([xbbp[4],xbtp[4]],[zbbp[4],zbtp[4]],color='white',linestyle='--',linewidth=4)
  #pretty white border
  a0.axvline(x=0, color='white',linewidth=4)
  a0.axvline(x=nx, color='white',linewidth=4)
  a0.hlines(nz, 0, nx, color='white',linewidth=4)
  a0.hlines(0, 0, nx, color='white',linewidth=4)
  plt.savefig(dnameout+'d_rot_'+str(i)+'.png', dpi=100)
  plt.close(fig)

  # make temperature plots
  fig = plt.figure(figsize=(nx/100.,nz/100.), dpi=100)
  a0 = plt.axes([0.,0.,1.,1.])
  for child in a0.get_children():
    if isinstance(child, matplotlib.spines.Spine):
      child.set_visible(False)  
  #a0.set_xticks(400*np.arange(0.1, 1, 0.1))
  #a0.set_yticks(400*np.arange(0.1, 1, 0.1))
  #a0.tick_params(axis='both', which='both', color='white', length=5, direction='in', top='on', right='on', labelleft='off', labelbottom='off')  
  a0.imshow(T_plot.T, origin='lower', extent=(0, nx, 0, nz), cmap='magma', vmin=pT_min, vmax=pT_max, interpolation='bilinear')
  #a0.imshow(T_plot.T, origin='lower', extent=(0, nxr, 0, nzr), cmap='magma')
  a0.autoscale(False)
  a0.text(0.97*nx, 0.95*nz, str(int(t/1000))+' Myr', color='white', horizontalalignment='right', fontproperties=helvetica)
  a0.hlines(0.05*nz+0.25*pscale, 0.05*nx, 0.05*nx+pscale, color='white', linewidth=lwidth)
  a0.text(0.05*nx+pscale+0.125*pscale, 0.05*nz, '1 kpc', color='white', fontproperties=helvetica)
  a0.plot(xbtp,zbtp,color='white',linestyle='--',linewidth=4)
  a0.plot(xbbp,zbbp,color='white',linestyle='--',linewidth=4)
  a0.plot([xbbp[1],xbtp[1]],[zbbp[1],zbtp[1]],color='white',linestyle='--',linewidth=4)
  a0.plot([xbbp[2],xbtp[2]],[zbbp[2],zbtp[2]],color='white',linestyle='--',linewidth=4)
  a0.plot([xbbp[3],xbtp[3]],[zbbp[3],zbtp[3]],color='white',linestyle='--',linewidth=4)
  a0.plot([xbbp[4],xbtp[4]],[zbbp[4],zbtp[4]],color='white',linestyle='--',linewidth=4)
  #pretty white border
  a0.axvline(x=0, color='white',linewidth=4)
  a0.axvline(x=nx, color='white',linewidth=4)
  a0.hlines(nz, 0, nx, color='white',linewidth=4)
  a0.hlines(0, 0, nx, color='white',linewidth=4)
  plt.savefig(dnameout+'T_rot_'+str(i)+'.png', dpi=100)
  plt.close(fig)

