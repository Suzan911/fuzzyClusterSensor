import xlrd
import xlwt
import os
import time
"""import matplotlib.pyplot as plt
import matplotlib.markers as mark"""
import multiprocessing as mp
import numpy as np
from itertools import product
from xlutils.copy import copy as xl_copy

def readExcelFile(tc, t_init_for_file, size):
    try:
        data = xlrd.open_workbook("sample_case_proc/R%02d/T%02d/%04d/data.xls" % (size, t_init_for_file, tc), formatting_info=True)
    except:
        print("Not found!")
        return 0

    start_time = time.time()
    book = xlrd.open_workbook("sample_case_proc/R%02d/R%02dT%02ddata.xls" % (size, size, t_init_for_file))
    if ("%04d" % tc) in book.sheet_names():
        #print("Skipped tc:{} R:{} T:{}\nRun on processer {}\n".format((tc, size, t_init_for_file / 100, mp.current_process())))
        return 0

    wb = xl_copy(book)
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
    path = "sample_case_proc/R%02d/R%02dT%02ddata.xls" % (size, size, t_init_for_file)
    wb.save(path)
    print("Processing at testcase {} which set initial radius at {} and T value at {}\nfinished within time {} s.\nRunning on processer {}\n".format(tc, size, t_init_for_file / 100, time.time() - start_time, mp.current_process()))
    #return file_id, T_avg

def main():
    if __name__ == "__main__":
        pool = mp.Pool(4)
        '''
        for size in range(40, 81, 5):
            for t_initial in range(10, 81, 5):
                for testcase in range(1, 101):
                    readExcelFile(size, t_initial, testcase)
        '''
        pool.starmap(readExcelFile, product(range(1, 101), range(10, 81, 5), range(10, 41, 5)))

main()

