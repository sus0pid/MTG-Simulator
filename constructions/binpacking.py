import pandas as pd
import numpy as np
from gurobipy import *
from time import time
import pprint
import random


def lb(c, w):
    return int(math.ceil(sum(w) / c))

# df = pd.DataFrame(bpp_data_set, columns=['instance_name', 'c', 'w'])
# df['n'] = df['w'].apply(len)
# df['wmin'] = df['w'].apply(min)
# df['wmax'] = df['w'].apply(max)
# df['lb'] = df.apply(lambda x: lb(x['c'], x['w']), axis=1)
# print(df)

def model_bpp(c, w, UB=None, bin_for_item=None, LogToConsole=True, TimeLimit=30):
    n = len(w)
    LB = lb(c, w)
    if UB == None:
        UB = n
    if LogToConsole:
        print('c =', c, '| n =', n, '| LB =', LB, '| UB =', UB)
    model = Model()
    model.params.LogToConsole = LogToConsole
    model.params.TimeLimit    = TimeLimit  # seconds
    x = model.addVars(n, UB, vtype=GRB.BINARY)
    y = model.addVars(UB, vtype=GRB.BINARY)
    model.setObjective(quicksum(y[j] for j in range(UB)), GRB.MINIMIZE)  # minimize the number of bins used
    model.addConstrs(quicksum(x[i,j] for j in range(UB)) == 1 for i in range(n))  # each item in exactly one bin
    model.addConstrs(quicksum(w[i] * x[i,j] for i in range(n)) <= c * y[j] for j in range(UB))
                                                                          # limit total weight in each bin; also, link $x_{ij}$ with $y_j$
    if bin_for_item != None:
        for i in range(n):
            x[i, bin_for_item[i]].start = 1
    model.optimize()
    bin_for_item = [-1 for i in range(n)]
    for i in range(n):
        for j in range(UB):
            if x[i,j].X > 0.5:
                bin_for_item[i] = j
    return model.ObjVal, model.ObjBound, bin_for_item


def heur_FFD(c, w): # first-fit-decreasing heuristic
    n = len(w)
    order = sorted([i for i in range(n)], key=lambda i: w[i], reverse=True) # sort by decreasing trust level
    bin_for_item = [-1 for i in range(n)]
    bin_space = []
    for i in order:
        for j in range(len(bin_space)): # pack in the first bin in which the item fits
            if w[i] <= bin_space[j]:
                bin_for_item[i] =  j
                bin_space[j]    -= w[i]
                break
        if bin_for_item[i] < 0: # if no bin can accomodate the item, open a new bin
            j = len(bin_space)
            bin_for_item[i] = j
            bin_space.append(c - w[i])
    n_bins = len(bin_space)
    return n_bins, bin_for_item


def heur_BFD(c, w): # best-fit-decreasing heuristic
    n = len(w)
    order = sorted([i for i in range(n)], key=lambda i: w[i], reverse=True) # sort by decreasing weights
    bin_for_item = [-1 for i in range(n)]
    bin_space = []
    for i in order:
        bin_left_space = [bin_space[j] - w[i] for j in range(len(bin_space))]
        if all(s < 0 for s in bin_left_space): # if no bin can accomodate the item, open a new bin
            j = len(bin_space)
            bin_for_item[i] = j
            bin_space.append(c - w[i])
        else: # pack in the bin with minimum left space
            j = bin_left_space.index(min(list(filter(lambda s: s>=0, bin_left_space))))
            bin_for_item[i] = j
            bin_space[j] -= w[i]
    n_bins = len(bin_space)
    return n_bins, bin_for_item


