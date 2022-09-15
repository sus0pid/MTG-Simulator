# calculate waiting time of the message in different network config
# 2021.07.04

from gettext import find
from os import wait
from typing import overload
import pandas as pd
import csv
import os
import argparse
import glob
import shutil
import math


parser = argparse.ArgumentParser(description="Calculate queuing delay")

parser.add_argument("--l", type=int, help="message arriving rate")
parser.add_argument("--path", help="path of the topology files")


def cal_waittime_bw(topo_path, l):
    """
    (1) bandwidth-weighted expected waiting time
        T_i = n*(2-\Lambda/M)/(2(M-\Lambda))
        n: the number of mixes in layer i
        M: the total bandwidth of layer i
        \Lambda: poission rate parameter which is the mean of possion distribution
    """
    topology = parse_topology(topo_path)
    j = 1
    data = {
        "tot_wtime": [],
        "max_wtime": [],
        "l0_wtime": [],
        "l1_wtime": [],
        "l2_wtime": []
        # "l0_overload_rate": [],
        # "l1_overload_rate": [],
        # "l2_overload_rate": []
    }

    while 'epoch_'+str(j) in topology:
        # print("Computing for epoch"+str(j))
        layer0 = [x[0] for x in topology['epoch_'+str(j)]['0'].values()]
        layer0.sort()
        layer1 = [x[0] for x in topology['epoch_'+str(j)]['1'].values()]
        layer1.sort()
        layer2 = [x[0] for x in topology['epoch_'+str(j)]['2'].values()]
        layer2.sort()

        # calculate T_i for layer 0-2
        l0_t = formula_bw(layer0, l)
        l1_t = formula_bw(layer1, l)
        l2_t = formula_bw(layer2, l)
        data["tot_wtime"].append(sum([l0_t, l1_t, l2_t]))
        data["max_wtime"].append(max([l0_t, l1_t, l2_t]))
        data["l0_wtime"].append(l0_t)
        data["l1_wtime"].append(l1_t)
        data["l2_wtime"].append(l2_t)
        # data["l0_overload_rate"].append(check_overload_rate_bw(l, layer0))
        # data["l1_overload_rate"].append(check_overload_rate_bw(l, layer1))
        # data["l2_overload_rate"].append(check_overload_rate_bw(l, layer2))

        # print(f"Processing config {j}, the expected waiting time is l0:{l0_t}, l1:{l1_t}, l2:{l2_t}")

        j += 1

    return data

def cal_waittime_uniform(topo_path, l):
    """
    (2) uniform selection expected waiting time
    T_i = \sum_{j=1}^{n} n^{-1} * x_j * (2 - n^{-1}*x_j*\Lambda) / 2(1-n^{-1}*x_j*\Lambda)
    n: the number of mixes in layer i
    x_j: given b_j is jth-mix's bandwidth in layer i, x_j = 1/b_j
    \Lambda: Possion rate parameter 
    """

    # read network config settings from logs/xxxx/xxxx.csv
    # transform layer index into dict topology
    topology = parse_topology(topo_path)
    j = 1
    data = {
        "tot_wtime": [],
        "max_wtime": [],
        "l0_wtime": [],
        "l1_wtime": [],
        "l2_wtime": []
        # "l0_overload_rate": [],
        # "l1_overload_rate": [],
        # "l2_overload_rate": []
    }

    while 'epoch_'+str(j) in topology:
        # print("Computing for epoch"+str(j))
        layer0 = [x[0] for x in topology['epoch_'+str(j)]['0'].values()]
        layer0.sort()
        layer1 = [x[0] for x in topology['epoch_'+str(j)]['1'].values()]
        layer1.sort()
        layer2 = [x[0] for x in topology['epoch_'+str(j)]['2'].values()]
        layer2.sort()

        # calculate T_i for layer 0-2
        l0_t = formula_uniform(layer0, l)
        l1_t = formula_uniform(layer1, l)
        l2_t = formula_uniform(layer2, l)
        data["tot_wtime"].append(sum([l0_t, l1_t, l2_t]))
        data["max_wtime"].append(max([l0_t, l1_t, l2_t]))
        data["l0_wtime"].append(l0_t)
        data["l1_wtime"].append(l1_t)
        data["l2_wtime"].append(l2_t)
        # data["l0_overload_rate"].append(check_overload_rate_uni(l, layer0))
        # data["l1_overload_rate"].append(check_overload_rate_uni(l, layer1))
        # data["l2_overload_rate"].append(check_overload_rate_uni(l, layer2))

        # print(f"Processing config {j}, the expected waiting time is l0:{l0_t}, l1:{l1_t}, l2:{l2_t}")
        j += 1
    return data


