import os
import time
import openpyxl as xl
import multiprocessing as mp
import matplotlib as plt
import numpy as np
import config
from itertools import product

def get_overall(size, t_init, is_fuzzy=True):
    path = config.root + "_" + ("fuzzy" if is_fuzzy else "fixed")
    try:
        data = xl.load_workbook(path + "/R%02d/R%02dT%02ddata.xlsx" % (size, size, t_init))
    except Exception as e:
        print(e)
        return

    T_case, SOP_case, Size_case = [], [], []
    for sheet in data.worksheets:
        SOP_case.append(sheet.max_row - 1)
        Size_case.append(np.mean(list(map(lambda cell: cell.value, sheet['C'][1:])), dtype=np.float64))
        T_case.append(np.mean(list(map(lambda cell: cell.value, sheet['D'][1:])), dtype=np.float64))

    SOP_avg = np.mean(SOP_case, dtype=np.float64) if SOP_case else 0
    Size_avg = np.mean(Size_case, dtype=np.float64) if Size_case else 0
    T_avg = np.mean(T_case, dtype=np.float64) if T_case else 0

    return SOP_avg, Size_avg, T_avg


def get_avg_sop(size, t_init, is_fuzzy=True):
    return get_overall(size, t_init, is_fuzzy)[0]


def get_avg_size(size, t_init, is_fuzzy=True):
    return get_overall(size, t_init, is_fuzzy)[1]


def get_avg_t(size, t_init, is_fuzzy=True):
    return get_overall(size, t_init, is_fuzzy)[2]


if __name__ == "__main__":
    """ Fuzzy """
    sop_fuzzy, size_fuzzy, t_fuzzy = [], [], []
    for r in config.size:
        SOP_avg, Size_avg, T_avg = [], [], []
        for t in config.t_init:
            value = get_overall(r, t, True)
            if value:
                SOP_avg.append(value[0])
                Size_avg.append(value[1])
                T_avg.append(value[2])
        sop_fuzzy.append(np.mean(SOP_avg, dtype=np.float64))
        size_fuzzy.append(np.mean(Size_avg, dtype=np.float64))
        t_fuzzy.append(np.mean(T_avg, dtype=np.float64))
    
    """ T 0.1 """
    sop_1, size_1, t_1 = [], [], []
    for r in config.size:
        SOP_avg, Size_avg, T_avg = [], [], []
        value = get_overall(r, 10, False)
        if value:
            SOP_avg.append(value)
            Size_avg.append(value[1])
            T_avg.append(value[2])
        sop_1.append(np.mean(SOP_avg, dtype=np.float64))
        size_1.append(np.mean(Size_avg, dtype=np.float64))
        t_1.append(np.mean(T_avg, dtype=np.float64))

    """ T 0.5 """
    sop_5, size_5, t_5 = [], [], []
    for r in config.size:
        SOP_avg = []
        Size_avg = []
        T_avg = []
        value = get_overall(r, 50, False)
        if value:
            SOP_avg.append(value)
            Size_avg.append(value[1])
            T_avg.append(value[2])
        sop_5.append(np.mean(SOP_avg, dtype=np.float64))
        size_5.append(np.mean(Size_avg, dtype=np.float64))
        t_5.append(np.mean(T_avg, dtype=np.float64))

    """ T 0.9 """
    sop_9, size_9, t_9 = [], [], []
    for r in config.size:
        SOP_avg, Size_avg, T_avg = [], [], []
        value = get_overall(r, 90, False)
        if value:
            SOP_avg.append(value)
            Size_avg.append(value[1])
            T_avg.append(value[2])
        sop_9.append(np.mean(SOP_avg, dtype=np.float64))
        size_9.append(np.mean(Size_avg, dtype=np.float64))
        t_9.append(np.mean(T_avg, dtype=np.float64))

    ''' SOP by T fixed and Fuzzy '''
    plt.plot(config.size, sop_fuzzy, label='Fuzzy', color="red")
    plt.plot(config.size, sop_1, label='T0.1', color="blue")
    plt.plot(config.size, sop_5, label='T0.5', color="green")
    plt.plot(config.size, sop_9, label='T0.9', color="black")
    plt.xlabel('Size')
    plt.ylabel('Round')
    plt.title("SOP avg")
    plt.legend(loc=0)
    plt.savefig(config.root + "/SOP_avg", dpi=300)
    plt.clf()

    ''' Average size by T fixed and Fuzzy '''
    plt.plot(config.size, size_fuzzy, label='Fuzzy', color="red")
    plt.plot(config.size, size_1, label='T0.1', color="blue")
    plt.plot(config.size, size_5, label='T0.5', color="green")
    plt.plot(config.size, size_9, label='T0.9', color="black")
    plt.xlabel('Size')
    plt.ylabel('Round')
    plt.title("SOP avg")
    plt.legend(loc=0)
    plt.savefig(config.root + "/Size_avg", dpi=300)
    plt.clf()

    ''' Average T value by T fixed and Fuzzy '''
    plt.plot(config.size, t_fuzzy, label='Fuzzy', color="red")
    plt.plot(config.size, t_1, label='T0.1', color="blue")
    plt.plot(config.size, t_5, label='T0.5', color="green")
    plt.plot(config.size, t_9, label='T0.9', color="black")
    plt.xlabel('Size')
    plt.ylabel('T')
    plt.title("T avg")
    plt.legend(loc=0)
    plt.savefig(config.root + "/T_avg", dpi=300)
    plt.clf()

