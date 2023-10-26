#Functions found to be useful for creating or manipulating temporal lists

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