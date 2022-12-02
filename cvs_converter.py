from scipy.special import comb
import numpy as np
import sys
import re

import math

import csv

def convert(file_name, rrs, algorithms, cutoff):
    new_cvs = []
    with open(file_name) as file_obj:
        top = next(file_obj).replace('\n','')
        header = (top.split (","))
        reader_obj = csv.reader(file_obj)
        # print(header)
        # i = 0
        # for row in reader_obj:
        #     if i < 3: print(row)
        #     i+= 1
        for l in reader_obj:
            for h in range(len(header)):
                if h == 0: 
                    inst = l[h]
                else:  #float(l[h].split(':')[1]) != 0:
                    algorithm = header[h]
                    performance = float(l[h].split(':')[1])
                    performance =  PARkRed(algorithm,inst,rrs, algorithms, cutoff, k=10,bound=None)
                    new_cvs.append([algorithm,inst,performance])
    return new_cvs

def PARk(algorithm,instance,rrs, algorithms, cutoff, k=10,bound=None):
    
    if instance == None:
        raise ValueError('Cannot calculate PAR for None instance.')
    elif algorithm == None:
        c = max([rrs[instance][algorithm][3] for algorithm in algorithms])
        if cutoff is not None:
            c = cutoff
        return c*k
    else:
        (r,t,q,c,s) = rrs[instance][algorithm]
        if cutoff is not None:
            c = cutoff
        if (t < c and r in ['SAT','UNSAT']):
            return t
        else:
            if bound == None:
                return c*k
            elif bound == "best":
                return c
            elif bound == "worst":
                return float("inf")

def PARkRed(algorithm,instance,rrs, algorithms, cutoff, k=10,bound=None):
    return PARk(None,instance,rrs, algorithms, cutoff, k,bound=None) - PARk(algorithm,instance,rrs, algorithms, cutoff, k,bound=None)



def main():
    import ZillaRunResultsUtils
    sys.path.append('DataConverter')
    import DataConverter


    file_name = sys.argv[1]
    rrs = ZillaRunResultsUtils.numerizeRunResults(DataConverter.readZillaFormatRunResults([file_name]))

    instances = rrs.keys() #Gallegos: Keys are utlized in the function someway
    #sys.stderr.write('%d instances.\n' % len(instances))
    algorithms = []
    for instance in instances:
        #algorithms.extend([ x for x in rrs[instance].keys() if re.match("glucose", x)])
        algorithms.extend(rrs[instance].keys()) #Gallegos: Figure out what this does. 
    algorithms = list(set(algorithms))

    cutoff = None
    if len(sys.argv) > 4:
        cutoff = int(sys.argv[4])

    new_file = convert(file_name, rrs, algorithms, cutoff)
    
    with open("test_file_park.csv", 'w', newline='', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(["algorithm", "instance", "performance"])

        writer.writerows(new_file)

if __name__ == '__main__':
    main()