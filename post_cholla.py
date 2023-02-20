import os
import matplotlib
matplotlib.use('agg')
import chute.cat as cc
import chute.plot.aurora as cpa

def mkdir(dirname):
    if os.path.isdir(dirname):
        return
    os.mkdir(dirname)
def loop(name,function):
    indir = 'raw_' + name + '/'
    outdir = name + '/'
    i = -1
    while True:
        i += 1
        first_file = '{}{}_{}.h5.0'.format(indir,str(i),name)
        if not os.path.isfile(first_file):
            break
        out_file = '{}{}_{}.h5'.format(outdir,str(i),name)
        if os.path.isfile(out_file):
            continue
        print(first_file)
        function(i,indir,outdir)
        print(out_file)



for name in ['rot_proj','proj','slice','particles','grid']:
    # Make raw and cat dirs
    mkdir('raw_{}'.format(name))
    mkdir(name)
    # Move out cats first
    # Then move out raws
    os.system('mv *{}.h5 {}/.'.format(name,name))
    os.system('mv *{}.h5.* raw_{}/.'.format(name,name))    

os.system('mv *.h5.* raw_grid/.')


    
loop('rot_proj',cc.rot_proj)
loop('proj',cc.projection)
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
        field = 'd'
        log_bool=True
        savefile = f'aurora/aurora_Field{field}_Log{log_bool}_{i:03d}.png'
        if not os.path.isfile(savefile):
            cpa.plot(i,log_bool=True,slicedir='./slice/',projdir='./proj/')
        i += 1

plot_loop()