def cal_waittime_uniform_fixed(topo_path, l, epoch):
    """
    (2) uniform selection expected waiting time
    T_i = \sum_{j=1}^{n} n^{-1} * x_j * (2 - n^{-1}*x_j*\Lambda) / 2(1-n^{-1}*x_j*\Lambda)
    n: the number of mixes in layer i
    x_j: given b_j is jth-mix's bandwidth in layer i, x_j = 1/b_j
    \Lambda: Possion rate parameter 
    """
    # read network config settings from logs/xxxx/xxxx.csv
    # transform layer index into dict topology
    topology = parse_topology(topo_path)
    j = epoch
    data = {
        "tot_wtime": [],
        "max_wtime": [],
        "l0_wtime": [],
        "l1_wtime": [],
        "l2_wtime": []
    }

    while 'epoch_'+str(j) in topology:
        print("Computing for epoch"+str(j))
        layer0 = [x[0] for x in topology['epoch_'+str(j)]['0'].values()]
        layer0.sort()
        layer1 = [x[0] for x in topology['epoch_'+str(j)]['1'].values()]
        layer1.sort()
        layer2 = [x[0] for x in topology['epoch_'+str(j)]['2'].values()]
        layer2.sort()
        print(f"Processing config {j}, the number of nodes is l0:{len(layer0)}, l1:{len(layer1)}, l2:{len(layer2)}")

        # calculate T_i for layer 0-2
        print(">>>layer0")
        l0_t = formula_uniform(layer0, l)
        print(">>>layer1")
        l1_t = formula_uniform(layer1, l)
        print(">>>layer2")
        l2_t = formula_uniform(layer2, l)
        data["tot_wtime"].append(sum([l0_t, l1_t, l2_t]))
        data["max_wtime"].append(max([l0_t, l1_t, l2_t]))
        data["l0_wtime"].append(l0_t)
        data["l1_wtime"].append(l1_t)
        data["l2_wtime"].append(l2_t)

        print(f"Processing config {j}, the expected waiting time is l0:{l0_t}, l1:{l1_t}, l2:{l2_t}, wtime:{data['tot_wtime']}")
        break
    return data

def formula_bw(layer_bws, l=1000):
    # set \Lambda value
    L = l
    lay_num = len(layer_bws)
    lay_bw = sum(layer_bws)
    time = lay_num * (2-L/lay_bw) / (2*(lay_bw-L))
    return abs(time)


def check_overload_rate_uni(l, layer_bws_list):
    # count the number of overloaded nodes in each layer
    threshold = l / len(layer_bws_list) # Lambda/N
    overload_count = 0
    for bw in layer_bws_list:
        if bw < threshold:
            overload_count += 1
    overload_rate = overload_count/len(layer_bws_list)
    return overload_rate


def check_overload_rate_bw(l, layer_bws_list):
    threshold = l / sum(layer_bws_list)
    overload_count = 0
    for bw in layer_bws_list:
        if bw < threshold:
            overload_count += 1
    overload_rate = overload_count/len(layer_bws_list)
    return overload_rate


