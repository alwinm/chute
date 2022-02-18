import numpy as np

def rotate_box(x, y, z, theta, phi, delta):
  cd = np.cos(delta)
  sd = np.sin(delta)
  cp = np.cos(phi)
  sp = np.sin(phi)
  ct = np.cos(theta)
  st = np.sin(theta)
  xp = x*(cp*cd - sp*ct*sd) - y*(cp*sd + sp*ct*cd) + z*sp*st
  yp = x*(sp*cd + cp*ct*sd) + y*(cp*ct*cd - st*sd) - z*cp*st
  zp = x*st*sd + y*st*cd + z*ct
  return xp, yp, zp
