import os
import chute.cat as cc
import chute.plot.aurora as cpa

def loop(name,function):
    indir = 'raw_' + name + '/'
    outdir = name + '/'
    i = 0
    while True:
        first_file = '{}/{}_{}.h5.0'.format(indir,str(i),name)
        if not os.path.isfile(first_file):
            break
        out_file = '{}/{}_{}.h5.0'.format(outdir,str(i),name)
        if os.path.isfile(out_file):
            continue
        print(first_file)
        function(i,indir,outdir)
        print(out_file)
        i += 1



for name in ['rot_proj','proj','slice']:
    # Make raw and cat dirs
    os.mkdir('raw_{}'.format(name))
    os.mkdir(name)
    # Move out cats first
    # Then move out raws
    os.system('mv *{}.h5 {}/.'.format(name,name))
    os.system('mv *{}.h5.* raw_{}/.'.format(name,name))    

loop('rot_proj',cc.rot_proj)
loop('proj',cc.proj)
loop('slice',cc.slice)

def plot_loop():
    i = 0
    while True:
        slicedir = './slice/'
        projdir = './proj/'
        slice_file = slicedir+str(i)+'_slice.h5'
        proj_file = projdir+str(i)+'_proj.h5'
        if not os.path.isfile(slice_file):
            return
        if not os.path.isfile(proj_file):
            return
        cpa.plot(i,log_bool=True,slicedir='./slice/',projdir='./proj/')
        i += 1

plot_loop()
