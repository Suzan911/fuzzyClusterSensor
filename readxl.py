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


'''Sample Write

    book = xlwt.Workbook(encoding="utf-8")
    for tc in range(start_loop, final_loop + 1):
        sheet1 = book.add_sheet(str(tc))
        sheet1.write(0, 0, "Round")
        sheet1.write(0, 1, "AverageAll_energy") 
        sheet1.write(0, 2, "Size")
        sheet1.write(0, 3, "T")
        print('Testcase', tc)

        field = Field(100, 0.0125, radius=field_radius, start_energy=3, t=varT / 100)
        left_node = [int(field.getDensity() * int(field.getSize())**2)]
        CCH_nodeCount = [0]
        t_avg_per_round = []
        e_avg_per_round = []
        r_avg_per_round = []
        while len(field.getNodes()) > 124: #(field.getDensity() * field.getSize()**2):
            print('\nRound:', len(left_node))
            CCH_election_phase(field, varT)
            CCH_nodeCount.append(len(field.getNodes('CCH')))
            CH_competition_phase(field, field_radius)
            cluster_announcement_phase(field, field_radius)
            #field.printField(pic_id=tc, r=len(left_node), showplot=0)
            
            # Data storage
            nodes = field.getNodes()
            CH_nodes = field.getNodes('CH')
            left_node.append(len(field.getNodes()))

            E_avg = (sum([n.getAverageAll_energy() for n in CH_nodes]) / len(CH_nodes) if len(CH_nodes) else 0)
            Size_avg = (sum([n.getSize() for n in CH_nodes]) / len(CH_nodes) if len(CH_nodes) else 0)
            T_avg = (sum([n.getT() for n in nodes]) / len(nodes) if len(nodes) else 0)
            
            sheet1.write(len(left_node)-1, 0, (len(left_node)-1))
            sheet1.write(len(left_node)-1, 1, E_avg)
            sheet1.write(len(left_node)-1, 2, Size_avg)
            sheet1.write(len(left_node)-1, 3, T_avg)

            t_avg_per_round.append(T_avg)
            e_avg_per_round.append(E_avg)
            r_avg_per_round.append(Size_avg)

            for _ in range(standy_loop):
                standyPhase(field)
            field.resetNode()
        #print("-- First node died at round", len(left_node))
        print("-- End of simulation")
        book.save("T%s.xls"%varT)
        """
'''