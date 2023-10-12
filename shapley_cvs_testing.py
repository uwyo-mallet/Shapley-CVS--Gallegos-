import mc_shapley
import sys

def main():
    algorithms = set([])
    instances = set([])
    scores = {}
    temp_order = None
    temp_order_bysolver = None
    temp_marges = None
    cmd_line = sys.argv[1:]
    file_name = cmd_line[0]

    
    mc_shapley.unitTest(ascores=[1.02,0,0.73,0,0,1], mscores=[0.29,0,1], tmscores=[0.29, 0, 1], sscores=[0.655,0.365,1], tsscores=[0.655,0.365,1], tOrder=[["A1","A2","A3"]])
    '''unitTest(ascores=[1.02,0,0.73,0,0,1.31], mscores=[0.29,0, 1.31], tmscores=[0.29, 0.73, 1.31], sscores=[0.655,0.365,1.31], tsscores=[0.29,0.73,1.31], tOrder=[["A3"],["A1"],["A2"]])
    unitTest(ascores=[0.5,0.5,1,0,0,1.0], mscores=[0,0.5,0.5], tmscores=[1,0.5,0.5], sscores=[0.5,0.75,0.75], tsscores=[1,0.5,0.5], tOrder=[["A3","A2"],["A1"]])
    unitTest(ascores=[1,1,1,1,1,1],mscores=[0,0,0],tmscores=[0,0,2], sscores=[0.66666,0.66666,0.66666], tsscores=[0,0,2], tOrder=[["A1","A2"],["A3"]])
    unitTest(ascores=[1.02,0,0.73,0,0,0], mscores=[0.29,0,0], tmscores=[0.29, 0, 0], sscores=[0.655,0.365,0], tsscores=[0.655,0.365,0], tOrder=[["A1","A2"], ["A3"]])
    '''
    mc_shapley.read_file(file_name, algorithms, instances, scores)

    #checks if there is a second file, indicating that the user wants a temporal calculation by adding the temporal file
    if len(cmd_line) > 1:
        temp_order = {}
        temp_order_bysolver = {}
        temp_file_name = cmd_line[1]
        mc_shapley.read_temporal_file(temp_file_name, temp_order, temp_order_bysolver, algorithms)
        temp_shaps = mc_shapley.getVBSShapTemp(instances, algorithms, temp_order, scores)
        temp_marges = {}

    #print(temp_order)
    shaps = mc_shapley.getVBSShap(instances, algorithms, scores)
    marges = mc_shapley.marginal_contributions(instances, algorithms, scores, temp_order, temp_order_bysolver, temp_marges)

    #outputs are dictioaries, these print them out legiablley
    #print(temp_order)
    for key in shaps.keys():
        if len(cmd_line) > 1:
            print(key+":", "\n\tShapley :",shaps[key], "\n\tMarginal Contribution:", marges[key], "\n\tTemporal Shapley:", temp_shaps[key], "\n\tTemporal MC:", temp_marges[key])
        else:
            print(key+":", "\n\tShapley :",shaps[key], "\n\tMarginal Contribution:", marges[key])


if __name__ == '__main__':
    main()