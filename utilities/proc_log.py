import sys
from numpy.random import f
from pandas import Index
import sys
sys.path.append("../classes")
from mixnet import Mixnet
import numpy as np
import pprint as pp
import os
# import mix_churn as mc


def cmpLog(mixnet, mal_bw_frac, batch_threshold, setting = "static", adv_type = "naive"):
    # print('>>>start cmp log data------')

    # each selection will generate a new layer_for_nodes list
    # each list will be written into layer_for_nodes.csv as a column
    # mixnet.disp_mixnet()
    attack_succ = True if 0 not in mixnet.bad_num else False
    try:
        attack_profit = np.prod([bb / lb for (bb, lb) in list(zip(mixnet.bad_bw, mixnet.layer_bw))])
        # print(attack_profit)
                                                                # adversary bandwidth proportion
        circuit_profit = np.prod([bn / ln for (bn, ln) in list(zip(mixnet.bad_num, mixnet.layer_num))])  
                                                                # adversary circuit proportion
        num_guards     = len([m for m in mixnet.mix_pool if m.GG])

        layer_frac     = [lbw/mixnet.total_bw for lbw in mixnet.layer_bw]
    except ZeroDivisionError as e:
        print('>'*10 + 'MIXNET INFO' + '<'*10)
        mixnet.disp_mixnet()
        print(f'layer_num: {mixnet.layer_num}')
        print(f'layer_bw: {mixnet.layer_bw}')
        print(f'bad_num: {mixnet.bad_num}')
        print(f'bad_bw: {mixnet.bad_bw}')
        print(e)


    # print('>'*10 + 'MIXNET INFO' + '<'*10)
    # print(f'layer_num: {mixnet.layer_num}')
    # print(f'layer_bw: {mixnet.layer_bw}')
    # print(f'layer_prop: {[round(lb/mixnet.total_bw, 4) for lb in mixnet.layer_bw]}')
    # print(f'bad_num: {mixnet.bad_num}')
    # print(f'bad_bw: {mixnet.bad_bw}')
    # print(f'bad_prop: {[round(b/mixnet.total_bw, 4) for b in mixnet.bad_bw]}')
    # print(f'attack benefit: {attack_profit}')
    # print(f'circuit controlled: {circuit_profit}')
    # print('>'*10 + 'MIXNET INFO' + '<'*10)
    # if adv_type == "naive":
    #     num_mal = len([m for m in mixnet.mix_pool if m.malicious])
    # elif adv_type == "smart":
    #     num_mal = nm
    # elif adv_type == "quantity":
    #     num_mal = nm # bw of mal_mixes
    num_mal = len([m for m in mixnet.mix_pool if m.malicious])
    attack_row = [num_mal, mal_bw_frac, batch_threshold, mixnet.total_bw] + \
                  mixnet.bad_num + mixnet.layer_num + mixnet.bad_bw + \
                  mixnet.layer_bw + layer_frac + \
                  [circuit_profit, attack_profit, attack_succ]
    # attack_row = [num_mal, mal_bw_frac, batch_threshold, mixnet.total_bw] + \
    #             mixnet.bad_num + mixnet.layer_num + mixnet.bad_bw + \
    #             mixnet.layer_bw + layer_frac + \
    #             [circuit_profit, attack_profit, attack_succ, num_guards]

    # get layer_no for mix_pool
    if setting == "static":
        layout_col = [-1] * len(mixnet.mix_pool)
        for l in range(3):
            for m in mixnet.mix_net['layer'+str(l)]:
                layout_col[m.mix_id] = l

    elif setting == "dynamic":
        # layout_col = [-1] * len(mixnet.mix_pool) + [-2] * (max_row_num-len(mixnet.mix_pool))
        layout_dict = {}
        layout_col = [-1] * len(mixnet.mix_pool) 

        for l in range(3):
            for m in mixnet.mix_net['layer'+str(l)]:
                layout_dict[m.mix_id] = l
        # print(layout_dict)
        for i in layout_dict.keys():
            layout_col[i] = layout_dict[i]
        # print(layout_col)



    # get on/offline status from mix_pool
    if setting == "static":
        on_off_col = [] * len(mixnet.mix_pool)
    elif setting == "dynamic":
        on_off_col = [] * len(mixnet.mix_pool) # on:1, off:-1, non-exist:0
    for m in mixnet.mix_pool:
        try:
            on_off_col[m.mix_id] = 1 if m.online else -1
        except IndexError as e:
            on_off_col.append(1 if m.online else -1)
            # sys.exit(e)

    if setting == "dynamic":
        return attack_row, layout_col, on_off_col
    else:
        return attack_row, layout_col

def writeBadMixes(mixnet, idx, batch_threshold):
    #write mixesall to csv file
    #mixall_index: file index
    print('----start writing all mixes to files------')
    try:
        # filename = 'ranmal_mixall'+str(mixall_index)+'.csv'
        with open(os.path.join('All_Mixes_{}'.format(batch_threshold), '{}_allmix.csv'.format(idx)), 'w') as mixall_w:
            header = 'MixID, Bandwidth, Malicious, SK\n'
            mixall_w.write(header)
            for m in mixnet.mix_pool:
                mixall_w.write(str(m))
                mixall_w.write('\n')
    except IOError as e:
        print(e)
        print('Write mixall to CSV failed')


# def writeHitLog(filename):
#     # write hit rates to csv
#     # in order to preserve previous data
#     # try:  # there exist hit log file
#     #     pre_data  = pd.read_csv(filename, usecols=["hit_rate"], skipinitialspace=True)["hit_rate"]
#     #     data = {"mix_id": [i for i in range(self.num_benign + DEFAULT_MAX_BAD_MIX_NUM)],
#     #             "hit_rate": [hit + phit for (hit, phit) in list(zip(self.hit_log, pre_data))]}
#     # except IOError as e:  # no layout log file before


#     data = {"mix_id": [m.mix_id for m in mixnet.mix_pool],
#             "hit_rate": self.hit_log}

#     df = pd.DataFrame(data)
#     df.to_csv(filename, index=False)

# def writeLayoutLog(mixnet, idx, batch_threshold):
#     assert (len(self.layout_log) >= 2)
#     data = {}
#     for idx, log in enumerate(self.layout_log):
#         if idx == 0:
#             data["mix_id"] = log
#         else:
#             data[idx] = log
#     df = pd.DataFrame(data)
#     df.to_csv(filename, index=False)
