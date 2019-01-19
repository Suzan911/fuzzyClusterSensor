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
testcase = range(1, 21)
t_init = range(10, 91, 40)
size = range(10, 81, 5)
density = 0.0125
standy_loop = 1
is_fuzzy = True # True if want to simulate fuzzy, False if want to simulate fixed T value
root = "D0125fuzzy"
pool = 4
width = 100
height = 100