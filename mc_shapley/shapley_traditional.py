from scipy.special import comb
import numpy as np
import sys
import re

import pytest as test
import math
from copy import deepcopy

import csv

'''
Traditional Shapley code, briefly written so I can experiment and test the traditional shapley code
Author (Victim): Nikita A. Gallegos
Date: 08/14/2023

'''
def marginal_contributions(instances, algorithms, scores, temp_order = None, temp_order_bysolver = None, temp_marges = None):
    marges = {}
    for algorithm in algorithms:
        leftover_algorithms = list(algorithms)
        leftover_algorithms.remove(algorithm)

        all_all_perf = np.sum([max([scores[a+instance] for a in algorithms]) for instance in instances])

        if len(leftover_algorithms) == 0:
            marginal_perf = all_all_perf
        else:
            marginal_perf = all_all_perf - np.sum([max([scores[a+instance] for a in leftover_algorithms]) for instance in instances])
        
        marges[algorithm] = marginal_perf
    return marges
def permutate(algorithm, left, results):
        
        #print(results)

        if not (left in results):
            results.append(deepcopy(left))

        if len(left) == 1:
            return results
        for a in left: 
            if a != algorithm:
                leftover = deepcopy(left)
                leftover.remove(a)
                permutate(algorithm, leftover, results)

def shapley(algorithms, instances, scores):
    shapleys = {}
    for algorithm in algorithms: 
        permutations = []
        n = len(algorithms)
        permutate(algorithm,algorithms, permutations)

        score = 0
        for perm in permutations:
            with_a = np.sum([max([scores[a+instance] for a in perm]) for instance in instances])
            perm.remove(algorithm)
            if not perm:
                without_a = 0
            else:
                without_a = np.sum([max([scores[a+instance] for a in perm]) for instance in instances])

            
            #print(perm, with_a, " - ", without_a)
            score += float(with_a - without_a)/float(comb(n-1,len(perm),exact=True))
        
        score = score/len(algorithms)
        shapleys[algorithm] = score
    return shapleys
        

def read_file(file_name, algorithms, instances, scores):
    with open(file_name) as file_obj:
        top = next(file_obj).replace('\n','')
        header = (top.split (",")) #uses the header to establish what each column is
        a = header.index("algorithm")
        i = header.index("instance")
        p = header.index("performance")
        #print(header)

        data = csv.reader(file_obj)

        for n, row in enumerate(data):
            if row[a] == "" or row[i] == "" or row[p] == "":
                raise Exception("Missing Data Entry in Row: %s" % n)
            algorithm = row[a]
            instance = row[i]
            score = float(row[p])

            algorithms.add(algorithm)
            instances.add(instance)
            scores[algorithm+instance] = score

def main():
    algorithms = set([])
    instances = set([])
    scores = {}
    temp_order = None
    temp_order_bysolver = None
    temp_marges = None
    cmd_line = sys.argv[1:]
    file_name = cmd_line[0]

    #unitTest2()
    #unitTest(ascores=[1.02,1.02,0.73,0.73,0,0], mscores=[0.29,0,0], tmscores=[0.29, 0.73, 0], sscores=[0.53,0.243,0], tsscores=[0.29,0.73,0], tOrder=[["A1"],["A2","A3"]])
    #unitTest(ascores=[1.02,0,0.73,0,0,1.31], mscores=[0.29,0, 1.31], tmscores=[0.29, 0.73, 1.31], sscores=[0.655,0.365,1.31], tsscores=[0.29,0.73,1.31], tOrder=[["A1"],["A2","A3"]])
    #unitTest(ascores=[0.5,0.5,1,0,0,1.0], mscores=[0,0.5,0.5], tmscores=[1,0.5,0.5], sscores=[0.5,0.75,0.75], tsscores=[1,0.5,0.5], tOrder=[["A3"],["A2"],["A1"]])
    #unitTest(ascores=[0.5,0.5,1,0,0,1.0], mscores=[0,0.5,0.5], tmscores=[1,0.5,0.5], sscores=[0.5,0.75,0.75], tsscores=[1,0.5,0.5], tOrder=[["A3"],["A2"],["A1"]])
    #unitTest(ascores=[1,1,1,1,1,1],mscores=[0,0,0],tmscores=[0,2,0], sscores=[0.5,0.5,0.5], tsscores=[0,2,0], tOrder=[["A1","A3"],["A2"]])

    read_file(file_name, algorithms, instances, scores)
    shaps = shapley(algorithms, instances, scores)
    print("results", shaps)






if __name__ == '__main__':
    main()