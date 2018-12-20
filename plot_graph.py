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
import config
from itertools import product
from xlutils.copy import copy as xl_copy

def get_avg_sop(size, t_init):
    SOP_avg = 0
    try:
        data = xlrd.open_workbook(config.root + "/fuzzy/R%02d/R%02dT%02ddata.xls" % (size, size, t_init))
    except:
        return

    SOP_case = []
    for sheet in data.sheets():
        SOP_case.append(len(sheet.col_values(3, start_rowx=1)))

    SOP_avg = np.sum(SOP_case) / len(SOP_case)
    return SOP_avg

def main():
    if __name__ == "__main__":
        sop = []
        for r in config.size:
            SOP_avgs = []
            for t in config.t_init:
                value = get_avg_sop(r, t)
                if value:
                    SOP_avgs.append(value)
            sop.append(np.sum(SOP_avgs) / len(SOP_avgs))
        print(sop)

        ''' SOP by size '''
        plt.plot(list(range(10, len(sop) * 5 + 1, 5)), sop[0], label='Fuzzy', color="red")
        plt.xlabel('R')
        plt.ylabel('Round')
        plt.title("SOP avg")
        plt.legend(loc=0)
        #plt.show()
        plt.savefig(config.root + "/SOP_avg", dpi=300)
        plt.clf()
main()

