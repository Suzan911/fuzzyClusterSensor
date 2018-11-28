"""
Analyst to plot graph
"""
import xlrd
import xlwt
import os
import time
import matplotlib.pyplot as plt
import matplotlib.markers as mark
import multiprocessing as mp
import numpy as np
from itertools import product
from xlutils.copy import copy as xl_copy

def get_avg_sop(size, t_init):
    SOP_avg = 0
    try:
        data = xlrd.open_workbook("sample_case_proc/R%02d/R%02dT%02ddata.xls" % (size, size, t_init))
    except:
        return

    SOP_case = []
    for sheet in data.sheets():
        SOP_case.append(len(sheet.col_values(3, start_rowx=1)))

    SOP_avg = np.sum(SOP_case) / len(SOP_case)
    return SOP_avg

def main():
    if __name__ == "__main__":
        sop = [[], [], []]
        for r in range(45, 91, 5):
            for index, t in enumerate([10, 50, 90]):
                sop[index].append(get_avg_sop(r, t))

        ''' SOP by size '''
        plt.plot(list(range(45, 91, 5)), sop[0], label='Fixed T=0.1', color="red")
        plt.plot(list(range(45, 91, 5)), sop[1], label='Fixed T=0.5', color="green")
        plt.plot(list(range(45, 91, 5)), sop[2], label='Fixed T=0.9', color="blue")
        plt.xlabel('R')
        plt.ylabel('Round')
        plt.title("SOP fixed avg")
        plt.legend(loc=0)
        #plt.show()
        plt.savefig("sample_case_proc/SOP_fixed_avg", dpi=300)
        plt.clf()
main()

