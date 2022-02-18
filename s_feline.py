import sys
import chute.cat as cc
import os
import resource

i = 0
while True:
    if not os.path.isfile(str(i)+'_slice.h5.0'):
        break
    if not os.path.isfile(str(i)+'_slice.h5'):
        cc.slice(i,'','')
    i += 1

i = 0
while True:
    if not os.path.isfile(str(i)+'_proj.h5.0'):
        break
    if not os.path.isfile(str(i)+'_proj.h5'):
        cc.projection(i,'','')
    i += 1

i = 0
while True:
    if not os.path.isfile(str(i)+'_rot_proj.h5.0'):
        break
    if not os.path.isfile(str(i)+'_rot_proj.h5'):
        cc.rot_proj(i,'','')
    i += 1    

    
mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(f'{mem}\n{mem/1024}\n{mem/1024/1024}')
