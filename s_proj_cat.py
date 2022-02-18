import sys
import chute.cat as cc
import os
import resource
i = int(sys.argv[1])
if not os.path.isfile(str(i)+'_slice.h5'):
    cc.slice(i,'','')
if not os.path.isfile(str(i)+'_proj.h5'):
    cc.projection(i,'','')
    
mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(f'{mem}\n{mem/1024}\n{mem/1024/1024}')
