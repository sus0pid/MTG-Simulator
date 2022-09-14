import sys
sys.path.append("../classes")
from numpy.lib import select
from mix import Mix
from mixnet import Mixnet
import sumup
import mix_gen as mg
import numpy as np
import ecvrf_edwards25519_sha512_elligator2 as vrf
import random
import pandas as pd
import os
import binpacking as bp
import pprint as pp

GUARD_LAYER = "layer1"

"""
Mixnet 
generation algorithm
- rand_rand #by rand, we use NYM
- rand_bp
- rand_layer

- bw_rand
- bw_bp
- bw_layer
"""

def mix_select(select_mode, mixnet, batch_threshold, setting):
    """
    select mixes from mix pool
    """
    mixnet.mix_select = []
    if setting == "static":
        select_pool, select_bw = get_batch_bw_static(mixnet, batch_threshold)
    elif setting == "dynamic":
        select_pool, select_bw = get_batch_bw_dynamic(mixnet, batch_threshold)
    if select_mode == 'bw':
        select_by_bw(mixnet, select_pool, select_bw)
    elif select_mode == 'rand':
        select_by_rand(mixnet, select_pool, select_bw)


    # """
    # 1. calculate new batch_thrreshold, calculate new mix_pool
    # 2. select mixes
    # """
    # new_batch_threshold = batch_threshold - sumup.sum_mix_bw(mixnet.mix_net['layer1'])
    # new_mix_pool = [m for m in mixnet.mix_pool if m not in mixnet.mix_net['layer1']]
    # if select_mode == 'bw':
    #     select_by_bw(mixnet, new_batch_threshold)
    # pass

def get_batch_bw_static(mixnet, batch_threshold):
    if mixnet.guard: # fixed case and not first epoch
    # all_mixes: available mixes to be selected from excluding fixed middle layer
    # batch_bw:  bandwidth threshold for selection excluding fixed middle layer
        try:
            all_mixes = [m for m in mixnet.mix_pool if m not in mixnet.mix_net[GUARD_LAYER]]
            batch_bw  = batch_threshold * mixnet.total_bw - sumup.sum_mix_bw(mixnet.mix_net[GUARD_LAYER])
        except TypeError as e:
            print('Error Occured: e')
            print('='*20)
            mixnet.disp_mixnet()
            mixnet.disp_mix_pool()
            print('='*20)
    else:
        all_mixes = mixnet.mix_pool[:]
        batch_bw  = batch_threshold * mixnet.total_bw
    return all_mixes, batch_bw

def get_batch_bw_dynamic(mixnet, batch_threshold):
    if mixnet.guard:
        select_pool = [m for m in mixnet.mix_pool if not m.GG and m.online]
        select_bw = 2 * sumup.sum_mix_bw(mixnet.mix_net[GUARD_LAYER])
    else:
        select_pool = [m for m in mixnet.mix_pool if m.online]
        select_bw = batch_threshold * sumup.sum_mix_bw(select_pool)
    return select_pool, select_bw


def select_by_bw(mixnet, all_mixes, batch_bw):
    """
    How many nodes should be selected? -- total bandwidth == threshold
    """
    print('--------bwSelection starts--------')
    # select one mix at a time until total mixes reach bandwidth batch threshold
    while True:
        weights      =  [m.bandwidth / sumup.sum_mix_bw(all_mixes) for m in all_mixes]
        sample_mix   =  np.random.choice(all_mixes, 1, replace=False, p=weights).tolist()
        mixnet.mix_select += sample_mix
        all_mixes    =  remove_mix(all_mixes, sample_mix)
        if sumup.sum_mix_bw(mixnet.mix_select) >= batch_bw:
            # mixnet.disp_mix_select(batch_threshold)
            print('--------bwSelection ends--------')
            break

def select_by_rand(mixnet, all_mixes, batch_bw):
    print('>>>randSelection starts...')
    # select one mix randomly at a time until total bandwidth reach batch threshold
    select_pool_bw = sumup.sum_mix_bw(all_mixes)
    while True:
        try:
            sample_mix = np.random.choice(all_mixes, 1, replace=False).tolist()
        except ValueError as e:
            print(e)
            print(f'sample_mix: {sample_mix}')
        mixnet.mix_select += sample_mix
        all_mixes    =  remove_mix(all_mixes, sample_mix)
        if sumup.sum_mix_bw(mixnet.mix_select) >= batch_bw:
            # mixnet.disp_mix_select(batch_threshold)
            print('>>>randSelection ends...')
            break
        if len(all_mixes) == 0:
            print('!!!Non-guard nodes are insufficient!')
            print(f'!!!bw of select pool: {select_pool_bw}')
            print(f'!!!bw of select goal: {batch_bw}')
            break


