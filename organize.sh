mkdir raw_proj
mkdir raw_rot_proj
mkdir raw_slice

mkdir proj
mkdir rot_proj
mkdir slice

mkdir raw_grid
mkdir grid

mv *rot_proj.h5 rot_proj/.
mv *rot_proj.h5.* raw_rot_proj/.

mv *proj.h5 proj/.
mv *proj.h5.* raw_proj/.

mv *slice.h5 slice/.
mv *slice.h5.* raw_slice/.

mv *.h5.* raw_grid/.
mv *.h5 grid/.