def heur_WFD(c, w): # worst-fit-decreasing heuristic
    n = len(w)
    order = sorted([i for i in range(n)], key=lambda i: w[i], reverse=True) # sort by decreasing weights
    bin_for_item = [-1 for i in range(n)]
    bin_space = []
    for i in order:
        bin_left_space = [bin_space[j] - w[i] for j in range(len(bin_space))]
        if all(s < 0 for s in bin_left_space): # if no bin can accomodate the item, open a new bin
            j = len(bin_space)
            bin_for_item[i] = j
            bin_space.append(c - w[i])
        else: # pack in the bin with maximum left space
            j = bin_left_space.index(max(list(filter(lambda s: s>=0, bin_left_space))))
            bin_for_item[i] = j
            bin_space[j] -= w[i]
    n_bins = len(bin_space)
    return n_bins, bin_for_item


def heur_FF(c, w): # first-fit heuristic
    n = len(w)
    order = [i for i in range(n)]
    random.shuffle(order) # pack the items according to an random order
    bin_for_item = [-1 for i in range(n)]
    bin_space = []
    for i in order:
        # print(f'......index = {i}......')
        for j in range(len(bin_space)): # pack in the first bin in which the item fits
            if w[i] <= bin_space[j]:
                bin_for_item[i] = j
                bin_space[j] -= w[i]
                break
        if bin_for_item[i] < 0: # if no bin can accomodate the item, open a new bin
            j = len(bin_space)
            bin_for_item[i] = j
            bin_space.append(c - w[i])
    n_bins = len(bin_space)
    return n_bins, bin_for_item


def heur_BF(c, w): # best-fit-decreasing heuristic
    n = len(w)
    # order = sorted([i for i in range(n)], key=lambda i: w[i], reverse=True) # sort by decreasing weights
    order = [i for i in range(n)]
    random.shuffle(order)
    bin_for_item = [-1 for i in range(n)]
    bin_space = []
    for i in order:
        bin_left_space = [bin_space[j] - w[i] for j in range(len(bin_space))]
        if all(s < 0 for s in bin_left_space): # if no bin can accomodate the item, open a new bin
            j = len(bin_space)
            bin_for_item[i] = j
            bin_space.append(c - w[i])
        else: # pack in the bin with minimum left space
            j = bin_left_space.index(min(list(filter(lambda s: s>=0, bin_left_space))))
            bin_for_item[i] = j
            bin_space[j] -= w[i]
    n_bins = len(bin_space)
    return n_bins, bin_for_item


def heur_WF(c, w): # worst-fit-decreasing heuristic
    n = len(w)
    # order = sorted([i for i in range(n)], key=lambda i: w[i], reverse=True) # sort by decreasing weights
    order = [i for i in range(n)]
    random.shuffle(order)
    bin_for_item = [-1 for i in range(n)]
    bin_space = []
    for i in order:
        bin_left_space = [bin_space[j] - w[i] for j in range(len(bin_space))]
        if all(s < 0 for s in bin_left_space): # if no bin can accomodate the item, open a new bin
            j = len(bin_space)
            bin_for_item[i] = j
            bin_space.append(c - w[i])
        else: # pack in the bin with minimum left space
            j = bin_left_space.index(max(list(filter(lambda s: s>=0, bin_left_space))))
            bin_for_item[i] = j
            bin_space[j] -= w[i]
    n_bins = len(bin_space)
    return n_bins, bin_for_item

# bpp_data = bpp_data_set[5]
# c, w = bpp_data['c'], bpp_data['w']
# n_bins, bin_for_item = heur_FFD(c, w)
# print("Heur found a solution with n_bins =", n_bins)
#
# n_bins, n_bins_lb, bin_for_item = model_bpp(c, w, LogToConsole=False, TimeLimit=5)
# print("Model found a solution with n_bins =", n_bins, "n_bins_lb =", n_bins_lb)

# for idx, bpp_data in enumerate(bpp_data_set):
#     c, w = bpp_data['c'], bpp_data['w']
#     n_bins, bin_for_item = heur_FFD(c, w)
#     print(idx, n_bins)
#
# for idx, bpp_data in enumerate(bpp_data_set):
#     c, w = bpp_data['c'], bpp_data['w']
#     n_bins, n_bins_lb, bin_for_item = model_bpp(c, w, LogToConsole=False, TimeLimit=5)
#     print(idx, n_bins, n_bins_lb)


