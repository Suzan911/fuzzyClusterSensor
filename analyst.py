"""
Analyst to plot graph
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
from xlutils.copy import copy as xl_copy

def analyst(t_init, size):
    start_time = time.time()
    try:
        data = xl.load_workbook(config.root + "/R%02d/R%02dT%02ddata.xls" % (size, size, t_init))
    except Exception as err:
        print(err)
        return

    T_case = []
    SOP_case = []
    Size_case = []
    for sheet in data.worksheets:
        SOP_case.append(sheet.max_row - 1)
        Size_case.append(np.mean(sheet['C'][1:], dtype=np.float64))
        T_case.append(np.mean(sheet['D'][1:], dtype=np.float64))

    T_avg = np.mean(T_case, dtype=np.float64) if T_case else 0
    Size_avg = np.mean(Size_case, dtype=np.float64) if Size_case else 0
    SOP_avg = np.mean(SOP_case, dtype=np.float64) if SOP_case else 0

    '''T by size'''
    plt.plot([1, len(T_case) + 1], [T_avg, T_avg], label='T avg = %.4f' % T_avg)
    plt.scatter(list(range(1, len(T_case) + 1)), T_case, s=10, marker=mark.MarkerStyle('x', fillstyle='full'), color='red')
    plt.xlabel('Testcase')
    plt.ylabel('T')
    plt.title("T avg R=%02d T=%.2f" % (size, t_init / 100))
    plt.legend(loc=0)
    #plt.show()
    plt.savefig(config.root + "/R%02d/R%02dT%02d_T_avg" % (size, size, t_init), dpi=300)
    plt.clf()

    ''' Cluster Size avg by size '''
    plt.plot([1, len(Size_case) + 1], [Size_avg, Size_avg], label='Cluster Size avg = %.4f' % Size_avg)
    plt.scatter(list(range(1, len(Size_case) + 1)), Size_case, s=10, marker=mark.MarkerStyle('x', fillstyle='full'), color='red')
    plt.xlabel('Testcase')
    plt.ylabel('Cluster size')
    plt.title("Cluster size avg R=%02d T=%.2f" % (size, t_init / 100))
    plt.legend(loc=0)
    #plt.show()
    plt.savefig(config.root + "/R%02d/R%02dT%02d_Size_avg" % (size, size, t_init), dpi=300)
    plt.clf()

    ''' SOP by size '''
    plt.plot([1, len(SOP_case) + 1], [SOP_avg, SOP_avg], label='SOP avg = %.4f' % SOP_avg)
    plt.scatter(list(range(1, len(SOP_case) + 1)), SOP_case, s=10, marker=mark.MarkerStyle('x', fillstyle='full'), color='red')
    plt.xlabel('Testcase')
    plt.ylabel('Round')
    plt.title("SOP avg R=%02d T=%.2f" % (size, t_init / 100))
    plt.legend(loc=0)
    #plt.show()
    plt.savefig(config.root + "/R%02d/R%02dT%02d_SOP_avg" % (size, size, t_init), dpi=300)
    plt.clf()

    print("Processing analyst which set initial radius at {} and initial T valuse at {} finished within time {}s.\nRunning on processer {}\n".format(size, t_init, time.time() - start_time, mp.current_process()))
    del data


if __name__ == "__main__":
    """
    Initial Value
    """
    t_initial = config.t_init
    size = config.size

    """
    Check remaining testcase that not generate
    """
    # to-do

    """
    Running
    """
    pool = mp.Pool(config.pool)
    # Running thought T value for each 100 testcase
    pool.starmap(analyst, product(t_initial, size)) # product(testcase, t-initial, size)
