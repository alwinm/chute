import sys
import matplotlib
matplotlib.use('agg')
import chute.plot.aurora as cpa
import chute.cat as cc
import os
i = int(sys.argv[1])
if not os.path.isfile(str(i)+'_slice.h5'):
    cc.slice(i,'','')
if not os.path.isfile(str(i)+'_proj.h5'):
    cc.projection(i,'','')


cpa.plot(int(sys.argv[1]),log_bool=True,field='scalar')
    
