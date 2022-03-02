import os
import sys

dir1 = sys.argv[1]
dir2 = sys.argv[2]
if len(sys.argv)>3:
    flags = ' '.join(sys.argv[3:])
else:
    flags = ''
subdirs1 = ['creasey','sod1','sound1','shock1','two_shocks','blast1','square']
subdirs2 = ['sod','sound2','kh22','rt2','imp2','kh2']
subdirs3 = ['sound3','sphere3']

subdirs = []
subdirs += subdirs1
subdirs += subdirs2
subdirs += subdirs3
for subdir in subdirs:
    basedir1 = '{}/out/{}/'.format(dir1,subdir)
    basedir2 = '{}/out/{}/'.format(dir2,subdir)
    if not os.path.isdir(basedir1):
        print(basedir1,' didnt exist')
        continue
    if not os.path.isdir(basedir2):
        print(basedir2,' didnt exist')
        continue
    for filename in sorted(os.listdir(basedir1)):
        filename1 = '{}{}'.format(basedir1,filename)
        filename2 = '{}{}'.format(basedir2,filename)
        filename3 = filename2 + '.0'
        if not os.path.isfile(filename2):
            filename2 = filename3
        if not os.path.isfile(filename2):
            print(filename2, 'didnt exist')

        if os.path.isfile(filename2):
            command = 'h5diff {} {} {}'.format(flags,filename1,filename2)
            print(command)
            result = os.system(command)
            if result == 2:
                print('\nCtrl-C',result)
                sys.exit(0)

