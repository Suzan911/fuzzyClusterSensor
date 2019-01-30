"""
For running algorithm phase
"""
import os
import shutil
import openpyxl as xl
import time as time
import numpy as np
import math
import multiprocessing as mp
import matplotlib.pyplot as plt
import matplotlib.markers as mark
import phase
import config
from itertools import product
from Field import Field
from Node import Node
from readxl import readExcelFile

def check_access_file(tc, size, t_init):
    """
    Check that have been already generate testcase or not
    """
    if not os.path.exists(config.root + "/R%02d/T%02d/%04d" % (size, t_init, tc)):
        return False, (tc, size, t_init)
    else:
        if os.path.exists(config.root + "/R%02d/T%02d/%04d/data.xlsx" % (size, t_init, tc)):
            try:
                book = xl.load_workbook(config.root + "/R%02d/R%02dT%02ddata.xlsx" % (size, size, t_init))
                if ("%04d" % tc) in book.sheetnames:
                    return True, (tc, size, t_init)
                else:
                    return False, (tc, size, t_init)
            except:
                return False, (tc, size, t_init)
        else:
            shutil.rmtree(config.root + "/R%02d/T%02d/%04d" % (size, t_init, tc))
            return False, (tc, size, t_init)


def running(tc, size, t_init, is_fuzzy=True):
    #----------------------
    # Initial value
    # Change these value if you want new property
    #----------------------
    t_init = 100
    density = config.density
    # size = 10
    #----------------------
    standy_loop = config.standy_loop
    radius = size
    t_init_for_file = int(t_init * 100)
    field_radius = size

    start_time = time.time()
    print("Processing in testcase {} which set initial radius at {}, density at {} and T value at {}.\nRunning on processer {}\n".format(tc, field_radius, density, t_init, mp.current_process()))

    # Check if file already generate
    if not os.path.exists(config.root + "/R%02d/T%02d/%04d" % (size, t_init_for_file, tc)):
        os.makedirs(config.root + "/R%02d/T%02d/%04d" % (size, t_init_for_file, tc))
    else:
        if os.path.exists(config.root + "/R%02d/T%02d/%04d/data.xlsx" % (size, t_init_for_file, tc)):
            while not readExcelFile(tc, t_init_for_file, size):
                time.sleep(1)
            time_used = time.time() - start_time
            print("Processing at testcase {} which set initial radius at {}, density at {} and T value at {}.\nfinished within time {}s.\nRunning on processer {}\n".format(tc, field_radius, density, t_init, time_used, mp.current_process()))
            return
        else:
            try:
                shutil.rmtree(config.root + "/R%02d/T%02d/%04d" % (size, t_init_for_file, tc))
            except Exception as err:
                pass
            os.makedirs(config.root + "/R%02d/T%02d/%04d" % (size, t_init_for_file, tc))

    book = xl.Workbook()
    sheet = book.active
    sheet.title = "%04d" % tc
    sheet.cell(1, 1, "Round")
    sheet.cell(1, 2, "AVG_energy") 
    sheet.cell(1, 3, "Size")
    sheet.cell(1, 4, "T")
    sheet.cell(1, 5, "No Pointer node")

    field = Field(config.width, config.height, density, radius=field_radius, start_energy=3, t=t_init)
    left_node = [int(field.getDensity() * field.getWidth() * field.getHeight())]
    ignore_node = []
    alpha_radius = math.sqrt(2 * math.log(10)) * radius
    while len(field.getNodes()) >= int(field.getDensity() * field.getWidth() * field.getHeight()):
        nodeList = field.getNodes()
        initEnergy = field.getInitEnergy()
        #------------line2 T wait <- 1/Ej--------
        for node in nodeList:
            #plt.text(node.getX(), node.getY(), node.getEnergy(), fontsize=2, wrap=True)
            node.setType('CCH')
            node.setDelay(1/node.getEnergy()) # delay
            node.setState('active')
        CCH_nodeList = sorted(field.getNodes('CCH'), key=lambda x: x.getDelay(), reverse=False)
        aaa = 0
        #------------line3 while T wait --------
        while len(CCH_nodeList):
            node = CCH_nodeList.pop(0)
            if node.getState() != 'sleep':
                node.setType('CH')
                # Consume Energy for sended a packet
                node.consume_transmit(200, radius)
                for nearbyNode in field.getNearbyNodes(node, radius, 'CCH', debug=0):
                    # Consume Energy for received a packet
                    nearbyNode.consume_receive(200)
                    nearbyNode.setType('CM')
                    nearbyNode.setState('sleep')
                    CCH_nodeList.remove(nearbyNode)
                    if not nearbyNode.hasPointerNode(): #PointerNode CH
                        node.setPointerNode(nearbyNode)
                        nearbyNode.setPointerNode(node)
        CH_nodeList = field.getNodes('CH')
        #---------------CM join CH-------------------
        lsCHdisfromnode = []
        lsCHmaxE = []
        for node in CH_nodeList:
            lsCHdisfromnode += [node.getDistanceFromNode(field.getBaseStation())]
            lsCHmaxE += [node.getEnergy()]
            for member in node.getPointerNode():
                member.consume_transmit(200, member.getDistanceFromNode(node))
                node.consume_receive(200)
                node.append_packet_energy(member.getEnergy())
        # Find the size and average energy for each Cluster Header
            node.updateSize()
            node.computeAverageEnergy()
        for node in CH_nodeList:
            print(Fuzzy(node.getEnergy(), max(lsCHmaxE), node.getDistanceFromNode(field.getBaseStation()), min(lsCHdisfromnode), max(lsCHdisfromnode)))
        for node in nodeList:
            #plt.text(node.getX(), node.getY(), node.getEnergy(), fontsize=2, wrap=True)
            if node.getEnergy() <= 0:
                field.deleteNode(node)
                del node
        
        """
        #-----print Field---------
        for node in field.getNodes('CH'):
            for member in node.getPointerNode():
                plt.plot([node.getX(), member.getX()], [node.getY(), member.getY()], color='r', alpha=0.4, linewidth=0.5)
        ignore_node = len(list(filter(lambda x: not x.hasPointerNode(), field.getNodes('CM'))))
        field.printField(testcase=tc, showplot=0, rnd=field.getRound())
        """
        
        # Data storage
        rnd = field.getRound()
        nodes = field.getNodes()
        CH_nodes = field.getNodes('CH')
        left_node.append(len(field.getNodes()))
        E_avg = (np.sum([n.getAverageAll_energy() for n in CH_nodes]) / len(CH_nodes)) if len(CH_nodes) else 0
        Size_avg = (np.sum([n.getSize() for n in CH_nodes]) / len(CH_nodes)) if len(CH_nodes) else 0
        T_avg = (np.sum([n.getT() for n in nodes]) / len(nodes)) if len(nodes) else 0

        sheet.cell(rnd + 1, 1, (len(left_node)-1))
        sheet.cell(rnd + 1, 2, E_avg)
        sheet.cell(rnd + 1, 3, Size_avg)
        #sheet.cell(rnd + 1, 4, T_avg)
        #sheet.cell(rnd + 1, 5, ignore_node)
        for _ in range(standy_loop):
            phase.standyPhase(field)
        field.nextRound()
        field.resetNode()
        print(rnd, E_avg)

    e_avg_per_round = list(map(lambda cell: cell.value, sheet['B'][1:]))
    r_avg_per_round = list(map(lambda cell: cell.value, sheet['C'][1:]))
    t_avg_per_round = list(map(lambda cell: cell.value, sheet['D'][1:]))
    t_avg_case = np.mean(t_avg_per_round, dtype=np.float64)
    e_avg_case = np.mean(e_avg_per_round, dtype=np.float64)
    r_avg_case = np.mean(r_avg_per_round, dtype=np.float64)

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

    time_used = time.time() - start_time
    sheet.cell(1, 6, "Runtime (sec)")
    sheet.cell(2, 6, "%f" % time_used)

    try:
        book.save(config.root + "/R%02d/T%02d/%04d/data.xlsx" % (size, t_init_for_file, tc))
        book.close()
    except Exception as err:
        print(err)

    print(os.path.exists(config.root + "/R%02d/T%02d/%04d/data.xlsx" % (size, t_init_for_file, tc)))


    print("Processing at testcase {} which set initial radius at {}, density at {} and T value at {}.\nfinished within time {}s.\nRunning on processer {}\n".format(tc, field_radius, density, t_init, time_used, mp.current_process()))