def hybrid_mixnet(mixnet, batch_threshold, e, select_mode, bp_method="lp"):
    # use bw to sample guard layer
    # use randomness to sample other layers
    assert(mixnet.guard == True)
    if e == 0:
        all_mixes, batch_bw = get_batch_bw_static(mixnet, batch_threshold)
        print("+"*10, "Guard Layer Sampling", "+"*10)
        print(f'guard: {mixnet.guard}, is_dirty: {mixnet.is_dirty}')
        mixnet.is_dirty = True
        mixnet.mix_net[GUARD_LAYER] = []
        # select guard layer if is_dirty == false
        while True:
            weights      =  [m.bandwidth / sumup.sum_mix_bw(all_mixes) for m in all_mixes]
            sample_mix   =  np.random.choice(all_mixes, 1, replace=False, p=weights).tolist()
            mixnet.mix_net[GUARD_LAYER] += sample_mix
            all_mixes    =  remove_mix(all_mixes, sample_mix)
            if sumup.sum_mix_bw(mixnet.mix_net[GUARD_LAYER]) >= batch_bw/3:
                # mixnet.disp_mix_select(batch_threshold)
                print('--------Guard Sampling ends--------')
                print(f'guard: {mixnet.guard}, is_dirty: {mixnet.is_dirty}')
                break
        # mixnet.disp_mixnet()

        if select_mode == "rand":
            # select other layers
            mixnet.mix_select   = [] 
            all_mixes, batch_bw = get_batch_bw_static(mixnet, batch_threshold)
            select_by_rand(mixnet, all_mixes, batch_bw)

            # place other layers
            mix_place("bp", mixnet, batch_threshold, bp_method)
        elif select_mode == "constraint":
            # select other layers
            mixnet.mix_select   = [] 
            all_mixes, batch_bw = get_batch_bw_static(mixnet, batch_threshold)
            new_mixes_pool = [m for m in all_mixes if m.bandwidth >= 1]
            select_by_rand(mixnet, new_mixes_pool, batch_bw)
            # place other layers
            mix_place("bp", mixnet, batch_threshold, bp_method)
    elif e > 0:
        mixnet.mix_net["layer_0"] = []
        mixnet.mix_net["layer_2"] = []
        if select_mode == "rand":
            # select other layers
            mixnet.mix_select   = [] 
            all_mixes, batch_bw = get_batch_bw_static(mixnet, batch_threshold)
            select_by_rand(mixnet, all_mixes, batch_bw)
            # place other layers
            mix_place("bp", mixnet, batch_threshold, bp_method)
        elif select_mode == "constraint":
            # select other layers
            mixnet.mix_select   = [] 
            all_mixes, batch_bw = get_batch_bw_static(mixnet, batch_threshold)
            new_mixes_pool = [m for m in all_mixes if m.bandwidth >= 1]
            select_by_rand(mixnet, new_mixes_pool, batch_bw)
            # place other layers
            mix_place("bp", mixnet, batch_threshold, bp_method)




def build_other_layers(mixnet, batch_threshold, bp_method):
    # select other layers
    mixnet.mix_select   = [] 
    select_pool = [m for m in mixnet.mix_pool if not m.GG and m.online]
    bw_goal     = 2 * sumup.sum_mix_bw(mixnet.mix_net[GUARD_LAYER])
    select_by_rand(mixnet, select_pool, bw_goal)

    # place other layers
    mix_place("bp", mixnet, batch_threshold, bp_method)


def mix_place(place_mode, mixnet, batch_threshold, bp_method="lp"):
    # print('-'*20)
    # print(f'selected bw: {sumup.sum_mix_bw(mixnet.mix_select)}')
    # print('-'*20)

    if mixnet.guard: # fixed not first epoch, keep middle layer
        assert(len(mixnet.mix_net[GUARD_LAYER])>0)
        for l in ['layer0', 'layer1', 'layer2']: # set other layers empty 
            if l != GUARD_LAYER:
                mixnet.mix_net[l] = []
    elif not mixnet.guard: # unfixed case
        mixnet.mix_net['layer0'] = []
        mixnet.mix_net['layer1'] = []
        mixnet.mix_net['layer2'] = []

    if place_mode == 'rand':
        place_rand(mixnet)
    elif place_mode == 'bp':
        place_bp(mixnet, bp_method) 
                # bp_method indicates which specific method of bin-packing solving
    elif place_mode == 'layer':
        place_layer(mixnet, batch_threshold)
    # elif place_mode in ['rand', 'nym']:
    #     constrained_place_rand(mixnet)

