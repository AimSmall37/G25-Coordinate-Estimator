import direct_linear_solver as dls 

my_distances = "example_distances.csv" # replace this file with your distances of choice
my_references = "example_references.csv" # replace this with your references of choice

print(dls.solve_coordinates("example_distances.csv", "example_references.csv"))