"""
Config initial variable

Variables
	# Use in simulation
	testcase   (*int): Amount of testcase
	t_init     (*int): Set of T values
	size	   (*int): Set of size
	density   (float): Node density per area (node / m**2)
	standy_loop (int): Amount of standy phase
	
	# Use in processing and file storaged
	root        (str): Folder root path
	pool        (int): Processer pool
"""
testcase = range(1, 6)
t_init = [1000]
size = range(10, 81, 5)
density = [0.00625]
standy_loop = 1
run_state = "Both"

root = "NCE."
pool = 4
width = 100
height = 100
