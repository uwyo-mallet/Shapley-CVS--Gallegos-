import csv
from scipy.special import comb
import numpy as np
from copy import deepcopy


def get_vbs_shap(algorithms, instances, scores):
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

def get_vbs_shap_temp(algorithms, instances, temporal_order, scores):
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

#Calculates the Shapley value the typical way, as Shapley intended.
#Does not utilize MC-nets for speed up, thus on large sets of data it can take a while to return
#Calculates Shapley value by finding all of the permutations of the set of algorithms
#Than calcuting the average marginal contribution over all of the permutations, this is done for each algorithm
#It returns a dictonary that maps the algorithm to it's shapley score
def traditional_shap(algorithms, instances, scores):
    shapleys = {}
    for algorithm in algorithms: 
        permutations = []
        n = len(algorithms)
        permutate_coalitions(algorithm,algorithms, permutations)

        score = 0
        for perm in permutations:

            with_a = np.sum([max((0 if (scores.get(a+instance) is None) else scores[a+instance]) for a in perm) for instance in instances])
            perm.remove(algorithm)
            
            if not perm:
                without_a = 0
            else:
                without_a = np.sum([max((0 if (scores.get(a+instance) is None) else scores[a+instance]) for a in perm) for instance in instances])

            
            #print(perm, with_a, " - ", without_a)
            score += float(with_a - without_a)/float(comb(n-1,len(perm),exact=True))
        
        score = score/len(algorithms)
        shapleys[algorithm] = score
    return shapleys

#calcultes the marginal contributions for each algorithm
#can be overloaded to marginal and temporal maginal contributions
def marginal_contributions(algorithms, instances, scores, temp_order = None, temp_order_bysolver = None, temp_marges = None):
    marges = {}
    for algorithm in algorithms:
        leftover_algorithms = list(algorithms)
        leftover_algorithms.remove(algorithm)

        all_all_perf = np.sum([max(scores[a+instance] for a in algorithms) for instance in instances])

        if len(leftover_algorithms) == 0:
            marginal_perf = all_all_perf
        else:
            marginal_perf = all_all_perf - np.sum([max(scores[a+instance] for a in leftover_algorithms) for instance in instances])
        
        marges[algorithm] = marginal_perf

        if temp_marges is not None:
            thisversion = temp_order_bysolver[algorithm]
            versions = [y for y in temp_order.keys() if y <= thisversion]
            available_algorithms = [alg for version in versions for alg in temp_order[version]]

            other_algorithms = list(available_algorithms)
            other_algorithms.remove(algorithm)

            all_perf =  np.sum([max(scores[a+instance] for a in available_algorithms) for instance in instances])
            if len(other_algorithms) == 0:
                tmp_marginal_perf = all_perf
            else:
                tmp_marginal_perf = all_perf - np.sum([max(scores[a+instance] for a in other_algorithms) for instance in instances])
        
            temp_marges[algorithm] = tmp_marginal_perf
    return marges

#calculates the temporal marginal contributions for each algorithm
#just calculates the temporal marginal contributions
def temporal_marginal_contributions(algorithms, instances, scores, temp_order, temp_order_bysolver):
    temp_marges = {}
    for algorithm in algorithms:
        thisversion = temp_order_bysolver[algorithm]
        versions = [y for y in temp_order.keys() if y <= thisversion]
        available_algorithms = [alg for version in versions for alg in temp_order[version]]

        other_algorithms = list(available_algorithms)
        other_algorithms.remove(algorithm)

        all_perf = np.sum([max(scores[a+instance] for a in available_algorithms) for instance in instances])
        if len(other_algorithms) == 0:
            tmp_marginal_perf = all_perf
        else:
            tmp_marginal_perf = all_perf - np.sum([max(scores[a+instance] for a in other_algorithms) for instance in instances])
        
        temp_marges[algorithm] = tmp_marginal_perf
    return temp_marges

#Opens the file inputed through the terminal, converts the data in the CVS to information containers the function needs, a
#Algorithms --> gathers all the names of the different algorithms that will be evaluated.
#Instances -->  all the different instances algorithms were run in. 
#Scores --> a dictionary that maps an algorithm used and an instance to the score obtained by that algorithm in that test intsance.
#returns an array of each list in the order, [algortihms, instances, scores]
def read_file(file_name):
    scores = {}
    algorithms = set()
    instances = set()

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
                raise ValueError("Missing Data Entry in Row: %d" % (n+2))
            
            algorithm = row[a]
            instance = row[i]
            score = float(row[p])

            algorithms.add(algorithm)
            instances.add(instance)
            if scores.get(algorithm+instance) is None:
                scores[algorithm+instance] = score
            elif scores[algorithm+instance] != score:
                raise ValueError("Two Different Scores for the Same Algorithm-Instance, Start at Row: %d" % (n+2))

    return [list(algorithms), list(instances), scores]

#Opens the file inputed through the terminal, converts the data in the CVS to information containers the function needs, a
#This reads the temporal file which provides information about the time an algorithm is made
#This time is used to attribute more or less credit to an algorithm for how much it contributed at that time
#temp_order by solver: The algorithm maps to a time (version)
#temp_order: time(version) maps to to algorithm
def read_temporal_file(file_name, algorithms):
    temp_order = {}
    temp_order_bysolver = {}

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
            raise ValueError("No temporal information found for %s!" % algorithm)
    return [temp_order, temp_order_bysolver]

#permutes all the possible subsets of algorithms that includes the inputed algorithm
#Can also be interpreted as generating all the joining orders up to the inputed algorithm of coalitions
def permutate_coalitions(algorithm, left, results):
        if not (left in results):
            results.append(deepcopy(left))

        if len(left) == 1:
            return results
        
        #leftover = [a for a in left if a != algorithm]
        for a in left: 
            if a != algorithm:
                leftover = deepcopy(left)
                leftover.remove(a)
                permutate_coalitions(algorithm, leftover, results)
        