def formula_uniform(layer_bws, l=1000):
    """
    calculates expected waiting time T_i
    input: layer_bws--list of all bandwidths in one layer
    output: time T_i
    """
    # set \Lambda value, L = 1/6 (10messages/hour) ==> 1/6 minutes, send one message every 10mins
    L = l
    n = len(layer_bws)
    x = [1/b for b in layer_bws]
    expected_time_per_node = [1/n * x[j] * (2 - 1/n*x[j]*L) / (2*(1-1/n*x[j]*L)) for j in range(n)]
    abs_exp_time_per_node = [abs(t) for t in expected_time_per_node]

    return sum((abs_exp_time_per_node))
        

def parse_topology(topo_path):
    """
    parse file containing information
    mix_id,bandwidth,malicious,layer

    outputs a dict {'config0':{'layer':{'mix_id':[bandwidth, malicious]},
    'config1': {...}, ..., 'configN':{...}}}

    """
    topology = {'epoch_0': {'-2':{}, '-1':{}, '0':{}, '1':{}, '2':{}}}
    with open(topo_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'layer' in row:
                topology['epoch_0'][row['layer']][row['mix_id']] = [float(row['bandwidth']),\
                                                     row['malicious']]
            elif 'epoch_0' in row:
                #parse configs
                i = 0 # starting from epoch1 rather than epoch0
                while 'epoch_'+str(i) in row:
                    if 'epoch_'+str(i) not in topology:
                        topology['epoch_'+str(i)] = {'-2':{}, '-1':{}, '0':{}, '1':{}, '2':{}}
                    topology['epoch_'+str(i)][row['epoch_'+str(i)]][row['mix_id']] = [float(row['bandwidth']), row['malicious']]
                    i+=1
    return topology


def wtime_uni(args):
    for i, name in enumerate(glob.glob(os.path.join(args.topo_dir, '*{}*layout.csv'.format(args.batch_th)))):
        print(f'>>>Processing {name}')
        wtimes = cal_waittime_uniform(name, args.l)
        filename = name.split('/')[-1]
        length = len(wtimes["tot_wtime"])
        wtimes["label"] = ['-'.join([filename.split('_')[1], filename.split('_')[2], filename.split('_')[5]])] * length
        wtimes["lambda"] = [args.l]*length
        wtimes["batch_th"] = [args.batch_th] * length
        df = pd.DataFrame(wtimes)
        if i == 0:
            df.to_csv(os.path.join(args.topo_dir, "{}_{}_uni_waittime.csv".format(args.batch_th, args.l)), 
                                                                    mode="a", index=False, header=True)
        else:
            df.to_csv(os.path.join(args.topo_dir, "{}_{}_uni_waittime.csv".format(args.batch_th, args.l)), 
                                                                    mode="a", index=False, header=False)



def wtime_bw(args):
    for i, name in enumerate(glob.glob(os.path.join(args.topo_dir, '*{}*layout.csv'.format(args.batch_th)))):
        print(f'>>>Processing {name}')
        wtimes = cal_waittime_bw(name, args.l)
        filename = name.split('/')[-1]
        length = len(wtimes["tot_wtime"])
        wtimes["label"] = ['-'.join([filename.split('_')[1], filename.split('_')[2], filename.split('_')[5]])] * length
        wtimes["lambda"] = [args.l] * length
        wtimes["batch_th"] = [args.batch_th] * length
        df = pd.DataFrame(wtimes)
        if i == 0:
            df.to_csv(os.path.join(args.topo_dir, "{}_{}_bw_waittime.csv".format(args.batch_th, args.l)), 
                                                                    mode="a", index=False, header=True)
        else:
            df.to_csv(os.path.join(args.topo_dir, "{}_{}_bw_waittime.csv".format(args.batch_th, args.l)), 
                                                                    mode="a", index=False, header=False)


def merge_uni_csv(batch_th, topo_dir):
    header = ['tot_wtime', 'max_wtime', 'l0_wtime', 'l1_wtime', 'l2_wtime',  
                'label', 'lambda', 'batch_th']
    #import csv files from folder
    allFiles = glob.glob(os.path.join(topo_dir, '{}*uni_waittime.csv'.format(batch_th)))

    # if not os.path.exists(os.path.join(topo_dir, "{}_bw_waittime.csv".format(lam))):
    with open (os.path.join(topo_dir, "{}_unit.csv".format(batch_th)), 'wb') as outfile:
        for i, fname in enumerate(allFiles):
            with open(fname, 'rb') as infile:
                if i != 0:
                    infile.readline() # Throw away header--but in this case there is no header in other files
                # block copy rest of file from input to output without parsing
                shutil.copyfileobj(infile, outfile)
                print(f">>>{fname} has been imported")


def merge_bw_csv(batch_th, topo_dir):
    header = ['tot_wtime', 'max_wtime', 'l0_wtime', 'l1_wtime', 'l2_wtime',  
                'label', 'lambda', 'batch_th']
    #import csv files from folder
    allFiles = glob.glob(os.path.join(topo_dir, '{}*bw_waittime.csv'.format(batch_th)))
    print(allFiles)

    # # if not os.path.exists(os.path.join(topo_dir, "{}_bw_waittime.csv".format(lam))):
    with open (os.path.join(topo_dir, "{}_bwt.csv".format(batch_th)), 'wb') as outfile:
        for i, fname in enumerate(allFiles):
            with open(fname, 'rb') as infile:
                if i != 0:
                    infile.readline() # Throw away header--but in this case there is no header in other files
                # block copy rest of file from input to output without parsing
                shutil.copyfileobj(infile, outfile)
                print(f">>>{fname} has been imported")


def merge_all_csv(batch_th, topo_dir):
    allFiles = glob.glob(os.path.join(topo_dir, '*{}_bwt.csv'.format(batch_th)))
    with open (os.path.join(topo_dir, "{}_bwt.csv".format(batch_th)), 'wb') as outfile:
        for i, fname in enumerate(allFiles):
            with open(fname, 'rb') as infile:
                if i != 0:
                    infile.readline() # Throw away header--but in this case there is no header in other files
                # block copy rest of file from input to output without parsing
                shutil.copyfileobj(infile, outfile)
                print(f">>>{fname} has been imported")

    allFiles = glob.glob(os.path.join(topo_dir, '*{}_unit.csv'.format(batch_th)))
    with open (os.path.join(topo_dir, "{}_unit.csv".format(batch_th)), 'wb') as outfile:
        for i, fname in enumerate(allFiles):
            with open(fname, 'rb') as infile:
                if i != 0:
                    infile.readline() # Throw away header--but in this case there is no header in other files
                # block copy rest of file from input to output without parsing
                shutil.copyfileobj(infile, outfile)
                print(f">>>{fname} has been imported")    

def main():
    args = parser.parse_args()
    if args.select_type == "bw":
        wtime_bw(args)
    elif args.select_type == "uniform":
        wtime_uni(args)
    elif args.select_type == "merge":
        merge_bw_csv(args.batch_th, args.topo_dir)
        merge_uni_csv(args.batch_th, args.topo_dir)
    elif args.select_type == "merge_all":
        merge_all_csv(args.batch_th, args.topo_dir)


def find_bug():
    path = "../integration_test/bowtie_dynamic/"
    file = "naive_hybrid_hybrid_28_lp_layout.csv"
    topo_path = os.path.join(path, file)
    wtimes =cal_waittime_uniform_fixed(topo_path, 800, 1)


if __name__ == "__main__":
    args = parser.parse_args()
    wtimes = cal_waittime_bw(args.path, args.l)
    print(f'The expected queuing delay of this topology is {sum(wtimes["tot_wtime"])/len(wtimes["tot_wtime"])}')
    print(wtimes["tot_wtime"])
