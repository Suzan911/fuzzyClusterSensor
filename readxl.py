import xlrd
import xlwt
import matplotlib.pyplot as plt
import matplotlib.markers as mark
import numpy as np

def readExcelFile(file_id):
	try:
		data = xlrd.open_workbook("T"+ str(file_id) + ".xls")
	except:
		print("Not found!")
		return 0

	table = data.sheets()
	total_T_avg = 0
	T_avg = 0
	# Loop thought sheet
	for sheet in table:
		T_values = list(map(float, sheet.col_values(3)[1:]))
		total_T_avg += sum(T_values)
		T_avg = total_T_avg / len(T_values)
	return file_id, T_avg

index = []
ls = []
for i in range(10, 36, 5):
	idx, t_value = readExcelFile(i)
	index.append(idx)
	ls.append(t_value)

plt.plot(index, ls)
plt.xlabel('T init')
plt.ylabel('T Values')
plt.title("T Average for each T initial")
plt.show()
plt.savefig('sample_case_proc/T_avg_graph', dpi=300)
plt.clf()
