"""
Plot graph to summarize the analyst
"""
import openpyxl as xl
import os
import time
import matplotlib.pyplot as plt
import matplotlib.markers as mark
import multiprocessing as mp
import numpy as np
import config
from itertools import product

def get_avg_sop(size, t_init):
    SOP_avg = 0
    try:
        data = xl.load_workbook(config.root + "/R%02d/R%02dT%02ddata.xlsx" % (size, size, t_init))
    except:
        return

    arr = np.fromiter(map(lambda sheet: sheet.max_row - 1, data.worksheets), dtype=np.float64)
    SOP_avg = np.mean(arr, dtype=np.float64)
    return SOP_avg

if __name__ == "__main__":
    sop = []
    for r in config.size:
        SOP_avgs = []
        for t in config.t_init:
            value = get_avg_sop(r, t)
            if value:
                SOP_avgs.append(value)
        sop.append(np.mean(SOP_avgs, dtype=np.float64))
    print(sop)

    ''' SOP by size '''
    plt.plot(list(range(10, ((len(sop) + 1) * 5) + 1, 5)), sop, label='Fuzzy', color="red")
    plt.xlabel('R')
    plt.ylabel('Round')
    plt.title("SOP avg")
    plt.legend(loc=0)
    #plt.show()
    plt.savefig(config.root + "/SOP_avg", dpi=300)
    plt.clf()
