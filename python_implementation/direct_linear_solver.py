import helpers as hp
import numpy as np 

# Main function 
def solve_coordinates(distance_sheet: str, reference_sheet: str) -> tuple: 
    """ This function directly solves for an unknown set of G25 coordinates, given 
    there are at least 26 distances provided to other coordinates. It utilizes 
    the Euclidean formula to expand each distance into a quadratic function 
    based on the 25 principal components. By combining like terms and performing 
    row reduction on a single row, we get a solvable linear algebra matrix, 
    with no higher order terms. 

    Parameters:
        distance_sheet (str): A list of at least 26 given genetic distances. The 
        left column should contain the euclidean distance value (float), and the 
        right column should contain the population name. Should be a .csv or .txt file. 

        reference_sheet (str): A list of the G25 coordinates for all sources. Should be a .csv or .txt file. 
    """
    my_df = hp.subset_populations(distance_sheet, reference_sheet)
    my_matrix = hp.get_matrix(hp.get_coefficients(hp.get_constants(my_df)))
    coef_matrix, b = hp.perform_row_reduction(my_matrix)
    solution = tuple(np.linalg.solve(coef_matrix, b))
    return(solution)