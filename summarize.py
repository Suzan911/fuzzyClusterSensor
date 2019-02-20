import os
import time
import openpyxl as xl
import multiprocessing as mp
import matplotlib.pyplot as plt
import numpy as np
import config
from itertools import product

def get_overall(density, size, t_init, root=config.root, is_fuzzy=True):
    path = root + ("%.5f" % density) + ("_fuzzy" if is_fuzzy else "_fixed")
    try:
        data = xl.load_workbook(path + "/R%02d/R%02dT%02ddata.xlsx" % (size, size, t_init))
    except Exception as e:
        print(e)
        return

    HR_case, SOP_case, Size_case,esp, ect = [], [], [], [], []
    for sheet in data.worksheets:
        SOP_case.append(sheet.max_row - 1)
        Size_case.append(np.mean(list(map(lambda cell: cell.value, sheet['C'][1:])), dtype=np.float64))
        HR_case.append(np.mean(list(map(lambda cell: cell.value, sheet['D'][1:])), dtype=np.float64))
        esp.append(sheet['I2'].value)
        ect.append(sheet['J2'].value)

    SOP_avg = np.mean(SOP_case, dtype=np.float64) if SOP_case else 0
    Size_avg = np.mean(Size_case, dtype=np.float64) if Size_case else 0
    HR_avg = np.mean(HR_case, dtype=np.float64) if HR_case else 0
    esps = np.mean(esp, dtype=np.float64) if esp else 0
    ects = np.mean(ect, dtype=np.float64) if ect else 0

    print(SOP_avg, Size_avg, HR_avg, path)
    return SOP_avg, Size_avg, HR_avg, esps, ects


def get_avg_sop(density, size, t_init, path=config.root, is_fuzzy=True):
    return get_overall(density, size, t_init, path, is_fuzzy)[0]


def get_avg_size(density, size, t_init, path=config.root, is_fuzzy=True):
    return get_overall(density, size, t_init, path, is_fuzzy)[1]


def get_avg_hr(density, size, t_init, path=config.root, is_fuzzy=True):
    return get_overall(density, size, t_init, path, is_fuzzy)[2]


