# I am not sure why I am calling this file aga.py
# The first name that popped into my head was agamemmnon

import os
import sys
import time
import chute.cat as cc

time.t0 = time.time()

OKCYAN = '\033[96m'
ENDC = '\033[0m'

restart_mode = False


def timer(string):
    print(string,time.time() - time.t0,' seconds')
    time.t0 = time.time()

def printf(*args,**kwargs):
    print(*args,**kwargs,flush=True)

def make_nompi():
    # creates the make type nompi if it does not exist
    infile = 'builds/make.type.hydro'
    outfile = 'builds/make.type.nompi'
    #if os.path.isfile(outfile):
    #    return

    with open(infile,'r') as ofile:
        data = ofile.readlines()

    with open(outfile,'w') as ofile:
        for line in data:
            if 'MPI_CHOLLA' not in line:
                ofile.write(line)

def make_ctu():
    # creates the make type ctu if it does not exist
    infile = 'builds/make.type.hydro'
    outfile = 'builds/make.type.ctu'
    #if os.path.isfile(outfile):
    #    return

    with open(infile,'r') as ofile:
        data = ofile.readlines()

    with open(outfile,'w') as ofile:
        for line in data:
            if 'VL' not in line:
                ofile.write(line)
            else:
                ofile.write(line.replace('VL','CTU'))

def make_simple():
    # creates the make type ctu if it does not exist
    infile = 'builds/make.type.hydro'
    outfile = 'builds/make.type.simple'
    #if os.path.isfile(outfile):
    #    return

    with open(infile,'r') as ofile:
        data = ofile.readlines()

    with open(outfile,'w') as ofile:
        for line in data:
            if 'VL' not in line:
                ofile.write(line)
            else:
                ofile.write(line.replace('VL','SIMPLE'))

def make_scalar():
    # creates the make type scalar if it does not exist
    infile = 'builds/make.type.hydro'
    outfile = 'builds/make.type.scalar'
    with open(infile,'r') as ofile:
        data = ofile.readlines()

    with open(outfile,'w') as ofile:

        for line in data:
            ofile.write(line)
        ofile.write('DFLAGS += -DSCALAR \n')

    if not os.path.isdir('temp'):
        os.mkdir('temp')
    
    typename = 'scalar'
    os.system('make clean')
    os.system('make -j TYPE={}'.format(typename))
    os.system('mv bin/* temp/.')        


def compile_cholla():
    # compile hydro and nompi, store binaries under temp/
    if not os.path.isdir('temp'):
        os.mkdir('temp')

    make_nompi()

    make_ctu()
    
    make_simple()
    
    for typename in ['hydro','nompi','ctu','simple']:
        os.system('make clean')
        os.system('make -j TYPE={}'.format(typename))
        os.system('mv bin/* temp/.')

tests1d = [
['/1D/Creasey_shock.txt','tout=30.0 outstep=30.0','creasey'],
['/1D/sod.txt','','sod1'],
['/1D/sound_wave.txt','tout=0.05 outstep=0.05','sound1'],
# strong shock tout outstep = 0.07
['/1D/strong_shock.txt','','shock1'],
# two shocks tout outstep = 0.035
['/1D/two_shocks.txt','','two_shocks'],
['/1D/blast_1D.txt','tout=0.038 outstep=0.038','blast1'],
['/1D/square_wave.txt','tout=1.0 outstep=1.0','square'],
]
tests2d = [
['/2D/sod.txt','nx=256 ny=256 tout=0.5 outstep=0.1','sod'],
['/2D/sound_wave.txt','tout=2.0 outstep=0.4','sound2'],
['/2D/KH_res_ind_2D.txt','tout=0.004 outstep=0.001','kh22'],
['/2D/KH_discontinuous_2D.txt','tout=16.0 outstep=4.0','kh2'],
['/2D/Rayleigh_Taylor.txt','tout=2.0 outstep=2.0','rt2'],
['/2D/Implosion_2D.txt','tout=0.03 outstep=0.01','imp2'],
]
tests3d = [
['/3D/sound_wave.txt','tout=0.05 outstep=0.05','sound3'],
['/3D/Spherical_Overpressure.txt','tout=0.1 outstep=0.1','sphere3'],
]
tests = tests1d + tests2d + tests3d


    

def run_test(binary,odir,test):
    pdir = 'examples'
    outdir = f'{odir}/{test[2]}/'
    if not os.path.isdir(outdir):
        os.system('mkdir -p ' + outdir)
    command = f'{binary} {pdir}{test[0]} {test[1]} outdir={odir}/{test[2]}/'

    if restart_mode:
        command += f' init=Read_Grid nfile=0 indir={odir}/{test[2]}/'

    printf(command)
    os.system(command)

def short_test():
    if not os.path.isdir('temp'):
        compile_cholla()    

    os.system('make clean')
    os.system('make -j')


    bins = os.listdir('bin')
    hydro_match = [string for string in bins if 'hydro' in string]
    for test in tests:
        run_test(f'bin/{hydro_match[0]}','out_hydro',test)

