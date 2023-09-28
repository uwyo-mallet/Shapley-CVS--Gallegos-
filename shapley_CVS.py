from scipy.special import comb
import numpy as np
import sys
import re

import pytest as test
import math

import csv

def getVBSShap(instances, algorithms, scores):
    '''
    instances - the set of different instances that were solved
    algorithms - the set of available algorithms.
    metric - the performance metric from (algorithm,instance) to real number. Higher is better.

    Returns a dictionary from algorithms to their Shapley value, where the coalitional function is
    $$ v(S) = \frac{1}{|X|} \sum_{x\in X} \max_{s\in S} metric(s,x),$$
    where X is the set of instances. This is the "average VBS game" with respect to the given instances,
    algorithms.
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


        #print(instance_algorithms)
        d += 1
        #if not(d % len(instances)*.01): print(d/len(instances)*100, "%", "done") #Percentage marks to know the code is processing and not infinite looping

        #For each algorithm, from worst to best.
        for i in range(len(instance_algorithms)):
            #print("loop", instance_algorithms[i])
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
            value = float(scores[instance_algorithms[i]+instance])
            #sys.stderr.write('Value of this rule : 1/%d, %.4f\n' % (m,value))

            #Calculate the rule Shapley values, and add them to the global Shapley values.

            #Shapley value for positive literals in the rule.
            pos_shap = float(value)/float(pos*comb(pos+neg,neg,exact=True))
            #Shapley value for negative literals in the rule.
            if neg > 0:
                neg_shap = -1*float(value)/float(neg*comb(pos+neg,pos,exact=True))
            else:
                neg_shap = None

            #print(ialgorithm)
            #Update the Shapley value for the literals appearing in the rule.
            for j in range(i,len(instance_algorithms)):
                jalgorithm = instance_algorithms[j]

                if jalgorithm not in shapleys:
                    shapleys[jalgorithm] = 0
                    #print("None")
                if j == i:
                    shapleys[jalgorithm] += pos_shap
                    #print("+",pos_shap, jalgorithm)
                else:
                    shapleys[jalgorithm] += neg_shap
                    #print("-",neg_shap, jalgorithm)
    return shapleys

def getVBSShapTemp(instances, algorithms, temporal_order, scores):
    '''
    instances - the set of different instances that were solved.
    algorithms - the set of available algorithms.
    temporal_order - the map of version to solvers
    metric - the performance metric from (algorithm,instance) to real number. Higher is better.

    Returns a dictionary from algorithms to their Shapley value, where the coalitional function is
    $$ v(S) = \frac{1}{|X|} \sum_{x\in X} \max_{s\in S} metric(s,x),$$
    where X is the set of instances. This is the "average VBS game" with respect to the given instances,
    algorithms.
    '''

    shapleys = {alg: 0 for alg in algorithms}

    n = len(algorithms)

    for instance in instances:
        #sys.stderr.write('Processing instance "%s"...\n' % instance) #progress notification]=

        prevbest = 0

        for version in sorted(temporal_order.keys()):
            #sys.stderr.write('Processing version "%s"...\n' % version)
            # Sort algorithms from that version increasing by metric value
            #instance_algorithms = sorted([alg for alg in algorithms if re.match("glucose", alg)], key=lambda a : metric(a,instance))
            instance_algorithms = sorted(temporal_order[version], key=lambda a : scores[a+instance])
            #sys.stderr.write('Sorted algorithms for %s: %s\n' % (version, instance_algorithms))
            ni = len(instance_algorithms)
        
            for i in range(ni):
                ialgorithm = instance_algorithms[i]

                #sys.stderr.write('Processing the rule corresponding to %d-th algorithm "%s" being the best in the coalition.\n' % (i, ialgorithm))

                # The MC-rule is that you must have the algorithm and none of the better ones.
                '''
                If x is the instance and s_1^x,...,s_n^x are sorted from worst, then the rule's pattern is:
                $$ p_i^x = s_i^x \wedge \bigwedge_{j=i+1}^n \overline{s}_j^x $$
                and its weight is 
                $$ w_i^x = metric(s_i^x,x).$$
                '''
                pos = 1
                neg = ni - i - 1

                if neg < 0:
                    raise Exception("This should never happen.")

                value = max(0, scores[instance_algorithms[i]+instance] - prevbest)
                #sys.stderr.write('Value of this rule : %.4f\n' % (value))

                # Calculate the rule Shapley values, and add them to the global Shapley values.
                combns = float(pos + neg)
                pos_shap = float(value / combns)
                shapleys[ialgorithm] += float(pos_shap)
                
                if neg > 0:
                    neg_shap = value / (neg * combns)
                    for j in range(i + 1, ni):
                        jalgorithm = instance_algorithms[j]
                        shapleys[jalgorithm] -= neg_shap

            prevbest = max(prevbest, scores[instance_algorithms[-1]+instance])

    return shapleys

#calcultes the marginal contributions for each algorithm
#can be overloaded to marginal and temporal maginal contributions
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

        if temp_marges is not None:
            thisversion = temp_order_bysolver[algorithm]
            versions = [y for y in temp_order.keys() if y <= thisversion]
            available_algorithms = [alg for version in versions for alg in temp_order[version]]

            other_algorithms = list(available_algorithms)
            other_algorithms.remove(algorithm)

            all_perf =  np.sum([max([scores[a+instance] for a in available_algorithms]) for instance in instances])
            if len(other_algorithms) == 0:
                tmp_marginal_perf = all_perf
            else:
                tmp_marginal_perf = all_perf - np.sum([max([scores[a+instance] for a in other_algorithms]) for instance in instances])
        
            temp_marges[algorithm] = tmp_marginal_perf
    return marges

#calculates the temporal marginal contributions for each algorithm
#just calculates the temporal marginal contributions
def temporal_marginal_contributions(instances, algorithms, scores, temp_order, temp_order_bysolver):
    tempMarges = {}
    for algorithm in algorithms:
        thisversion = temp_order_bysolver[algorithm]
        versions = [y for y in temp_order.keys() if y <= thisversion]
        available_algorithms = [alg for version in versions for alg in temp_order[version]]

        other_algorithms = list(available_algorithms)
        other_algorithms.remove(algorithm)

        all_perf = np.sum([max([scores[a+instance] for a in available_algorithms]) for instance in instances])
        if len(other_algorithms) == 0:
            tmp_marginal_perf = all_perf
        else:
            tmp_marginal_perf = all_perf - np.sum([max([scores[a+instance] for a in other_algorithms]) for instance in instances])
        
        tempMarges[algorithm] = tmp_marginal_perf
    return tempMarges

#Opens the file inputed through the terminal, converts the data in the CVS to information containers the function needs, a
#Algorithms --> gathers all the names of the different algorithms that will be evaluated.
#Instances -->  all the different instances algorithms were run in. 
#Scores --> a dictionary that maps an algorithm used and an instance to the score obtained by that algorithm in that test intsance.
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

#Opens the file inputed through the terminal, converts the data in the CVS to information containers the function needs, a
#This reads the temporal file which provides information about the time an algorithm is made
#This time is used to attribute more or less credit to an algorithm for how much it contributed at that time
#temp_order: The algorithm maps to a time (version)
#temp_order by sover: time(version) maps to to algorithm
def read_temporal_file(file_name, temp_order, temp_order_bysolver, algorithms):
    with open(file_name, 'r') as f:
        reader = csv.DictReader(f)
        #print(reader)
        for row in reader:
            if not row['version'] in temp_order:
                temp_order[row['version']] = []
            temp_order[row['version']].append(row['solver'])
            temp_order_bysolver[row['solver']] = row['version']
    for algorithm in algorithms:
        if not algorithm in temp_order_bysolver:
            raise Exception("No temporal information found for %s!" % algorithm)

#converts a tempOrder dict to a tempOrderbySolver
def toBySolver(tempOrder):
    bySolver = {}
    for time in tempOrder.keys():
        for alg in tempOrder[time]:
            bySolver[alg] = time
    return bySolver

#converts an array of algorithm names to a temporal list, considering the algorithms from the begining to be more recent than those at the end
def toTempOrder(tOrder):
    tempOrder = {}
    for i,algs in enumerate(tOrder):
        tempOrder[str(len(tOrder)-i)] = algs
    return tempOrder

#old testing code
# algorithms = ["insertion", "insertion", "first"]
# instances = [0, 1, 2]
# scores = [2.4, 1.05, 0.96]
# shaps = getVBSShap(instances, algorithms, scores)
# print(shaps)

#verifies that a dictionary has the same values according to input array

def dictScores(algorithms, inputScores):
    scores = {}
    for i, alg in enumerate(algorithms):
            scores[alg] = inputScores[i]
    return scores

'''
Function that creates a unit test from array inputs, utlizes only two instances

