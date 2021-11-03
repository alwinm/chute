# define cholla units

# g_cosmo = 4.300927161e-06
kyr_cgs = 3.15569e10
kpc_cgs = 3.086e21
km_cgs = 1e5
msun_cgs = 1.98847e33

mp_cgs = 1.672622e-24
kb_cgs = 1.380658e-16
gn_cgs = 6.67259e-8
gn_code = 4.49451e-18


length_unit_cgs = kpc_cgs
time_unit_cgs = kyr_cgs
mass_unit_cgs = 1.98855e33

density_unit_cgs = mass_unit_cgs/length_unit_cgs**3
velocity_unit_cgs = length_unit_cgs/time_unit_cgs
energy_unit_cgs =  density_unit_cgs * velocity_unit_cgs**2
pressure_unit_cgs = energy_unit_cgs
