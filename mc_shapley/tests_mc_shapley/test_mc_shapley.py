#Code to verify the code of mc_shapley and ensure the calculated MC Shapley value is correct.
import sys
sys.path.insert(0, '../src')

from mcshapley import temporalUtils as temporal_utils
from mcshapley import shaps as shapley_cvs
import pytest as test

sys.path.insert(0, '../tests_mc_shapley')

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

    marg = shapley_cvs.marginal_contributions(algorithms, instances, scores) 
    tempMarg = shapley_cvs.temporal_marginal_contributions(algorithms, instances, scores, tempOrder, tempOrderBySolver)
    shap = shapley_cvs.get_vbs_shap(algorithms, instances, scores)
    tempShap = shapley_cvs.get_vbs_shap_temp(algorithms, instances, scores, tempOrder)

    tradShap = shapley_cvs.traditional_shap(algorithms, instances, scores)
    #print(tempMarg)

    #print(dictScores(frozenset(algorithms),margAnswersB), marg)

    functions = [(marg, margAnswers, "Marginal Contribution"), (tempMarg, tempMargAnswers, "Temporal Marginal Contribution"), 
                 (shap, shapAnswers, "Shapley Value"), (tempShap, tempShapAnswers,"Temporal Shapley"), 
                 (tradShap, shapAnswers, "Traditional Shapley Value")]
    for func in functions:
        #print(func[0], func[1])
        assert func[0] == test.approx(func[1], rel=1e-4), func[2] + " UNIT TEST FAILURE: \nReturned: " + str(func[0]) + " does not equal answer:" + str(func[1]) + "\n"


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

def test_traditional():
    [algorithms, instances, scores] = shapley_cvs.read_file("test_file2.txt") 
    assert shapley_cvs.traditional_shap(algorithms, instances, scores) == test.approx(shapley_cvs.get_vbs_shap(algorithms, instances, scores), rel=1e-4)

def test_better():
    scores = {'a ': 1, 'b' : 2, 'c' : 3, 'd' : 4, 'e' : 5, 'f' : 10}
    newScores = shapley_cvs.inverse_proportion(scores)
    assert newScores == {'a ': 9, 'b' : 8, 'c' : 7, 'd' : 6, 'e' : 5, 'f' : 0}

def test_flag():
    [algorithms, instances, scores] = shapley_cvs.read_file("test_file2.txt") 
    newScores = shapley_cvs.inverse_proportion(scores)
    assert shapley_cvs.get_vbs_shap(algorithms, instances, newScores) == test.approx(shapley_cvs.get_vbs_shap(algorithms, instances, scores, invp=True), rel=1e-4)

def test_readfile_1(): 
        algorithms = set(["A1", "A2", "A3"])
        instances = set(["1-1", "1-2"])
        scores = {"A11-1": 1.02, "A21-1": 0.73, "A31-1": 0.3, "A11-2": 1.0, "A21-2": 0.5, "A31-2": 0.21}

        ais = shapley_cvs.read_file("test_file1.txt")
        assert set(ais[0]) == algorithms, "Algorithms were not read properly: " + str(ais[0]) + " does not equal " + str(algorithms)
        assert set(ais[1]) == instances, "Instances were not read in properly: " + str(ais[1]) + " does not equal " + str(instances)
        assert ais[2] == scores, 'Score dictionary is malformed: ' + str(ais[2]) + " does not equal " + str(scores)

def test_readfile_2(): 
        algorithms = set(["insertion", "first", "random"])
        instances = set(["1-10000", "2-10000"])
        scores = {"insertion1-10000": 0, "first1-10000": 0, "random1-10000": 0.01, "insertion2-10000": 0, "first2-10000": 0.96, "random2-10000": 0.01}

        ais = shapley_cvs.read_file("test_file2.txt")
        assert set(ais[0]) == algorithms, "Algorithms were not read properly: " + str(ais[0]) + " does not equal " + str(algorithms) + "\n"
        assert set(ais[1]) == instances, "Instances were not read in properly: " + str(ais[1]) + " does not equal " + str(instances) + "\n"
        assert ais[2] == scores, 'Score dictionary is malformed: ' + str(ais[2]) + " does not equal " + str(scores) + "\n"

        t_order = {"1946": ["insertion"], "1961": ["first", "random"]}
        t_order_bysolver = {"insertion": "1946", "first": "1961", "random": "1961"}
        temporal = shapley_cvs.read_temporal_file("temp_test_file2.csv", ais[0])
        assert temporal[0] == t_order, "Temporal order was not read properly: " + str(temporal[0]) + " does not equal " + str(t_order) + "\n" 
        assert temporal[1] == t_order_bysolver, "Temporal order by solver was not formed properly: " + str(temporal[1]) + " does not equal " + str(t_order_bysolver) + "\n" 

def test_readfile_3(): 
    algorithms = set(["A1", "A2", "A3", "A4", "A5"])
    instances = set(["1-1", "1-2", "1-3", "1-4", "1-5", "1-6", "1-7"])

    ais = shapley_cvs.read_file("test_file3.csv")
    assert set(ais[0]) == algorithms, "Algorithms were not read properly: " + str(ais[0]) + " does not equal " + str(algorithms) + "\n"
    assert set(ais[1]) == instances, "Instances were not read in properly: " + str(ais[1]) + " does not equal " + str(instances) + "\n"
    assert ais[2]["A21-3"] == 0.11, "Score dictionary is malformed: " + str(ais[2]["A21-3"]) + " does not equal 0.11" + "\n"
    assert ais[2]["A11-3"] == 0.15, "Score dictionary is malformed: " + str(ais[2]["A11-3"]) + " does not equal 0.15" + "\n"
    assert ais[2]["A41-3"] == 0.45, "Score dictionary is malformed: " + str(ais[2]["A41-3"]) + " does not equal 0.45" + "\n"
    assert ais[2]["A41-5"] == 0.28, "Score dictionary is malformed: " + str(ais[2]["A41-5"]) + " does not equal 0.28" + "\n"
    assert ais[2]["A51-7"] == 1, "Score dictionary is malformed: " + str(ais[2]["A51-7"]) + " does not equal 0.15" + "\n"
    assert ais[2].get("A31-4") is  None, "Failure, wrote new information into data: A3, 1-4"

def test_missing_entry(): 
    with test.raises(ValueError) as exc_info: 
        shapley_cvs.read_file("test_file4.csv")
    assert str(exc_info.value) == "Missing Data Entry in Row: 18", "Failed to raise proper exception: " 

def test_score_conflict():
    with test.raises(ValueError) as exc_info: 
        shapley_cvs.read_file("test_file5.csv")
    assert str(exc_info.value) == "duplicate entries, Start at Row: 17", "Failed to raise proper exception: " 

def test_temporal_missing(): 
    algorithms = ["A1", "A2", "A3", "A4", "A5"]
    with test.raises(ValueError) as exc_info: 
        shapley_cvs.read_temporal_file("temp_test_file3.csv", algorithms)
    assert str(exc_info.value) == "No temporal information found for A5!", "Failed to raise proper exception: " 

'''
def test_kotthoff():
    #print(sys.path)
    [algorithms, instances, scores] = shapley_cvs.read_file("test_file_park.csv") 
    shapleys = shapley_cvs.get_vbs_shap(algorithms, instances, scores, invp=False)
    print(shapleys)
    assert shapleys == test.approx({'qsort4': 0, '1978 + cutoff + median 3': 0, '1993 + median 9 + split end': 0, '1993 + median 9': 0, '2009': 0}, rel=1e-4)'''