#ascore = array of scores of alogrithm at an instance, ordered by algorithm than instance, I.E. A1T2 comes before A2T1, A1T1 comes before A1T2
#mscores = array of what marginal contributions of each algorithm should be, algorithms correspond with the index-1
#tmscores = array of what the temporal marginal contributions of algorithms should be, ordered like mscores
#sscores = array of what shapley values of algorithms should be, ordered like mscores
#tscores = array of what temporal shapley values of algorithms should be, ordered like mscores
#tOrder = array of the temporal location of algorithms, ordered like mscores
'''
def unitTest(ascores, mscores, tmscores, sscores, tsscores, tOrder):
    algorithms = set(["A1","A2","A3"])
    instances = set(["T-1", "T-2"])
    scores = {"A1T-1": ascores[0],"A1T-2": ascores[1], "A2T-1" : ascores[2], "A2T-2": ascores[3], "A3T-1": ascores[4],  "A3T-2" : ascores[5]}
    tempOrder = toTempOrder(tOrder)
    tempOrderBySolver = toBySolver(tempOrder)
    #print(tempOrder, tempOrderBySolver)

    #margAnswersB = [0.29,0,1.31]
    margAnswers = {"A1": mscores[0], "A2": mscores[1], "A3" :mscores[2]}
    tempMargAnswers = {"A1": tmscores[0], "A2": tmscores[1], "A3" : tmscores[2]}
    tempShapAnswers = {"A1": tsscores[0], "A2": tsscores[1], "A3" : tsscores[2]}
    shapAnswers ={"A1": sscores[0], "A2": sscores[1], "A3" : sscores[2]}
    



    #answers = [margAnswers, tempMargAnswers, tempShapAnswers, shapAnswers]

    marg = marginal_contributions(instances, algorithms, scores) 
    tempMarg = temporal_marginal_contributions(instances, algorithms, scores, tempOrder, tempOrderBySolver)
    shap = getVBSShap(instances, algorithms, scores)
    tempShap = getVBSShapTemp(instances, algorithms, tempOrder, scores)
    #print(tempMarg)

    #print(dictScores(frozenset(algorithms),margAnswersB), marg)

    functions = [(marg, margAnswers, "Marginal Contribution"), (tempMarg, tempMargAnswers, "Temporal Marginal Contribution"), (shap, shapAnswers, "Shapley Value"), (tempShap, tempShapAnswers,"Temporal Shapley")]
    for func in functions:
        #print(func[0], func[1])
        assert func[0] == test.approx(func[1], rel=1e-4), func[2]+" UNIT TEST FAILURE: \nReturned: "+str(func[0])+" does not equal answer:"+str(func[1])+"\n"


def main():
    algorithms = set([])
    instances = set([])
    scores = {}
    temp_order = None
    temp_order_bysolver = None
    temp_marges = None
    cmd_line = sys.argv[1:]
    file_name = cmd_line[0]

    
    unitTest(ascores=[1.02,0,0.73,0,0,1], mscores=[0.29,0,1], tmscores=[0.29, 0, 1], sscores=[0.655,0.365,1], tsscores=[0.655,0.365,1], tOrder=[["A1","A2","A3"]])
    unitTest(ascores=[1.02,0,0.73,0,0,1.31], mscores=[0.29,0, 1.31], tmscores=[0.29, 0.73, 1.31], sscores=[0.655,0.365,1.31], tsscores=[0.29,0.73,1.31], tOrder=[["A3"],["A1"],["A2"]])
    unitTest(ascores=[0.5,0.5,1,0,0,1.0], mscores=[0,0.5,0.5], tmscores=[1,0.5,0.5], sscores=[0.5,0.75,0.75], tsscores=[1,0.5,0.5], tOrder=[["A3","A2"],["A1"]])
    unitTest(ascores=[1,1,1,1,1,1],mscores=[0,0,0],tmscores=[0,0,2], sscores=[0.66666,0.66666,0.66666], tsscores=[0,0,2], tOrder=[["A1","A2"],["A3"]])
    unitTest(ascores=[1.02,0,0.73,0,0,0], mscores=[0.29,0,0], tmscores=[0.29, 0, 0], sscores=[0.655,0.365,0], tsscores=[0.655,0.365,0], tOrder=[["A1","A2"], ["A3"]])

    read_file(file_name, algorithms, instances, scores)

    #checks if there is a second file, indicating that the user wants a temporal calculation by adding the temporal file
    if len(cmd_line) > 1:
        temp_order = {}
        temp_order_bysolver = {}
        temp_file_name = cmd_line[1]
        read_temporal_file(temp_file_name, temp_order, temp_order_bysolver, algorithms)
        temp_shaps = getVBSShapTemp(instances, algorithms, temp_order, scores)
        temp_marges = {}

    #print(temp_order)
    shaps = getVBSShap(instances, algorithms, scores)
    marges = marginal_contributions(instances, algorithms, scores, temp_order, temp_order_bysolver, temp_marges)

    #outputs are dictioaries, these print them out legiablley
    #print(temp_order)
    for key in shaps.keys():
        if len(cmd_line) > 1:
            print(key+":", "\n\tShapley :",shaps[key], "\n\tMarginal Contribution:", marges[key], "\n\tTemporal Shapley:", temp_shaps[key], "\n\tTemporal MC:", temp_marges[key])
        else:
            print(key+":", "\n\tShapley :",shaps[key], "\n\tMarginal Contribution:", marges[key])


if __name__ == '__main__':
    main()