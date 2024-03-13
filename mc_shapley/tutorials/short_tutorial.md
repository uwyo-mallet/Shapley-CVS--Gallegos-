# Short Tutorials

A short tutorial explaining what are and how to use the promiment functions in the library. For further details about the theory refer to the attached references. 

## read_file(file_name)

The read_file function reads in a csv file and returns a list containing three more lists. At index 0 is the list of algorithms, at index 1 is the list of the different instances each algortihm perfomed in, at index 3 is a dictionary that maps an algorithm and an instance to a performance. The performance being the algortihm's stated performance within that instance. 

The input csv file for read_file(file_name) has 3 columns: Algorithm, Instance, Performance. Each row is interpreted as the Perfomance C of the algorithm A within instance B. 

Example File:  "Sorting_Performances.csv"

            algorithm, instance, performance
            Quicksort  Mixed     20
            Insertion  Mixed     11
            Quicksort  Ordered   10
            Insertion  Ordered   10


Code Example:

    import mc_shapley as shap
    output = read_file("Sorting_Performances.csv")

    print("Algorithms", output[0])
    print("Instances", output[1])
    print("Performances", output[2])
    


Example Output:
    
    Algorithms [Quicksort, Insertion]
    Instance [Mixed, Ordered]
    Performance {QuicksortMixed : 20, InsertionMixed : 11, QuicksortOrdered : 10, InsertionOrdered : 10}

## Read_Temporal_File

The read_temporal_file function is used for reading in a csv file with temporal data. The temporal data is used to associate an algorithm (solver) with a time (version). Algorithms associated with lower values of time are assumed to have existed before those with higher values of time. This distincion is important when applying the temporal functions included in the library. The function also takes an input of a list of algorithms, this list is used to verify that the temporal file is not missing any information nor including additional algorithms.

The function returns a list containing two dictionaries. The dictionary at index 0 maps time to algorithm and the dictionary at index 1 maps an algorithm to it's asscociated time. 

The input file is constructed using two headers, denoting each column. The first header is version and the second header is solver. All listed in the version header are points in time and those listed under the solver are the algorithms associated with that time. 

Example File: "Sorting_Temporal.csv"

        version, solver
        1900     insertion
        1961     quicksort

Code Example:

        import mc_shapley as shap

        output = shap.read_file("Sorting_Performances.csv")

        algorithms = output[0]
        temp = shap.read_temporal_file("Sorting_Temporal.csv", algorithms)  
        print("Temp to Solver", temp[0])
        print("Solver to Temp", temp[1])

Example Output:

        Temp to Solver {'1900': ['Insertion'], '1961': ['Quicksort']}
        Solver to Temp {'Insertion': '1900', 'Quicksort': '1961'}

## Non-Temporal Functions

There are three non-temporal functions in the library: marginal_contributions, traditional_shap, get_vbs_shap. They all take the same arguements. A list of algorithms, A list of instances, and a dictionary of Performances (called scores), specifically the output of the *read_file* function. The marginal_contributions function returns a dictionary that maps algorithms to their marginal_contributions regarding the coallition of all of the algorithms in the list. The traditional_shap and get_vbs_shap functions return a dictionary that maps algorithms to their shapely value for the coalition of all the algorithms in the list. The difference between the traditional_shap and get_vbs_shap functions is that the get_vbs_shap function uses MC-Nets reduce the complexity of calculating the shapely value to P. Therefore it is recommended to use the traditional_shap on small inputs or for testing. If you want to know more about how MC-Nets reduce the shaple value's complexity, check out the references. 

Code Example: 

        import mc_shapley as shap

        output = shap.read_file("Sorting_Performance")

        MC = shap.marginal_contributions(output[0], output[1], output[2])
        SV1 = shap.traditional_shap(output[0], output[1], output[2])
        SV2 = shap.get_vbs_shap(output[0], output[1], output[2])

        print("Marginal Contributions", MC)
        print("Shapley Value")
        print("\tTraditional", SV1)
        print("\tMC-net", SV2)

Example Output:

        Marginal Contributions {'Quicksort': 9.0, 'Insertion': 0.0}
        Shapley Value
                Traditional {'Quicksort': 19.5, 'Insertion': 10.5}
                MC-net {'Quicksort': 19.5, 'Insertion': 10.5}

## Temporal Functions
There are two temporal functions in the library: temporal_marginal_contributions, and get_vbs_shap_temp. The temporal functions behave the same to their non-temporal counterparts, except the value these functions give algorithms is also influenced by time they are associated with (often the time they were invented). If you want to know more details about how exactly time is used in the temporal functions calculations, please refer to the references. 

The temporal functions have the same arguements as the non-temporal: algorithms, instances, scores. They also have additional arguements the tempOrder tables. These are the outputs from the read_temporal_file function. They are tables that either map algorithms to times (tempOrder) or time to algorithms (tempOrderBySolver). 

Code Example: 
        import mc_shapley as shap

        output = shap.read_file("Sorting_Performances.csv") #returns [list of algorithms, list of instances, dictionary of scores]
        
        algorithms = output[0]
        temp = shap.read_temporal_file("Sorting_Temporal.csv", algorithms) #returns [tempOrder, tempOrderBySolver]

        TMC = shap.temporal_marginal_contributions(output[0], output[1], output[2], temp[0], temp[1])
        TSV = shap.get_vbs_shap_temp(output[0], output[1], output[2], temp[0])

        print("Temporal Marginal Contributions", TMC)
        print("Temporal Shapley Value", TSV)

Example Output: 
        Temporal Marginal Contributions {'Insertion': 21.0, 'Quicksort': 9.0}
        Temporal Shapley Value {'Insertion': 21.0, 'Quicksort': 9.0}
