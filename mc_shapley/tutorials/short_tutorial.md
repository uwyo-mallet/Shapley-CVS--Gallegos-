A short tutorial explaining what are and how to use the promiment functions in the library. For further details about the theory refer to the attached references. 

read_file(file_name)

The read_file function reads in a csv file and returns a list containing three lists. At index 0 is the list of algorithms, at index 1 is the list of the different instances each algortihm perfomed in, at index 3 is a dictionary that maps an algorithm and an instance to a score. The score being the algortihms stated performance within that instance. 

The input csv file for read_file(file_name) has 3 columns: Algorithm, Instance, Score. Each row is interpreted as the C of the algorithm A within instance B. 

Example File: 


        file name: "Sorting_Scores"

            Algorithm, Instance, Score
            A          B         C
            Quicksort  Mixed     20
            Insertion  Mixed     11
            Quicksort  Ordered   10
            Insertion  Ordered   10


Code Example:

    
    output = read_file("Sorting_Scores")

    print("Algorithms", output[0])
    print("Instances", output[1])
    print("Scores", output[2])
    


Example Output:

    
    Algorithms [Quicksort, Insertion]
    Instance [Mixed, Ordered]
    Score {QuicksortMixed : 20, InsertionMixed : 11, QuicksortOrdered : 10, InsertionOrdered : 10}
    



get_vbs_shap(algorithms, instances, scores)