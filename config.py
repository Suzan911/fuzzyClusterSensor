"""
Config initial variable

Variables
    # Use in simulation
    testcase   (*int): Amount of testcase
    t_init     (*int): Set of T values
    size       (*int): Set of size
    density  (*float): Node density per area (node/m**2)
    standy_loop (int): Amount of standy phase
    width       (int): Width of field
    height      (int): Height of field
    run_state   (str): Running state ("Fuzzy", "Fixed", "Both") Beware! Case-sensitive
    
    # Use in processing and file storaged
    root        (str): Folder root path
    pool        (int): Processer pool
"""
testcase = range(1, 101)
t_init = [10, 50, 90]
size = range(10, 81, 5)
density = [0.00625, 0.0125, 0.025, 0.05, 0.1]
standy_loop = 1
width = 100
height = 100
run_state = "Both"

root = "D"
pool = 2
