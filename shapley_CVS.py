from scipy.special import comb
import numpy as np
import sys
import re

import math

import csv

def getVBSShap(instances, algorithms, scores):
    '''
    instances - the instances to solve.
    algorithms - the set of available algorithms.
    metric - the performance metric from (algorithm,instance) to real number. Higher is better.

    Returns a dictionary from algorithms to their Shapley value, where the coalitional function is
    $$ v(S) = \frac{1}{|X|} \sum_{x\in X} \max_{s\in S} metric(s,x),$$
    where X is the set of instances. This is the "average VBS game" with respect to the given instances,
    algorithms and metric.
    '''
    n = len(algorithms)
    m = len(instances)

    shapleys = {}

    d = 0
    #For each instance
    for instance in instances:
        #sys.stderr.write('Processing instance "%s" ...\n' % instance)
        #Sort algorithms by decreasing order of performance.
        #instance_algorithms = sorted([alg for alg in algorithms if re.match("glucose", alg)], key=lambda a : metric(a,instance))
        instance_algorithms = sorted(list(algorithms), key=lambda a :scores[a+instance])
        d += 1
        if not(d % len(instances)*.01): print(d/len(instances)*100, "%", "done") #Percentage marks to know the code is processing and not infinite looping

        #For each algorithm, from worst to best.
        for i in range(len(instance_algorithms)):
            #print(i)
            ialgorithm = instance_algorithms[i]

            #sys.stderr.write('Processing the rule corresponding to %d-th algorithm "%s" being the best in the coalition.\n' % (i,ialgorithm))

            #The MC-rule is that you must have the algorithm and none of the better ones.
            '''
            If x is the instance and s_1^x,...,s_n^x are sorted from worst, then the rule's pattern is:
            $$ p_i^x = s_i^x \wedge \bigwedge_{j=i+1}^n \overline{s}_j^x $$
            and its weight is 
            $$ w_i^x = metric(s_i^x,x).$$
            '''
            pos = 1
            neg = n-i-1

            #metricvalue = metric(ialgorithm,instance)
            ## normalised as fraction of instances
            #value = 1/float(m)*metricvalue
            value = scores[instance_algorithms[i]+instance]
            #sys.stderr.write('Value of this rule : 1/%d * %.4f = %.4f\n' % (m,metricvalue,value))

            #Calculate the rule Shapley values, and add them to the global Shapley values.

            #Shapley value for positive literals in the rule.
            pos_shap = value/float(pos*comb(pos+neg,neg,exact=True))
            #Shapley value for negative literals in the rule.
            if neg > 0:
                neg_shap = -value/float(neg*comb(pos+neg,pos,exact=True))
            else:
                neg_shap = None

            #print(ialgorithm)
            #Update the Shapley value for the literals appearing in the rule.
            for j in range(i,len(instance_algorithms)):
                jalgorithm = instance_algorithms[j]

                if jalgorithm not in shapleys:
                    shapleys[jalgorithm] = 0

                if j == i:
                    shapleys[jalgorithm] += pos_shap
                else:
                    shapleys[jalgorithm] += neg_shap
    return shapleys


#old testing code
# algorithms = ["insertion", "insertion", "first"]
# instances = [0, 1, 2]
# scores = [2.4, 1.05, 0.96]
# shaps = getVBSShap(instances, algorithms, scores)
# print(shaps)

def main():
    algorithms = set([])
    instances = set([])
    scores = {}
    file_name = sys.argv[1]

    #Opens the file inputed through the terminal, converts the data in the CVS to information containers the function needs, a
    #Algorithms --> gathers all the names of the different algorithms that will be evaluated.
    #Instances -->  all the different instances algorithms were run in. 
    #Scores --> a dictionary that maps an algorithm used and an instance to the score obtained by that algorithm in that test intsance.
    with open(file_name) as file_obj:
        top = next(file_obj).replace('\n','')
        header = (top.split (","))
        data = csv.reader(file_obj)
        for row in data:
            algorithms.add(row[0])
            instances.add(row[1])
            scores[row[0]+row[1]] = float(row[2])
    
        print(getVBSShap(instances, algorithms, scores))

if __name__ == '__main__':
    main()