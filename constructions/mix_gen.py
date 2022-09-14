import sys
sys.path.append("../classes")
from mix import Mix
import numpy as np
import os
import mixnet_gen as mng
import random
import math
import sumup


def gen_ben_mixes(num_benign, mal_bw_frac):
    """
    Generate benign mixes according to the bandwidth distribution of Tor.
    mal_bw_frac / ben_bw_frac = 20% / 80% by default
    The number of benign mixes: 1000 by default
    """
    print('>>>Generating benign mixes......')
    shape, scale = 0.6520738, 1 / 0.0676395
    benign_bw = list(np.random.gamma(shape, scale, num_benign))
    total_bw = sum(benign_bw) / (1 - mal_bw_frac)
    benign_mixes = [Mix(i, benign_bw[i]) for i in range(num_benign)]
    print(f'>>>Total bandwidth: {total_bw} MB/s')
    print(f'>>>Num of benign: {len(benign_bw)}')
    return benign_mixes, total_bw


def write_mixes(mix_list, filename):
    try:
        with open(filename, 'w') as f:
            header = 'MixID, Bandwidth, Malicious\n'
            f.write(header)
            for m in mix_list:
                f.write(str(m))
                f.write('\n')
    except IOError as e:
        print(e)
        print('Write mixes to file failed!')


