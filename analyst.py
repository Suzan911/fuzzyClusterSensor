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

def analyst(size, t_init):
    T_avg = 0
    SOP_avg = 0
    Size_avg = 0
    start_time = time.time()
    try:
        data = xlrd.open_workbook("sample_case_proc/R%02d/R%02dT%02ddata.xls" % (size, size, t_init))
    except:
        return

    T_case = []
    SOP_case = []
    Size_case = []
    for sheet in data.sheets():
        T_values = sheet.col_values(3, start_rowx=1)
        Size_values = sheet.col_values(2, start_rowx=1)
        SOP_case.append(len(T_values))
        Size_case.append(np.sum(Size_values) / len(Size_values))
        T_case.append(np.sum(T_values) / len(T_values))

    T_avg = np.sum(T_case) / len(T_case)
    Size_avg = np.sum(Size_case) / len(Size_case)
    SOP_avg = np.sum(SOP_case) / len(SOP_case)
    '''
    # Loop thought sheet
    for sheet in table:
        left_node = sheet.col_values(0)
        E_avg = sheet.col_values(1)
        Size_avg = sheet.col_values(2)
        T_avg = sheet.col_values(3)#[1:]
        ignore_node = sheet.col_values(4)#[1:]
    '''

    '''T by size'''
    plt.plot([1, len(T_case) + 1], [T_avg, T_avg], label='T avg = %.4f' % T_avg)
    plt.scatter(list(range(1, len(T_case) + 1)), T_case, s=10, marker=mark.MarkerStyle('x', fillstyle='full'), color='red')
    plt.xlabel('Testcase')
    plt.ylabel('T')
    plt.title("T avg R=%02d T=%.2f" % (size, t_init / 100))
    plt.legend(loc=0)
    #plt.show()
    plt.savefig("sample_case_proc/R%02d/R%02dT%02d_T_avg" % (size, size, t_init), dpi=300)
    plt.clf()

    ''' Cluster Size avg by size '''
    plt.plot([1, len(Size_case) + 1], [Size_avg, Size_avg], label='Cluster Size avg = %.4f' % Size_avg)
    plt.scatter(list(range(1, len(Size_case) + 1)), Size_case, s=10, marker=mark.MarkerStyle('x', fillstyle='full'), color='red')
    plt.xlabel('Testcase')
    plt.ylabel('Cluster size')
    plt.title("Cluster size avg R=%02d T=%.2f" % (size, t_init / 100))
    plt.legend(loc=0)
    #plt.show()
    plt.savefig("sample_case_proc/R%02d/R%02dT%02d_Size_avg" % (size, size, t_init), dpi=300)
    plt.clf()

    ''' SOP by size '''
    plt.plot([1, len(SOP_case) + 1], [SOP_avg, SOP_avg], label='SOP avg = %.4f' % SOP_avg)
    plt.scatter(list(range(1, len(SOP_case) + 1)), SOP_case, s=10, marker=mark.MarkerStyle('x', fillstyle='full'), color='red')
    plt.xlabel('Testcase')
    plt.ylabel('Round')
    plt.title("SOP avg R=%02d T=%.2f" % (size, t_init / 100))
    plt.legend(loc=0)
    #plt.show()
    plt.savefig("sample_case_proc/R%02d/R%02dT%02d_SOP_avg" % (size, size, t_init), dpi=300)
    plt.clf()

    print(T_avg, SOP_avg, Size_avg)
    print("Processing analyst which set initial radius at {} and initial T valuse at {} finished within time {}s.\nRunning on processer {}\n".format(size, t_init, time.time() - start_time, mp.current_process()))
    del data

def main():
    if __name__ == "__main__":
        pool = mp.Pool(4)
        '''
        for size in range(40, 81, 5):
            for t_initial in range(10, 81, 5):
                for testcase in range(1, 101):
                    readExcelFile(size, t_initial, testcase)
        '''
        pool.starmap(analyst, product(range(10, 81, 5), range(10, 81, 5))) # size, t_init

main()

