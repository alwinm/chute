import sys
import chute.cat as cc
import resource

if len(sys.argv) < 1:
    exit()

i = int(sys.argv[1])

cc.hydro(i,'','')

mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
print(f'{mem}\n{mem/1024}\n{mem/1024/1024}')