def fetch_mixes(filename, mal_bw_frac):
    mix_list = []
    try:
        print('>>>Generating benign mixes......')
        with open(filename, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                vals = line.strip().split(',')
                mix = Mix(int(vals[0]), float(vals[1]), int(vals[3]),
                              vals[2].strip() == str(True))
                mix_list.append(mix)
            return mix_list
    except IOError as e:
        print(e)
        print('Fetch mixes failed!')


def gen_mixes(adv_type, mal_num, benign_mix_file, num_benign, mal_bw_frac):
    """
    Adversary could strategically generate mixes
    select = 'bw': reassign bw --- Tor
                1) greedy bw seperation: big node with high bw, less total count
                2) mimic historical selected nodes
    select = 'rand': reassign total count --- NYM/Random
    """

    print(f'>>>Generating malicious mixes......')

    benign_mixes = fetch_mixes(os.path.join(benign_mix_file,
                                            "{0}_benignmix.csv".format(num_benign)), mal_bw_frac)
    # read benign mixes data to mixnet
    total_bw = sumup.sum_mix_bw(benign_mixes) / (1-mal_bw_frac)

    if adv_type == 'naive':
        # naive malicious mix generation: 3-150 nodes with even distributed bandwidth
        mix_pool = naive_mix_gen(benign_mixes, mal_bw_frac, total_bw, mal_num)
    elif adv_type == 'quality':
        # quality malicious mix generation: (1) greedy, (2) range
        mix_pool = bwgreedy_mix_gen(
            benign_mixes, mal_bw_frac, total_bw)  # greedy method
        # mix_pool = bwrange_mix_gen(benign_mixes, mal_bw_frac, total_bw) # range method
    elif adv_type == 'quantity':
        # quantitative malicious mix generation: greedy method--generate as many nodes as he can
        # with same malicious bandwidth budget
        mix_pool = quantity_mix_gen(
            benign_mixes, mal_bw_frac, total_bw, mal_num)

    elif adv_type == 'smart':
        # smart adversary divide bandwidth budget into three parts, and use each portion to generate
        # big/middle/small nodes
        # mix_pool = smart_mix_gen(benign_mixes, mal_bw_frac, total_bw)
        #mix_pool = smart_mix_gen2(benign_mixes, mal_bw_frac, total_bw, mal_num)
        mix_pool = smart_ffd_mix_gen(
            benign_mixes, mal_bw_frac, total_bw)  # for randffd
    return mix_pool


def bwgreedy_mix_gen(benign_mixes, mal_bw_frac, total_bw):
    """
    Aim: get the most number of mixes selected
    Method1: generate mixes with highest bw so that most mixes will be selected during selection process
    """
    mix_pool = benign_mixes[:]
    mal_mix_hbw = max([m.bandwidth for m in benign_mixes])
    mal_mix_num = int(total_bw * mal_bw_frac // mal_mix_hbw)
    mal_mix_lbw = total_bw * mal_bw_frac % mal_mix_hbw
    if mal_mix_num > 0:
        for index in range(mal_mix_num):
            mix = Mix(index+len(benign_mixes),
                          mal_mix_hbw, mng.gen_sk(), True)
            mix_pool.append(mix)

    if mal_mix_lbw > 0:
        mix_pool.append(Mix(mal_mix_num+len(benign_mixes), mal_mix_lbw,
                                mng.gen_sk(), True))
    return mix_pool


def bwrange_mix_gen(benign_mixes, mal_bw_frac, total_bw):
    """
    Aim: get most number of mixes selected
    Method2: generate mixes with bw randomly distributed [lbw, hbw]
    Need to solve: how to set lbw and hbw: hbw = max(bws), lbw = 20
    -learn the distribution in mixnet first and then generate mixes according to the history
    figure shows that when bw >= 20, hitrate >= 0.8
    other important points: (0.9, 29), (0.8, 20), (0.7, 15), (0.6, 11.5), (0.5, 8.5)
    """
    mix_pool = benign_mixes[:]
    hbw = max([m.bandwidth for m in benign_mixes])
    lbw = 20  # hitrate >= 0.8 is guaranteed
    mal_bw = []

    while total_bw * mal_bw_frac - sum(mal_bw) > 29:
        mal_bw.append(random.uniform(lbw, hbw))
    if total_bw * mal_bw_frac >= sum(mal_bw):
        mal_bw.append(total_bw * mal_bw_frac - sum(mal_bw))
    else:
        new_bw = max(mal_bw) + total_bw * mal_bw_frac - sum(mal_bw)
        mal_bw.remove(max(mal_bw))
        mal_bw.append(new_bw)

    for index, bw in enumerate(mal_bw):
        mix_pool.append(
            Mix(index+len(benign_mixes), bw, mng.gen_sk(), True))
    return mix_pool


def naive_mix_gen(benign_mixes, mal_bw_frac, total_bw, mal_num):
    # each node has even bandwidth
    mix_pool = benign_mixes[:]
    mal_bw = [total_bw*mal_bw_frac/mal_num for i in range(mal_num)]
    for index, bw in enumerate(mal_bw):
        mix_pool.append(
            Mix(index+len(benign_mixes), bw, mng.gen_sk(), True))
    return mix_pool


def quantity_mix_gen(benign_mixes, mal_bw_frac, total_bw, mal_bw):
    """
    set the mix_bw limit to 1MBps, starting from 1 to 15
    for randrand/randbp/bwrand/hybrid, generate as much small nodes as possible
    """
    mix_pool = benign_mixes[:]
    mal_num = math.floor(total_bw*mal_bw_frac/mal_bw)
    mal_bws = [mal_bw for i in range(mal_num)]
    diff = total_bw*mal_bw_frac - sum(mal_bws)
    assert (diff > 0)
    mal_bws.append(diff)
    print(mal_bws)

    for index, bw in enumerate(mal_bws):
        mix_pool.append(
            Mix(index+len(benign_mixes), bw, mng.gen_sk(), True))
    return mix_pool


def smart_mix_gen(benign_mixes, mal_bw_frac, total_bw):
    """
    In each range, generate several mixes
    - 50-max
    - 14-45
    - 8-14
    """
    mix_pool = benign_mixes[:]
    hbws = [70, 25, 13]
    lbws = [50, 15, 1]
    mal_bw = []
    mbws = []
    for i in range(3):
        # print(f"i={i}")
        while 1/3*total_bw*mal_bw_frac - sum(mbws) >= 20:
            mbws.append(random.uniform(lbws[i], hbws[i]))
        mal_bw += mbws
        mbws = []
    diff = sum(mal_bw) - total_bw*mal_bw_frac
    if diff > 0:
        mal_bw[0] -= diff
    else:
        mal_bw[-1] -= diff
    # print(f"mal_bw: {mal_bw}")

    for index, bw in enumerate(mal_bw):
        mix_pool.append(
            Mix(index+len(benign_mixes), bw, mng.gen_sk(), True))
    return mix_pool


def smart_ffd_mix_gen(benign_mixes, mal_bw_frac, total_bw):
    """
    generate mix nodes such that adversary can gain highest compromised circuits
    big nodes: bw=50, number=20
    middle nodes: bw=15, number = 50
    small nodes: bw=1.5
    """
    mix_pool = benign_mixes[:]
    bws = [50, 15, 1.5]
    nums = [22, 56, 210]
    mal_bw = []
    for bw, num in zip(bws, nums):
        mal_bw.extend([bw for i in range(num)])
    diff = sum(mal_bw) - total_bw*mal_bw_frac
    if diff > 0:
        if diff < mal_bw[0]:
            mal_bw[0] -= diff
    else:
        mal_bw.extend([1 for i in range(int(-diff))])

    print(f'mal_bw: {mal_bw}')
    print(f'len: {len(mal_bw)}')

    for index, bw in enumerate(mal_bw):
        mix_pool.append(
            Mix(index+len(benign_mixes), bw, mng.gen_sk(), True))
    return mix_pool


def smart_mix_gen2(benign_mixes, mal_bw_frac, total_bw, nm):
    """
    generate big nodes and small nodes
    """
    mix_pool = benign_mixes[:]
    mal_bw = []
    max_bw = max([m.bandwidth for m in mix_pool])

    while 1/3*total_bw*mal_bw_frac - sum(mal_bw) >= 70:
        mal_bw.append(random.uniform(70, max_bw+10))
    mal_bw += [2/3*total_bw*mal_bw_frac/nm for i in range(nm)]

    diff = total_bw*mal_bw_frac - sum(mal_bw)
    if diff > 0:
        mal_bw.append(diff)
    else:
        mal_bw[0] += diff
    for mb in mal_bw:
        assert (mb > 0)

    print(f'mal_bw: {total_bw * mal_bw_frac}')
    print(f'sum(mal_bw): {sum(mal_bw)}')

    for index, bw in enumerate(mal_bw):
        mix_pool.append(
            Mix(index+len(benign_mixes), bw, mng.gen_sk(), True))
    return mix_pool


def disp_mixes(mix_list):
    for m in mix_list:
        print(m)


def sum_mix_stab(mix_list):
    stabs = [m.stab for m in mix_list]
    return sum(stabs)


def gen_new_mixes(new_num, pool_num, malicious, epoch_of_birth):

    shape, scale = 0.6520738, 1 / 0.0676395
    new_mixes_bw = list(np.random.gamma(shape, scale, new_num))
    new_mixes = [Mix(index+pool_num, bw, mng.gen_sk(), malicious, epoch_of_birth)
                 for index, bw in enumerate(new_mixes_bw)]
    return new_mixes
