#Code for generating examples to be displayed in the tutorial
import mc_shapley as shap

def main(): 
    output = shap.read_file("Sorting_Scores.txt")

    print("Algorithms", output[0])
    print("Instances", output[1])
    print("Scores", output[2])

    MC = shap.marginal_contributions(output[0], output[1], output[2])
    SV1 = shap.traditional_shap(output[0], output[1], output[2])
    SV2 = shap.get_vbs_shap(output[0], output[1], output[2])
    
    print("Marginal Contributions", MC)
    print("Shapley Value")
    print("\tTraditional", SV1)
    print("\tMC-net", SV2)
    
    temp = shap.read_temporal_file("Sorting_Temporal.txt", output[0])  
    print("Temp to Solver", temp[0])
    print("Solver to Temp", temp[1])
    
    TMC = shap.temporal_marginal_contributions(output[0], output[1], output[2], temp[0], temp[1])
    TSV = shap.get_vbs_shap_temp(output[0], output[1], output[2], temp[0])
    
    print("Temporal Marginal Contributions", TMC)
    print("Temporal Shapley Value", TSV)


if __name__ == "__main__":
    main()