
import xlrd
import xlwt
import os
import time
"""import matplotlib.pyplot as plt
import matplotlib.markers as mark"""
import multiprocessing as mp
import numpy as np
import config
from itertools import product
from xlutils.copy import copy as xl_copy

def readExcelFile(tc, t_init_for_file, size):
    #print("readExcelFile", tc, t_init_for_file, size)
    try:
        path = config.root + "/R%02d/T%02d/%04d/data.xls" % (size, t_init_for_file, tc)
        data = xlrd.open_workbook(path, formatting_info=True)
    except:
        print("Not found!")
        return 0

    start_time = time.time()
    try:
        book = xlrd.open_workbook(config.root + "/R%02d/R%02dT%02ddata.xls" % (size, size, t_init_for_file))
        if ("%04d" % tc) in book.sheet_names():
            #print("Skipped tc:{} R:{} T:{}\nRun on processer {}\n".format((tc, size, t_init_for_file / 100, mp.current_process())))
            return 0
        wb = xl_copy(book)
    except:
        book = xlwt.Workbook(encoding="utf-8")
        wb = book

    start_time = time.time()
    sheet1 = wb.add_sheet("%04d" % tc)
    sheet1.write(0, 0, "Round")
    sheet1.write(0, 1, "AverageAll_energy") 
    sheet1.write(0, 2, "Size")
    sheet1.write(0, 3, "T")
    sheet1.write(0, 4, "No Pointer node")
    table = data.sheets()

    # Loop thought sheet
    for sheet in table:
        left_node = sheet.col_values(0)
        E_avg = sheet.col_values(1)
        Size_avg = sheet.col_values(2)
        T_avg = sheet.col_values(3)#[1:]
        ignore_node = sheet.col_values(4)#[1:]

    for rnd in range(1, len(left_node)):
        sheet1.write(rnd, 0, left_node[rnd])
        sheet1.write(rnd, 1, E_avg[rnd])
        sheet1.write(rnd, 2, Size_avg[rnd])
        sheet1.write(rnd, 3, T_avg[rnd])
        sheet1.write(rnd, 4, ignore_node[rnd])
    path = config.root + "/R%02d/R%02dT%02ddata.xls" % (size, size, t_init_for_file)
    wb.save(path)
    del sheet1
    print("Processing at testcase {} which set initial radius at {} and T value at {}\nfinished within time {} s.\nRunning on processer {}\n".format(tc, size, t_init_for_file / 100, time.time() - start_time, mp.current_process()))

def validate_access_file(tc, t_init, size):
    try:
        path = config.root + "/R%02d/T%02d/%04d/data.xls" % (size, t_init_for_file, tc)
        data = xlrd.open_workbook(path, formatting_info=True)
    except:
        return 0
    return (tc, t_init, size)

def main():
    if __name__ == "__main__":
        """
        Initial Value
        """
        testcase = [0]#config.testcase
        t_initial = config.t_ini
        size = config.size

        """
        Check remaining testcase that not generate
        """
        # to-do

        """
        Running
        """
        pool = mp.Pool(8)
        # Running thought T value for each 100 testcase
        pool.starmap(readExcelFile, product(testcase, t_initial, size)) # product(testcase, t-initial, size)

main()