# for idx, bpp_data in enumerate(bpp_data_set):
#     t_start = time()
#     c, w = bpp_data['c'], bpp_data['w']
#     n_bins, bin_for_item = heur_FFD(c, w)
#     n_bins, n_bins_lb, bin_for_item = model_bpp(c, w, n_bins, bin_for_item, LogToConsole=False, TimeLimit=10)
#     t_end = time()
#     print(idx, n_bins, n_bins_lb, t_end - t_start)

def test():
    sm_file = "oboselected_mixes_7.csv"
    mix_data = pd.read_csv(sm_file, usecols=['MixID', 'Bandwidth', 'Malicious'], skipinitialspace=True)
    ids = mix_data['MixID']
    bws = mix_data['Bandwidth']
    mal = mix_data['Malicious']
    mixes = list(zip(ids, bws, mal))
    # pprint.pprint(mixes)
    total_bw = 12496.745761681897 #1000 good nodes and 30 bad nodes
    c = total_bw * 0.255 #sum(bws)/total_bw/3 = 0.25357
    w = bws

    print('\n' + 10 * " > " + "Heuristic_FFD" + 10 * " > ")
    n_bins, bin_for_item = heur_FFD(c, w)
    print(n_bins, bin_for_item)
    layer_bw = [0, 0, 0]
    layer_mix = [[], [], []]
    bad_nodes = [0, 0, 0]
    bad_bws = [0, 0, 0]
    for idx, bin in enumerate(bin_for_item):
        layer_bw[bin] += bws[idx]
        layer_mix[bin].append(mixes[idx])
        if mixes[idx][2] == True:
            bad_nodes[bin] += 1
            bad_bws[bin] += mixes[idx][1]
    print(layer_bw)
    print([l/total_bw for l in layer_bw])
    print([len(lm) for lm in layer_mix])
    pprint.pprint(bad_nodes)
    pprint.pprint(bad_bws)
    print(f'attack benefit: {np.prod([bb / lb for (bb, lb) in list(zip(bad_bws, layer_bw))])}')
    # for idx, lm in enumerate(layer_mix):
    #     print(f'.........Layer {idx}.........')
    #     pprint.pprint(lm)


    print('\n' + 10 * " > " + "Heuristic_BFD" + 10 * " > ")
    n_bins, bin_for_item = heur_BFD(c, w)
    print(n_bins, bin_for_item)
    layer_bw = [0, 0, 0]
    layer_mix = [[], [], []]
    bad_nodes = [0, 0, 0]
    bad_bws = [0, 0, 0]
    for idx, bin in enumerate(bin_for_item):
        layer_bw[bin] += bws[idx]
        layer_mix[bin].append(mixes[idx])
        if mixes[idx][2] == True:
            bad_nodes[bin] += 1
            bad_bws[bin] += mixes[idx][1]
    print(layer_bw)
    print([l/total_bw for l in layer_bw])
    print([len(lm) for lm in layer_mix])
    pprint.pprint(bad_nodes)
    pprint.pprint(bad_bws)
    print(f'attack benefit: {np.prod([bb / lb for (bb, lb) in list(zip(bad_bws, layer_bw))])}')
    # for idx, lm in enumerate(layer_mix):
    #     print(f'.........Layer {idx}.........')
    #     pprint.pprint(lm)


    print('\n' + 10 * " > " + "Heuristic_WFD" + 10 * " > ")
    n_bins, bin_for_item = heur_WFD(c, w)
    print(n_bins, bin_for_item)
    layer_bw = [0, 0, 0]
    layer_mix = [[], [], []]
    bad_nodes = [0, 0, 0]
    bad_bws = [0, 0, 0]
    for idx, bin in enumerate(bin_for_item):
        layer_bw[bin] += bws[idx]
        layer_mix[bin].append(mixes[idx])
        if mixes[idx][2] == True:
            bad_nodes[bin] += 1
            bad_bws[bin] += mixes[idx][1]
    print(layer_bw)
    print([l/total_bw for l in layer_bw])
    print([len(lm) for lm in layer_mix])
    pprint.pprint(bad_nodes)
    pprint.pprint(bad_bws)
    print(f'attack benefit: {np.prod([bb / lb for (bb, lb) in list(zip(bad_bws, layer_bw))])}')
    # for idx, lm in enumerate(layer_mix):
    #     print(f'.........Layer {idx}.........')
    #     pprint.pprint(lm)



    print('\n' + 10 * " > " + "Heuristic_FF" + 10 * " > ")
    n_bins, bin_for_item = heur_FF(c, w)
    print(n_bins, bin_for_item)
    layer_bw = [0, 0, 0]
    layer_mix = [[], [], []]
    bad_nodes = [0, 0, 0]
    bad_bws = [0, 0, 0]
    for idx, bin in enumerate(bin_for_item):
        layer_bw[bin] += bws[idx]
        layer_mix[bin].append(mixes[idx])
        if mixes[idx][2] == True:
            bad_nodes[bin] += 1
            bad_bws[bin] += mixes[idx][1]
    print(layer_bw)
    print([l/total_bw for l in layer_bw])
    print([len(lm) for lm in layer_mix])
    pprint.pprint(bad_nodes)
    pprint.pprint(bad_bws)
    print(f'attack benefit: {np.prod([bb / lb for (bb, lb) in list(zip(bad_bws, layer_bw))])}')
    # for idx, lm in enumerate(layer_mix):
    #     print(f'.........Layer {idx}.........')
    #     pprint.pprint(lm)


    print('\n' + 10 * " > " + "Heuristic_BF" + 10 * " > ")
    n_bins, bin_for_item = heur_BF(c, w)
    print(n_bins, bin_for_item)
    layer_bw = [0, 0, 0]
    layer_mix = [[], [], []]
    bad_nodes = [0, 0, 0]
    bad_bws = [0, 0, 0]
    for idx, bin in enumerate(bin_for_item):
        layer_bw[bin] += bws[idx]
        layer_mix[bin].append(mixes[idx])
        if mixes[idx][2] == True:
            bad_nodes[bin] += 1
            bad_bws[bin] += mixes[idx][1]
    print(layer_bw)
    print([l/total_bw for l in layer_bw])
    print([len(lm) for lm in layer_mix])
    pprint.pprint(bad_nodes)
    pprint.pprint(bad_bws)
    print(f'attack benefit: {np.prod([bb / lb for (bb, lb) in list(zip(bad_bws, layer_bw))])}')
    # for idx, lm in enumerate(layer_mix):
    #     print(f'.........Layer {idx}.........')
    #     pprint.pprint(lm)


    print('\n' + 10 * " > " + "Heuristic_WF" + 10 * " > ")
    n_bins, bin_for_item = heur_WF(c, w)
    print(n_bins, bin_for_item)
    layer_bw = [0, 0, 0]
    layer_mix = [[], [], []]
    bad_nodes = [0, 0, 0]
    bad_bws = [0, 0, 0]
    for idx, bin in enumerate(bin_for_item):
        layer_bw[bin] += bws[idx]
        layer_mix[bin].append(mixes[idx])
        if mixes[idx][2] == True:
            bad_nodes[bin] += 1
            bad_bws[bin] += mixes[idx][1]
    print(layer_bw)
    print([l/total_bw for l in layer_bw])
    print([len(lm) for lm in layer_mix])
    pprint.pprint(bad_nodes)
    pprint.pprint(bad_bws)
    print(f'attack benefit: {np.prod([bb / lb for (bb, lb) in list(zip(bad_bws, layer_bw))])}')
    # for idx, lm in enumerate(layer_mix):
    #     print(f'.........Layer {idx}.........')
    #     pprint.pprint(lm)


    print('\n' + 10 * " > " + "ILP" + 10 * " > ")
    n_bins, n_bins_lb, bin_for_item = model_bpp(c, w, n_bins, LogToConsole=False)
    print(n_bins, n_bins_lb)
    layer_bw = [0, 0, 0]
    layer_mix = [[], [], []]
    bad_nodes = [0, 0, 0]
    bad_bws = [0, 0, 0]
    for idx, bin in enumerate(bin_for_item):
        layer_bw[bin] += bws[idx]
        layer_mix[bin].append(mixes[idx])
        if mixes[idx][2] == True:
            bad_nodes[bin] += 1
            bad_bws[bin] += mixes[idx][1]
    print(layer_bw)
    print([l / total_bw for l in layer_bw])
    print([len(lm) for lm in layer_mix])
    pprint.pprint(bad_nodes)
    pprint.pprint(bad_bws)
    # benefit = [bb/lb for (bb, lb) in list(zip(bad_bws, layer_bw))]
    print(f'attack benefit: {np.prod([bb / lb for (bb, lb) in list(zip(bad_bws, layer_bw))])}')
    # for idx, lm in enumerate(layer_mix):
    #     print(f'.........Layer {idx}.........')
    #     pprint.pprint(lm)


