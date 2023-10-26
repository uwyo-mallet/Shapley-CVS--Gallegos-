#Code to verify the code of mc_shapley and ensure the calculated MC Shapley value is correct.
from .. import temporal_utils
from .. import shapley_cvs
import pytest as test

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
def unitTestTemplate(ascores, mscores, tmscores, sscores, tsscores, tOrder):
    algorithms = ["A1","A2","A3"]
    instances = ["T-1", "T-2"]


    scores = {"A1T-1": ascores[0],"A1T-2": ascores[1], "A2T-1" : ascores[2], "A2T-2": ascores[3], "A3T-1": ascores[4],  "A3T-2" : ascores[5]}
    tempOrder = temporal_utils.toTempOrder(tOrder)
    tempOrderBySolver = temporal_utils.toBySolver(tempOrder)
    #print(tempOrder, tempOrderBySolver)

    #margAnswersB = [0.29,0,1.31]

    margAnswers = {"A1": mscores[0], "A2": mscores[1], "A3" :mscores[2]}
    tempMargAnswers = {"A1": tmscores[0], "A2": tmscores[1], "A3" : tmscores[2]}
    tempShapAnswers = {"A1": tsscores[0], "A2": tsscores[1], "A3" : tsscores[2]}
    shapAnswers ={"A1": sscores[0], "A2": sscores[1], "A3" : sscores[2]}
    



    #answers = [margAnswers, tempMargAnswers, tempShapAnswers, shapAnswers]

    marg = shapley_cvs.marginal_contributions(instances, algorithms, scores) 
    tempMarg = shapley_cvs.temporal_marginal_contributions(instances, algorithms, scores, tempOrder, tempOrderBySolver)
    shap = shapley_cvs.getVBSShap(instances, algorithms, scores)
    tempShap = shapley_cvs.getVBSShapTemp(instances, algorithms, tempOrder, scores)
    #print(tempMarg)

    #print(dictScores(frozenset(algorithms),margAnswersB), marg)

    functions = [(marg, margAnswers, "Marginal Contribution"), (tempMarg, tempMargAnswers, "Temporal Marginal Contribution"), (shap, shapAnswers, "Shapley Value"), (tempShap, tempShapAnswers,"Temporal Shapley")]
    for func in functions:
        #print(func[0], func[1])
        assert func[0] == test.approx(func[1], rel=1e-4), func[2]+" UNIT TEST FAILURE: \nReturned: "+str(func[0])+" does not equal answer:"+str(func[1])+"\n"


def test_unit_test_1():
    unitTestTemplate(ascores=[1.02,0,0.73,0,0,1], mscores=[0.29,0,1], tmscores=[0.29, 0, 1], sscores=[0.655,0.365,1], tsscores=[0.655,0.365,1], tOrder=[["A1","A2","A3"]])

def test_unit_test_2():
    unitTestTemplate(ascores=[1.02,0,0.73,0,0,1.31], mscores=[0.29,0, 1.31], tmscores=[0.29, 0.73, 1.31], sscores=[0.655,0.365,1.31], tsscores=[0.29,0.73,1.31], tOrder=[["A3"],["A1"],["A2"]])

def test_unit_test_3():
    unitTestTemplate(ascores=[0.5,0.5,1,0,0,1.0], mscores=[0,0.5,0.5], tmscores=[1,0.5,0.5], sscores=[0.5,0.75,0.75], tsscores=[1,0.5,0.5], tOrder=[["A3","A2"],["A1"]])

def test_unit_test_4():
    unitTestTemplate(ascores=[1,1,1,1,1,1],mscores=[0,0,0],tmscores=[0,0,2], sscores=[0.66666,0.66666,0.66666], tsscores=[0,0,2], tOrder=[["A1","A2"],["A3"]])

def test_unit_test_5():
    unitTestTemplate(ascores=[1.02,0,0.73,0,0,0], mscores=[0.29,0,0], tmscores=[0.29, 0, 0], sscores=[0.655,0.365,0], tsscores=[0.655,0.365,0], tOrder=[["A1","A2"], ["A3"]])