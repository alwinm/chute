# Parse cholla printf data
import pickle


def parse(filename):
    with open(filename,'r') as ofile:
        data = ofile.readlines()

    output = {}

    for line in data:
        tokens = line.split()
        
        if len(tokens) == 0:
            continue

        if len(tokens) <= 7:
            continue

        if tokens[0] == 'n_step:':
            key = 'timestep'
        elif tokens[0] == 'Time':
            key = tokens[1]
        else:
            continue

        value = float(tokens[7])
        
        if key not in output:
            output[key] = []

        output[key].append(value)
        
    return output
        
def save(filename,data):
    if type(data) == str or type(filename) != str:
        print('Save requires filename first, then data')
        
    with open(filename, 'wb') as handle:
        pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)

        
def load(filename):
    with open(filename, 'rb') as handle:
        data = pickle.load(handle)
    return data
            
    
def quickstats(out_dict):
    import numpy as n
    for key in out_dict:
        array = n.array(out_dict[key])
        outstring = 'Time {} Total {} ms Average {} ms +/- {} ms\n'.format(key,n.sum(array),n.mean(array),n.std(array))
        print(outstring)