def place_rand(mixnet):
    """
    place mixes to each layer randomly using VRF function
    VRF() -> y, y is the random number
    l = y mod 3, l is the final chosen layer index
    """
    print('>>>vrfPlacement starts...')
    # alpha_string = random.getrandbits(256).to_bytes(32, 'little')

    # layer_index = []
    # l = 2 if mixnet.guard else 3
    # for m in mixnet.mix_select:
    #     layer_index.append(vrfGeneration(m.sk.to_bytes(32, 'little'), alpha_string)%l)
    
    # get randomplacement faster;)
    layer_index = []
    l = 2 if mixnet.guard else 3
    for m in mixnet.mix_select:
        layer_index.append(random.randint(0, 10000)%l) # using random function rather than VRF to save more calculation time.
    
    if mixnet.guard: # place two layers
        create_net(mixnet, replace_layer_index(layer_index))
    else: # place three layers
        create_net(mixnet, layer_index)
    print('>>>vrfPlacement ends...')

def constrained_place_rand(mixnet):
    print(">>>Random placement with constraint")
    total_bw = 11401.2045713556
    diff_threshold = 0.07 * total_bw
    iter_count = 0
    while iter_count < 50:
        layer_index = []
        l = 2 if mixnet.guard else 3
        for m in mixnet.mix_select:
            layer_index.append(random.randint(0, 10000)%l)

        # check if this match the contraint, say the difference threshold is 0.07 of total_bw
        layer_bw = [0, 0, 0]
        for idx, bin in enumerate(layer_index):
            layer_bw[bin] += mixnet.mix_select[idx].bandwidth
        max_df = max_diff(layer_bw[0], layer_bw[1], layer_bw[2], total_bw)
        if max_df <= diff_threshold:
            if mixnet.guard: # place two layers
                create_net(mixnet, replace_layer_index(layer_index))
            else: # place three layers
                create_net(mixnet, layer_index)
            print('>>>vrfPlacement ends...')
            break
        else:
            iter_count += 1
        
    
def max_diff(a, b, c, total_bw):    
    diff = [abs(a-b)/total_bw, abs(a-c)/total_bw, abs(b-c)/total_bw]
    return round(max(diff), 3)
   
def place_bp(mixnet, bp_method):
    """
    TODO: capacity is changing with batch_threshold
    when batch_threshold is low, capacity should be bigger proportion compared to when the batch_threshold is high
    """
    print('>>>binpackingPlacement starts...')
    # set the capacity for each bin
    weight   = [m.bandwidth for m in mixnet.mix_select]
    # assert(mixnet.guard == True)
    if mixnet.guard:
        capacity = mixnet.total_bw * (sum(weight)/mixnet.total_bw/2 + 0.003)
        print(f">>>capacity for one bin is {capacity}")
    else:
        capacity = mixnet.total_bw * (sum(weight)/mixnet.total_bw/3 + 0.003) # 0.003(0.75 0.45) --> 0.03[0.35]

    if bp_method == 'ffd': # fisrt-fit-decreasing
        print(">>>Heuristic_FFD")
        n_bins, bin_for_item = bp.heur_FFD(capacity, weight)
    elif bp_method == 'wfd': # worst-fit-decreasing
        print(">>>Heuristic_WFD")
        n_bins, bin_for_item = bp.heur_WFD(capacity, weight)
    elif bp_method == 'bfd': # best-fit-decreasing
        print(">>>Heuristic_BFD")
        n_bins, bin_for_item = bp.heur_BFD(capacity, weight)
    elif bp_method == 'lp': # linear programming
        print(">>>Linear Programmig")
        if mixnet.guard:
            n_bins, n_bins_lb, bin_for_item = bp.model_bpp(capacity, weight, 2, LogToConsole=False) 
            # print(f">>>bp layer index: {bin_for_item}")
        else:
            n_bins, n_bins_lb, bin_for_item = bp.model_bpp(capacity, weight, 3, LogToConsole=False)
            
    if mixnet.guard:
        create_net(mixnet, replace_layer_index(bin_for_item))
    else:
        create_net(mixnet, bin_for_item)

    print('>>>binpackingPlacement ends--------')

