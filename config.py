"""
Config initial variable

Variables
	# Use in simulation
	testcase   (*int): Amount of testcase
	t_init     (*int): Set of T values
	size	   (*int): Set of size
	density   (float): Node density per area (node/m**2)
	standy_loop (int): Amount of standy phase
	
	# Use in processing and file storaged
	root        (str): Folder root path
	pool        (int): Processer pool
"""
testcase = range(1, 21)
t_init = [10, 50, 90]
size = range(10, 81, 5)
density = 0.025
standy_loop = 1
root = "testcase"
pool = 4