def run_tests():
    # single nompi
    # single MPI
    # MPI
    if not os.path.isdir('temp'):
        compile_cholla()

    bins = os.listdir('temp')

    for typename in ['ctu','simple','nompi']:
        match = [string for string in bins if typename in string]
        if not match:
            continue
        for test in tests:
            run_test(f'temp/{match[0]}','out_'+typename,test)

    hydro_match = [string for string in bins if 'hydro' in string]
    if not hydro_match:
        return

    # 1 gpu mpi
    for test in tests:
        run_test(f'temp/{hydro_match[0]}','out_hydro',test)

    # multi-gpu mpi
    for test in tests1d:
        run_test(f'mpirun -np 2 temp/{hydro_match[0]}','out_mpi',test)

    for test in tests2d:
        run_test(f'mpirun -np 4 temp/{hydro_match[0]}','out_mpi',test)

    for test in tests3d:
        run_test(f'mpirun -np 8 temp/{hydro_match[0]}','out_mpi',test)


def run_scalar():
    make_scalar()
    bins = os.listdir('temp')
    typename = 'scalar'
    match = [string for string in bins if typename in string]
    if not match:
        print('NO matching binary for scalar found')
        return

    for test in tests:                                                                                                                                                                             
        run_test(f'temp/{match[0]}','out_'+typename,test) 


def cat():
    # loop through out_mpi directories and concatenate as appropriate
    odir = 'out_mpi'
    for test in tests:
        outdir = f'{odir}/{test[2]}/'
        
        i = 0
        while os.path.isfile(outdir+str(i)+'.h5.0'):
            cc.hydro(i,outdir,outdir)
            i += 1

def compare(dir1,dir2,filename):
    f1 = dir1+filename
    f2 = dir2+filename
    if not os.path.isfile(f2):
        f2 += '.0'
    if not os.path.isfile(f1):
        f1 += '.0'
    if not os.path.isfile(f2):
        printf(f2,' missing')
        return 
    if not os.path.isfile(f1):
        printf(f1,' missing')
        return
    command = 'h5diff {} {}'.format(f1,f2)
    colorcommand = 'h5diff {}{}{}{} {}{}{}{}'.format(OKCYAN,dir1,ENDC,filename,OKCYAN,dir2,ENDC,filename)
    printf(command)
    printf(colorcommand)
    output = os.popen(command).readlines()
    skip = False
    for line in output:
        if 'Git Commit Hash' in line:
            skip = True
        elif 'Macro Flags' in line:
            skip = True
        elif skip:
            skip = False
        else:
            print(line)

def hdiff():
    # internal hdiff check
    # for each test, compare the nompi version, MPI version,
    for test in tests:
        nompi_dir = f'out_nompi/{test[2]}/'
        hydro_dir = f'out_hydro/{test[2]}/'
        mpi_dir = f'out_mpi/{test[2]}/'
        for filename in os.listdir(nompi_dir):
            printf('='*40)
            compare(nompi_dir,hydro_dir,filename)
            compare(nompi_dir,mpi_dir,filename)
            compare(hydro_dir,mpi_dir,filename)

def repodiff(dir1,dir2):
    for out in ['nompi','hydro','mpi','ctu','simple']:
        for test in tests:
            _dir1 = '{}/out_{}/{}/'.format(dir1,out,test[2])
            _dir2 = '{}/out_{}/{}/'.format(dir2,out,test[2])
            
            if not os.path.isdir(_dir1):
                continue

            for filename in os.listdir(_dir1):
                printf('='*40)
                compare(_dir1,_dir2,filename)

def repodiff_scalar(dir1,dir2):
    for out in ['scalar']:
        for test in tests:
            _dir1 = '{}/out_{}/{}/'.format(dir1,out,test[2])
            _dir2 = '{}/out_{}/{}/'.format(dir2,out,test[2])
            
            if not os.path.isdir(_dir1):
                print(_dir1, ' missing directory')
                continue

            for filename in os.listdir(_dir1):
                printf('='*40)
                compare(_dir1,_dir2,filename)    

if 'rebuild' in sys.argv:
    os.remove('builds/make.type.nompi')
    os.remove('builds/make.type.ctu')
    os.remove('builds/make.type.simple')
    compile_cholla()
    exit()
if 'compile' in sys.argv:
    compile_cholla()
    exit()

if 'run' in sys.argv:
    run_tests()
    exit()

if 'restart' in sys.argv:
    restart_mode = True
    run_tests()
    exit()

if 'cat' in sys.argv:
    cat()
    exit()

if 'hdiff' in sys.argv:
    hdiff()
    exit()

if 'help' in sys.argv:
    printf('rebuild,compile,run,cat,hdiff,repo,short')
    exit()

if 'repo' in sys.argv:
    repodiff(sys.argv[2],sys.argv[3])
    exit()

if 'short' in sys.argv:
    short_test()
    
if 'scalar' in sys.argv:
    run_scalar()

if 'repo_scalar' in sys.argv:
    print('repo scalar')
    repodiff_scalar(sys.argv[2],sys.argv[3])


# default behavior:
# runs tests
# cats tests
# runs hdiff on tests

#run_tests()
#cat()
#hdiff()
#timer('run_tests finished:')