if __name__ == "__main__":
    """
    Initial Value
    """
    testcase = config.testcase
    t_initial = config.t_init
    size = config.size
    is_fuzzy = config.is_fuzzy # True if want to simulate fuzzy, False if want to simulate fixed T value

    """
    Check remaining testcase that not generate
    """
    validate_case = list(filter(lambda x: not x[0], [check_access_file(tc, s, t_value) for tc in testcase for t_value in t_initial for s in size]))
    chuck = sorted(list(map(lambda x, fuzzy=is_fuzzy: (*x[1], fuzzy), validate_case)))
    print("Currently there are", len(chuck), "testcase that not generate yet.\n")

    """
    Processing
    """
    start_time = time.time()
    pool = mp.Pool(config.pool)
    # Running thought T value for each 100 testcase
    pool.starmap(running, chuck) # product(testcase, t-initial, size)
    print("Finished simulate all testcase using {}s.".format(time.time() - start_time))

    """
    Plot Graph
    To-do
    """
    #print("Starting plot graph...")



def Fuzzy(node_energy: float, avg_energy: float, d: float, dmin: float, dmax: float) -> float:
    """
    Fuzzy algorithms
    """
    energy = node_energy / avg_energy
    veryHigh = max(0, min(1,(energy-0.6)*2.5 if energy < 0.9 else 1)) if 0.1 <= energy <= 0.5 else 0
    high = max(0, min(1,(energy-0.4)*2.5 if energy < 0.7 else (0.9-energy)*2.5)) if 0.1 <= energy <= 0.5 else 0
    medium = max(0, min(1,(energy-0.2)*2.5 if energy < 0.5 else (0.7-energy)*2.5)) if 0.1 <= energy <= 0.5 else 0
    Low = max(0, min(1,energy*2.5 if energy < 0.3 else (0.5-energy)*2.5)) if 0.1 <= energy <= 0.5 else 0
    verylow = max(0, min(1,1 if energy <= 0.1 else (0.3-energy)*2.5)) if energy <= 0.3 else 0
    print(energy, veryHigh, medium, Low, verylow)

    RD = (d - dmin) / (dmax - dmin)
    far = max(0, min(1, 1 if RD >=0.05 else RD*0.22)) if RD >= 0.5 else 0
    adequate = max(0, min(1, (RD - 0.05)*0.22 if RD >=0.5 else RD*0.22)) if 0.05 <= RD <= 0.95 else 0
    close = max(0, min(1, (0.55 - RD)*0.22 if RD >=0.05 else 1)) if RD <= 0.5 else 0
    print(far, adequate, close)

    rules = [max(min(verylow, close, adequate, far),min(verylow, adequate), min(verylow, far)), max(min(Low, close),min(Low, adequate)), min(Low, far), min(medium, close),
    min(medium,adequate), min(medium, far), min(high,close), min(high,adequate),  max(min(high, far), min(veryHigh, far), min(veryHigh, close),  min(veryHigh,adequate))]
    
    start_mid_t, T_value, count = 0.03125, 0, -1#####
    for i in rules:
        weight = i * start_mid_t
        T_value += weight
        count = count + i if weight and count >= 0 else i if weight else count
        start_mid_t += 0.0625######
    return rules#T_value / count