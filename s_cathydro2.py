import sys
import chute.cat as cc
import resource
import time
import os

t0 = time.time()

if len(sys.argv) < 1:
    exit()

i = int(sys.argv[1])

if len(sys.argv) > 2:
    indir = sys.argv[2]
else:
    indir = 'raw_grid/'

if len(sys.argv) > 3:
    outdir = sys.argv[3]
else:
    outdir = 'grid/'

if indir and not os.path.isdir(indir):
    os.mkdir(indir)

if outdir and not os.path.isdir(outdir):
    os.mkdir(outdir)
    

cc.hydro(i,indir,outdir)

mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(f'{mem}KB\n{mem/1024}MB\n{mem/1024/1024}GB')

print(time.time() - t0,' seconds elapsed')
