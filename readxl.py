<<<<<<< HEAD
import xlrd
import xlwt
import os
"""import matplotlib.pyplot as plt
import matplotlib.markers as mark"""
import numpy as np

def readExcelFile(size, t_init_for_file, tc):
    try:
        data = xlrd.open_workbook("sample_case_proc/R%02d/T%02d/%04d/data.xls" % (size, t_init_for_file, tc))
    except:
        print("Not found!")
        return 0

    sheet1 = book.add_sheet("%04d" % tc)
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
    book.save("R%02dT%02ddata.xls" % (size, t_init_for_file))
    #return file_id, T_avg



book = xlwt.Workbook(encoding="utf-8") #range(1, 101), range(10, 81, 5), range(40, 81, 5))) # product(testcase, t-initial, size)
for size in range(40, 81, 5):
    for t_initial in range(10, 81, 5):
        for testcase in range(1, 101):
            readExcelFile(size, t_initial, testcase)
=======
import xlrd
import xlwt
import os
"""import matplotlib.pyplot as plt
import matplotlib.markers as mark"""
import numpy as np

def readExcelFile(size, t_init_for_file, tc):
    try:
        data = xlrd.open_workbook("sample_case_proc/R%02d/T%02d/%04d/data.xls" % (size, t_init_for_file, tc))
    except:
        print("Not found!")
        return 0

    sheet1 = book.add_sheet("%04d" % tc)
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
    book.save("R%02dT%02ddata.xls" % (size, t_init_for_file))
    #return file_id, T_avg



book = xlwt.Workbook(encoding="utf-8") #range(1, 101), range(10, 81, 5), range(40, 81, 5))) # product(testcase, t-initial, size)
for size in range(40, 81, 5):
    for t_initial in range(10, 81, 5):
        for testcase in range(1, 101):
            readExcelFile(size, t_initial, testcase)
"""

>>>>>>> 75021c2ce08902ae5ac438582c08e7efcf8f5515