def test_fits(): # test the correctness of the algorithm
    # test best-fit
    w = [4, 8, 5, 1, 7, 6, 1, 4, 2, 2]
    c = 10

    print('\n' + 10 * " > " + "FF" + 10 * " > ")
    n_bins, bin_for_item = heur_FF(c, w)
    print(n_bins, bin_for_item)
    bin_cont = [[], [], [], [], [], []]
    for idx, bin in enumerate(bin_for_item):
        bin_cont[bin].append(w[idx])
    pprint.pprint(bin_cont)

    print('\n' + 10 * " > " + "BF" + 10 * " > ")
    n_bins, bin_for_item = heur_BF(c, w)
    print(n_bins, bin_for_item)
    bin_cont = [[], [], [], [], [], []]
    for idx, bin in enumerate(bin_for_item):
        bin_cont[bin].append(w[idx])
    pprint.pprint(bin_cont)

    print('\n' + 10 * " > " + "WF" + 10 * " > ")
    n_bins, bin_for_item = heur_WF(c, w)
    print(n_bins, bin_for_item)
    bin_cont = [[], [], [], [], [], []]
    for idx, bin in enumerate(bin_for_item):
        bin_cont[bin].append(w[idx])
    pprint.pprint(bin_cont)

    print('\n' + 10 * " > " + "FFD" + 10 * " > ")
    n_bins, bin_for_item = heur_FFD(c, w)
    print(n_bins, bin_for_item)
    bin_cont = [[], [], [], [], [], []]
    for idx, bin in enumerate(bin_for_item):
        bin_cont[bin].append(w[idx])
    pprint.pprint(bin_cont)

    print('\n' + 10 * " > " + "BFD" + 10 * " > ")
    n_bins, bin_for_item = heur_BFD(c, w)
    print(n_bins, bin_for_item)
    bin_cont = [[], [], [], [], [], []]
    for idx, bin in enumerate(bin_for_item):
        bin_cont[bin].append(w[idx])
    pprint.pprint(bin_cont)

    print('\n' + 10 * " > " + "WFD" + 10 * " > ")
    n_bins, bin_for_item = heur_WFD(c, w)
    print(n_bins, bin_for_item)
    bin_cont = [[], [], [], [], [], []]
    for idx, bin in enumerate(bin_for_item):
        bin_cont[bin].append(w[idx])
    pprint.pprint(bin_cont)
