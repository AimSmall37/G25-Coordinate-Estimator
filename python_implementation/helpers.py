import numpy as np 
import pandas as pd 

# Helper functions to prepare data for linear algebra solving
def subset_populations(distance_sheet, reference_sheet):
    distance_df = pd.read_csv(distance_sheet, sep="\t")
    if distance_df.shape[0] < 26: 
        raise ValueError(f"File contains {distance_df.shape[0]} distances. Program needs at least 26 distances to execute properly. Exiting.")
    target_pops = distance_df.iloc[:, 1]
    sample_df = pd.read_csv(reference_sheet, header=None)
    if sample_df.shape[0] < 26:
        raise ValueError(f"File contains {sample_df.shape[0]} distances. Program needs at least 26 reference samples to execute properly. Exiting.")
    new_subset = sample_df[sample_df.iloc[:, 0].isin(target_pops)]
    merged_df = pd.merge(distance_df, new_subset, 
                         left_on=distance_df.iloc[:, 1], 
                         right_on=new_subset.iloc[:, 0], 
                         how="inner")
    if merged_df.shape[0] < 26: 
        raise ValueError("There are populations in the distances file that do not exist in the reference file. Please update your reference file accordingly. Exiting.")
    cleaned_df = merged_df.iloc[0:27, np.r_[0:2, 4:29]] # return only the first 26 distances 
    cleaned_df.columns = ["population", "euclidean_distance", "PC1", "PC2", "PC3", "PC4", "PC5", "PC6", "PC7", "PC8", "PC9", "PC10", "PC11", "PC12", "PC13", "PC14", "PC15", "PC16", "PC17", "PC18", "PC19", "PC20", "PC21", "PC22", "PC23", "PC24", "PC25"]
    return cleaned_df

def get_constants(my_df): 
    '''We can expand the euclidean distance formula to get 
    euclidean^2 = (x1^2 - 2x1PC1 + PC1^2) + ... + (x25^2 - 2x25PC25 + PC25^2).
    Since the PCs are constants, we can combine these like terms and return 
    PC1^2 + ... + PC25^2 - euclidean^2 = 0'''
    my_df = my_df.copy()
    my_df["sum_of_squares"] = (my_df.iloc[:, 2:27]**2).sum(axis=1) - my_df["euclidean_distance"]**2
    return my_df

def get_coefficients(my_df):
    '''Based on the equation above, once we have combined the like terms, we 
    get x1^2 - 2x1PC1 + ... + x25^2 - 2x25PC25 + sum_of_squares. We will then 
    return the coefficients.'''
    my_df = my_df.copy()
    for i in range(1, 26):
        my_df[f"coef_{i}"] = -2 * my_df[f"PC{i}"]
    return my_df

def get_matrix(my_df):
    my_df = my_df.copy()
    cols = ["sum_of_squares"] + [f"coef_{i}" for i in range(1, 26)]
    return my_df[cols].to_numpy()

def perform_row_reduction(my_matrix): 
    '''We chose 26 rows, because we can perform the row operation -R1 * R{i} for 
    i in (2, 26) and cancel out all of the exponential unknowns x1^2, ... x25*2. 
    We are left with a solvable linear algebra matrix. 
    '''
    for row in range(1, 26):  
        my_matrix[row, :] -= my_matrix[0, :]
    coef_matrix = my_matrix[1:26, 1:26]
    b = -1 * my_matrix[1:26, 0]
    return coef_matrix, b 