def replace_layer_index(layer_index):
    # for fixed case of bp placement: replace '1' by '2'
    print(">>>Replacing layer index")
    for l in layer_index:
        assert(l in [0, 1])

    new_index = []
    for l in layer_index:
        if l == 0:
            new_index.append((int(GUARD_LAYER[-1]) + 1) % 3 ) 
        if l == 1:
            new_index.append((int(GUARD_LAYER[-1]) + 2) % 3 ) 
    return new_index

def place_layer(mixnet, batch_threshold):
    """
    implementation of layer placement
    """
    print('--------layerPlacement starts--------')
    select_bw = [m.bandwidth for m in mixnet.mix_select]
    try:
        layer_threshold = batch_threshold / 3 * 0.99 * mixnet.total_bw 
                                        # layer threshold keeps the same whether fixed or not
    except TypeError as e:
        print(e)
    
    flag_index = []
    p = q = 0
    while p < len(select_bw):
        p += 1
        if sum(select_bw[q:p]) >= layer_threshold:
            flag_index.append(p)
            q = p
    if mixnet.guard and mixnet.is_dirty:
        layer_index = [0]*flag_index[0] + [1]*(len(select_bw)-flag_index[0]) # selected mixes are grouped into two sets
        create_net(mixnet, replace_layer_index(layer_index))
    else:
        layer_index = [0]*flag_index[0] + [1]*(flag_index[1]-flag_index[0]) + [2]*(len(select_bw)-flag_index[1])
        create_net(mixnet, layer_index)

    print('--------layerPlacement ends--------')


def create_net(mixnet, layer_index):
    # print(f'>>>layer_index: {layer_index}')
    mixnet.layer_index = layer_index
    mixnet.layer_bw    = [0, 0, 0]
    mixnet.bad_num     = [0, 0, 0]
    mixnet.bad_bw      = [0, 0, 0]
    try:
        for idx, bin in enumerate(layer_index):
            mixnet.layer_bw[bin] += mixnet.mix_select[idx].bandwidth
            mixnet.mix_net['layer'+str(bin)].append(mixnet.mix_select[idx])
            if mixnet.mix_select[idx].malicious:
                mixnet.bad_num[bin] += 1
                mixnet.bad_bw[bin]  += mixnet.mix_select[idx].bandwidth
        if mixnet.guard:
            for m in mixnet.mix_net[GUARD_LAYER]:
                if m.malicious == True:
                    mixnet.bad_num[int(GUARD_LAYER[-1])] += 1
                    mixnet.bad_bw[int(GUARD_LAYER[-1])]  += m.bandwidth
                mixnet.layer_bw[int(GUARD_LAYER[-1])] += m.bandwidth
        mixnet.layer_num = [len(l) for l in mixnet.mix_net.values()]
    except IndexError as e:
        print(f'Create mixnet failed: {e}')

def remove_mix(org_list, rmv_list):
    temp_list = []
    for m in org_list:
        if m.mix_id not in [m.mix_id for m in rmv_list]:
            temp_list.append(m)
    return temp_list

def gen_sk():
    """
    generate big integer and save int
    :return:
    """
    return random.getrandbits(256)

def vrfGeneration(sk, alpha_string):
    """
    Input: sk, alpha(x)--bytes
    output:beta, pi (bytes)
    :return: int(beta_string)
    """
    # alpha_string = random.getrandbits(256).to_bytes(32, 'little')
    # sk = random.getrandbits(256).to_bytes(32, 'little') #to_bytes(): convert big integer to bytes
    # print("sk = bytes.formhex('{})".format(sk.hex()))
    _, Y = vrf._get_secret_scalar_and_public_key(sk)
    pi_string = vrf.ecvrf_prove(sk, alpha_string)
    beta_string = vrf.ecvrf_proof_to_hash(pi_string)
    return int.from_bytes(beta_string, 'little')

def merge_mix_sk():
    """
    merge benign mix info and sk into one file
    """
    for i in [10, 100, 500, 1000]:
        # reading two csv files
        data1 = pd.read_csv(os.path.join('Benign_Mixes', "{}_Benign_Mix.csv".format(i)))
        data2 = pd.read_csv(os.path.join('Mix_SK', "{}Mix_SK.csv".format(i)))

        # using merge function by setting how='inner'
        output1 = pd.merge(data1, data2,
                        on='MixID',
                        how='inner')

        # writing output to csv file
        output1.to_csv(os.path.join('Benign_Mixes', "{}_benignmix.csv".format(i)), index=False) 
