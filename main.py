"""
For running algorithm phase
"""
import math
import os
import shutil
import xlwt
import xlrd
import time as time
import numpy as np
import multiprocessing as mp
import matplotlib.pyplot as plt
import matplotlib.markers as mark
import phase
import config
from readxl import readExcelFile
from itertools import product
from Field import Field
from Node import Node
#from xlutils.copy import copy as xl_copy

def check_access_file(tc, size, t_init):
    """
    Check that have been already generate testcase or not
    """
    if not os.path.exists(config.root + "/R%02d/T%02d/%04d" % (size, t_init, tc)):
        return False, (tc, size, t_init)
    else:
        if os.path.exists(config.root + "/R%02d/T%02d/%04d/data.xls" % (size, t_init, tc)):
            try:
                book = xlrd.open_workbook(config.root + "/R%02d/R%02dT%02ddata.xls" % (size, size, t_init))
                if ("%04d" % tc) in book.sheet_names():
                    return True, (tc, size, t_init)
                else:
                    return False, (tc, size, t_init)
            except:
                return False, (tc, size, t_init)
        else:
            shutil.rmtree(config.root + "/R%02d/T%02d/%04d" % (size, t_init, tc))
            return False, (tc, size, t_init)


# This is main
def running(tc, t_init, size, is_fuzzy=True):
    #----------------------
    # Initial value
    # Change these value if you want new property
    #----------------------
    t_init = t_init / 100
    density = config.density
    # size = 10
    #----------------------

    standy_loop = config.standy_loop
    field_radius = size
    t_init_for_file = int(t_init * 100)

    start_time = time.time()
    print("Processing in testcase {} which set initial radius at {}, density at {} and T value at {}.\nRunning on processer {}\n".format(tc, field_radius, density, t_init, mp.current_process()))

    # Check if file already generate
    if not os.path.exists(config.root + "/R%02d/T%02d/%04d" % (size, t_init_for_file, tc)):
        os.makedirs(config.root + "/R%02d/T%02d/%04d" % (size, t_init_for_file, tc))
    else:
        if os.path.exists(config.root + "/R%02d/T%02d/%04d/data.xls" % (size, t_init_for_file, tc)):
            while not readExcelFile(tc, t_init_for_file, size):
                time.sleep(1)
            time_used = time.time() - start_time
            print("Processing at testcase {} which set initial radius at {}, density at {} and T value at {}.\nfinished within time {}s.\nRunning on processer {}\n".format(tc, field_radius, density, t_init, time_used, mp.current_process()))
            return
        else:
            shutil.rmtree(config.root + "/R%02d/T%02d/%04d" % (size, t_init_for_file, tc))
            os.makedirs(config.root + "/R%02d/T%02d/%04d" % (size, t_init_for_file, tc))

    book = xlwt.Workbook(encoding="utf-8")
    sheet1 = book.add_sheet("%04d" % tc)
    sheet1.write(0, 0, "Round")
    sheet1.write(0, 1, "AverageAll_energy") 
    sheet1.write(0, 2, "Size")
    sheet1.write(0, 3, "T")
    sheet1.write(0, 4, "No Pointer node")

    field = Field(100, density, radius=field_radius, start_energy=3, t=t_init)
    left_node = [int(field.getDensity() * int(field.getSize())**2)]
    t_avg_per_round = []
    e_avg_per_round = []
    r_avg_per_round = []
    ignore_node = []
    while len(field.getNodes()) >= (field.getDensity() * field.getSize()**2):
        if phase.CCH_election_phase(field, t_init):
            # Running one setup phase
            phase.CH_competition_phase(field, field_radius)
            phase.cluster_announcement_phase(field, field_radius)
            phase.cluster_association_phase(field)
            phase.cluster_confirmation_phase(field, is_fuzzy=is_fuzzy, plot_graph=False)

            ignore_node = len(list(filter(lambda x: not x.hasPointerNode(), field.getNodes('CM'))))
            #field.printField(testcase=tc, showplot=0, rnd=field.getRound())
            
            # Data storage
            rnd = field.getRound()
            nodes = field.getNodes()
            CH_nodes = field.getNodes('CH')
            left_node.append(len(field.getNodes()))
            E_avg = (np.sum([n.getAverageAll_energy() for n in CH_nodes]) / len(CH_nodes)) if len(CH_nodes) else 0
            Size_avg = (np.sum([n.getSize() for n in CH_nodes]) / len(CH_nodes)) if len(CH_nodes) else 0
            T_avg = (np.sum([n.getT() for n in nodes]) / len(nodes)) if len(nodes) else 0

            e_avg_per_round.append(E_avg)
            r_avg_per_round.append(Size_avg)
            t_avg_per_round.append(T_avg)
            sheet1.write(rnd, 0, (len(left_node)-1))
            sheet1.write(rnd, 1, E_avg)
            sheet1.write(rnd, 2, Size_avg)
            sheet1.write(rnd, 3, T_avg)
            sheet1.write(rnd, 4, ignore_node)
            for _ in range(standy_loop):
                phase.standyPhase(field)
            field.nextRound()
            field.resetNode()
    
    # Save graph
    '''
    plt.plot(list(range(len(left_node))), left_node)
    plt.xlabel('Round')
    plt.ylabel('Node')
    plt.title("Node left per round")
    # plt.show()
    plt.savefig("sample_case_proc/T%04d/%04d" % (t_init, testcase), dpi=300)
    plt.clf()

    plt.plot(list(range(len(CCH_nodeCount))), CCH_nodeCount)
    plt.xlabel('Round')
    plt.ylabel('Amount of CCH Node')
    plt.title("CCH node per round")
    # plt.show()
    plt.savefig("sample_case_proc/T%04d/%04d" % (t_init, testcase), dpi=300)
    plt.clf()
    plt.plot(list(range(len(t_avg_per_round))), t_avg_per_round)
    '''
    t_avg_case = np.sum(t_avg_per_round) / len(t_avg_per_round)
    e_avg_case = np.sum(e_avg_per_round) / len(e_avg_per_round)
    r_avg_case = np.sum(r_avg_per_round) / len(r_avg_per_round)
    plt.plot(list(range(len(t_avg_per_round))), t_avg_per_round, linewidth=0.7, alpha=0.7)
    plt.plot([0, len(t_avg_per_round)], [t_avg_case, t_avg_case], color='red')
    plt.xlabel('Round')
    plt.ylabel('T')
    plt.title("T Average per round")
    # plt.show()
    plt.savefig(config.root + "/R%02d/T%02d/%04d/t_avg" % (size, t_init_for_file, tc), dpi=300)
    plt.clf()

    plt.plot(list(range(len(e_avg_per_round))), e_avg_per_round, linewidth=0.8, alpha=0.8, color='green')
    plt.plot([0, len(e_avg_per_round)], [3, 0], color='red', linewidth=0.8, alpha=0.4)
    plt.xlabel('Round')
    plt.ylabel('Energy')
    plt.title("Energy Average per round")
    # plt.show()
    plt.savefig(config.root + "/R%02d/T%02d/%04d/energy_avg" % (size, t_init_for_file, tc), dpi=300)
    plt.clf()

    plt.plot(list(range(len(r_avg_per_round))), r_avg_per_round, linewidth=0.7, alpha=0.7)
    plt.plot([0, len(r_avg_per_round)], [r_avg_case, r_avg_case], color='red')
    plt.xlabel('Round')
    plt.ylabel('Size Cluster')
    plt.title("Size Cluster Average per round")
    # plt.show()
    plt.savefig(config.root + "/R%02d/T%02d/%04d/size_avg" % (size, t_init_for_file, tc), dpi=300)
    plt.clf()   
    
    #del field
    time_used = time.time() - start_time
    sheet1.write(0, 5, "Time used: %f" % time_used)
    book.save(config.root + "/R%02d/T%02d/%04d/data.xls" % (size, t_init_for_file, tc))
    while not readExcelFile(tc, t_init_for_file, size):
        time.sleep(1)
    print("Processing at testcase {} which set initial radius at {}, density at {} and T value at {}.\nfinished within time {}s.\nRunning on processer {}\n".format(tc, field_radius, density, t_init, time_used, mp.current_process()))


def main():
    if __name__ == "__main__":
        """
        Initial Value
        """
        testcase = config.testcase
        t_initial = config.t_init
        size = config.size
        is_fuzzy = True # True if want to simulate fuzzy, False if want to simulate fixed T value

        """
        Check remaining testcase that not generate
        """
        validate_case = list(filter(lambda x: not x[0], [check_access_file(tc, s, t_value) for tc in testcase for t_value in t_initial for s in size]))
        chuck = sorted(list(map(lambda x, fuzzy=is_fuzzy: (*x[1], fuzzy), validate_case)))
        print("Currently there are", len(chuck), "testcase that not generate yet.\n")

        """
        Processing
        """
        total_time = time.time()
        pool = mp.Pool(config.pool)
        # Running thought T value for each 100 testcase
        pool.starmap(running, chuck) # product(testcase, t-initial, size)
        print("Finished simulate all testcase using {}s.".format(total_time - time.time()))

main()