def summarize():
    """ Make folder """
    if not os.path.exists("summary"):
        os.makedirs("summary")

    for density in config.density:
        if config.run_state == "Fuzzy" or config.run_state == "Both":
            """ Fuzzy """
            sop_fuzzy, size_fuzzy, hr_fuzzy, essfu,eppfu = [], [], [], [], []
            for r in config.size:
                SOP_avg, Size_avg, HR_avg, esfu,epfu = [], [], [], [], []
                for t in config.t_init:
                    value = get_overall(density, r, t, is_fuzzy=True)
                    if value:
                        SOP_avg.append(value[0])
                        Size_avg.append(value[1])
                        HR_avg.append(value[2])
                        esfu.append(value[3])
                        epfu.append(value[4])
                sop_fuzzy.append(np.mean(SOP_avg, dtype=np.float64))
                size_fuzzy.append(np.mean(Size_avg, dtype=np.float64))
                hr_fuzzy.append(np.mean(HR_avg, dtype=np.float64))
                essfu.append(np.mean(esfu, dtype=np.float64))
                eppfu.append(np.mean(epfu, dtype=np.float64))

            """ Old Fuzzy """
            """
            sop_old_fuzzy, size_old_fuzzy, hr_old_fuzzy, essfu_old,eppfu_old= [], [], [], [], []
            for r in config.size:
                SOP_avg, Size_avg, HR_avg, esfu,epfu = [], [], [], [], []
                for t in config.t_init:
                    value = get_overall(density, r, t, "D", is_fuzzy=True)
                    if value:
                        SOP_avg.append(value[0])
                        Size_avg.append(value[1])
                        HR_avg.append(value[2])
                        esfu.append(value[3])
                        epfu.append(value[4])
                sop_old_fuzzy.append(np.mean(SOP_avg, dtype=np.float64))
                size_old_fuzzy.append(np.mean(Size_avg, dtype=np.float64))
                hr_old_fuzzy.append(np.mean(HR_avg, dtype=np.float64))
                essfu_old.append(np.mean(esfu, dtype=np.float64))
                eppfu_old.append(np.mean(epfu, dtype=np.float64))
            """
        if config.run_state == "Fixed" or config.run_state == "Both":
            """ Fixed HR 1 """
            sop_1, size_1, hr_1, essfx, eppfx = [], [], [], [], []
            for r in config.size:
                SOP_avg, Size_avg, HR_avg, esfx,epfx = [], [], [], [], []
                for t in config.t_init:
                    value = get_overall(density, r, t, is_fuzzy=False)
                    if value:
                        SOP_avg.append(value[0])
                        Size_avg.append(value[1])
                        HR_avg.append(value[2])
                        esfx.append(value[3])
                        epfx.append(value[4])
                sop_1.append(np.mean(SOP_avg, dtype=np.float64))
                size_1.append(np.mean(Size_avg, dtype=np.float64))
                hr_1.append(np.mean(HR_avg, dtype=np.float64))
                essfx.append(np.mean(esfx, dtype=np.float64))
                eppfx.append(np.mean(epfx, dtype=np.float64))

            """ Fixed HR 5
            sop_5, size_5, hr_5 = [], [], []
            for r in config.size:
                SOP_avg, Size_avg, HR_avg = [], [], []
                for t in config.t_init:
                    value = get_overall(density, r, t, is_fuzzy=False)
                    if value:
                        SOP_avg.append(value[0])
                        Size_avg.append(value[1])
                        HR_avg.append(value[2])
                sop_5.append(np.mean(SOP_avg, dtype=np.float64))
                size_5.append(np.mean(Size_avg, dtype=np.float64))
                hr_5.append(np.mean(HR_avg, dtype=np.float64))
            """

        ''' SOP by HR fixed and Fuzzy '''
        if config.run_state == "Fuzzy" or config.run_state == "Both":
            plt.plot(config.size, sop_fuzzy, label='Fuzzy', color="red")
            #plt.plot(config.size, sop_old_fuzzy, label='Old Fuzzy', color="#FF9999")
        if config.run_state == "Fixed" or config.run_state == "Both":
            plt.plot(config.size, sop_1, label='HR%d' % config.standy_loop, color="blue")
        plt.xlabel('Size')
        plt.ylabel('Round')
        plt.title("SOP avg @Density %.5f" % density)
        plt.legend(loc=0)
        plt.savefig("summary/" + config.root + ("%.5f" % density) + "_SOP_avg.png", dpi=300)
        plt.clf()

        ''' Average size by HR fixed and Fuzzy '''
        if config.run_state == "Fuzzy" or config.run_state == "Both":
            plt.plot(config.size, size_fuzzy, label='Fuzzy', color="red")
            #plt.plot(config.size, size_old_fuzzy, label='Old Fuzzy', color="#FF9999")
        if config.run_state == "Fixed" or config.run_state == "Both":
            plt.plot(config.size, size_1, label='HR%d' % config.standy_loop, color="blue")
        plt.plot(config.size, config.size, color="black", linestyle="-.")
        plt.xlabel('Size')
        plt.ylabel('Round')
        plt.title("Size avg @Density %.5f" % density)
        plt.legend(loc=0)
        plt.savefig("summary/" + config.root + ("%.5f" % density) + "_Size_avg.png", dpi=300)
        plt.clf()

        ''' Average Hyper round by HR fixed and Fuzzy '''
        if config.run_state == "Fuzzy" or config.run_state == "Both":
            plt.plot(config.size, hr_fuzzy, label='Fuzzy', color="red")
            #plt.plot(config.size, hr_old_fuzzy, label='Old Fuzzy', color="#FF9999")
        if config.run_state == "Fixed" or config.run_state == "Both":
            plt.plot(config.size, hr_1, label='HR%d' % config.standy_loop, color="blue")
        plt.plot(config.size, config.size, color="black", linestyle="-.")
        plt.xlabel('Round')
        plt.ylabel('HR length')
        plt.title("HR length avg @Density %.5f" % density)
        plt.legend(loc=0)
        plt.savefig("summary/" + config.root + ("%.5f" % density) + "_HR_avg.png", dpi=300)
        plt.clf()

        ''' Energy Re-clustering avg fixed and Fuzzy '''
        if config.run_state == "Fuzzy" or config.run_state == "Both":
            plt.plot(config.size, eppfu, label='Fuzzy', color="red")
        if config.run_state == "Fixed" or config.run_state == "Both":
            plt.plot(config.size, eppfx, label='HR1', color="blue")
        plt.xlabel('Size')
        plt.ylabel('Energy per Round per node')
        plt.title("Energy Re-clustering avg @Density %.5f" % density)
        plt.legend(loc=0)
        plt.savefig("summary/" + config.root + ("%.5f" % density) + "_Energy_Re-clustering_avg.png", dpi=300)
        plt.clf()

        ''' Energy Standy Phase avg fixed and Fuzzy '''
        if config.run_state == "Fuzzy" or config.run_state == "Both":
            plt.plot(config.size, essfu, label='Fuzzy', color="red")
        if config.run_state == "Fixed" or config.run_state == "Both":
            plt.plot(config.size, essfx, label='HR1', color="blue")
        plt.xlabel('Size')
        plt.ylabel('Energy per Round per node')
        plt.title("Energy Standy Phase avg @Density %.5f" % density)
        plt.legend(loc=0)
        plt.savefig("summary/" + config.root + ("%.5f" % density) + "_Energy_Re-Standy_avg.png", dpi=300)
        plt.clf()


if __name__ == "__main__":
    summarize()
