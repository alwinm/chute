# Cat everything under a directory 

import os
import sys
import chute.cat as cc

dirname = sys.argv[1]
if dirname[-1] != '/':
    dirname += '/'
outname = dirname + 'out/'

subdirs = os.listdir(outname)

for subdir in subdirs:
    datadir = outname + subdir + '/'
    if os.path.isdir(datadir):
        i = 0
        while os.path.isfile(datadir + str(i) + '.h5.0'):
            cc.hydro(i,datadir,datadir)
            i += 1
