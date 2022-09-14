"""
Deal with guard set check, add, and prune
"""
import sys
sys.path.append("../classes")
from os import execv
import mixnet_gen as mng
import sumup
import numpy as np
import mix_churn as mc
import math


def get_online_mixes(mix_list):
    return [m for m in mix_list if m.online]


def get_non_guard_mixes(mix_list):
    return [m for m in mix_list if not m.GG]


def build_guard_set(mixnet, current_epoch, guard_threshold, BG_threshold):
    mixnet.refresh_total_bw()
    if current_epoch == 0:
        # build guard set from mix pool
        AG_select_pool = get_online_mixes(mixnet.mix_pool)
        # the first time configure guard layer
        ActiveG_list = select_by_bw(
            AG_select_pool, guard_threshold*mixnet.total_bw)
        # label nodes as guards, track the AGT
        label_GG(ActiveG_list, mixnet, current_epoch)
        label_AG(ActiveG_list, mixnet)

        BG_select_pool = get_non_guard_mixes(get_online_mixes(mixnet.mix_pool))
        BackupG_list = select_by_bw(
            BG_select_pool, BG_threshold*mixnet.total_bw)  # say, 3%
        label_GG(BackupG_list, mixnet, current_epoch)

        # put AG and BG to GG set
        mixnet.GG_set['AG'] = ActiveG_list
        mixnet.GG_set['BG'] = BackupG_list

        # place AG in guard layer
        mixnet.mix_net[mng.GUARD_LAYER] = ActiveG_list

    else:  # epoch > 0
        # after mix churn, we check the guard layer first
        low_bound = guard_threshold - 0.02
        high_bound = guard_threshold + 0.02
        onlineG_list = check_guard_churn(
                                        mixnet, 
                                        low_bound, 
                                        high_bound, 
                                        current_epoch)
        print(
            f">>>guard_threshold: {guard_threshold}, {guard_threshold*mixnet.total_bw}")
        print(f">>>low_bound: {low_bound}, {low_bound*mixnet.total_bw}")

        # copy old guards into new AG
        old_AG_ids = [m.mix_id for m in mixnet.GG_set['AG']]
        new_AG = [m for m in onlineG_list if m.mix_id in old_AG_ids]

        # if there is any old guards come back, add them
        rest_onlineG = [m for m in onlineG_list if m not in new_AG]
        new_AG.extend(
            [m for m in rest_onlineG if m not in new_AG and m.AGT > 0])

        # check if it reaches threshold
        if sumup.sum_mix_bw(new_AG) < low_bound*mixnet.total_bw:
            rest_onlineG = [m for m in onlineG_list if m not in new_AG]
            normalize_stab(rest_onlineG)
            sorted_rest_onlineG = sorted(rest_onlineG,
                                         key=lambda m: (
                                             m.bandwidth*m.norm_stab, m.norm_stab),
                                         reverse=True)

            for m in sorted_rest_onlineG:
                new_AG.append(m)
                if sumup.sum_mix_bw(new_AG) >= low_bound*mixnet.total_bw:
                    break

        # try:
        #     assert(mg.sum_mix_bw(new_AG) >= low_bound*mixnet.total_bw)
        # except AssertionError as e:
        #     print(e)
        #     print(f'total bandwidth: {mixnet.total_bw}')
        #     print(f'AG bandwidth: {sumup.sum_mix_bw(new_AG)}')
        #     mc.disp_mixes(new_AG)
        #     sys.exit('Not reach bw threshold!')

        mixnet.GG_set['AG'] = new_AG
        mixnet.GG_set['BG'] = [m for m in onlineG_list if m not in new_AG]

        # track AGT after selecting AG set
        label_AG(mixnet.GG_set['AG'], mixnet)
        mixnet.mix_net[mng.GUARD_LAYER] = mixnet.GG_set['AG']

        # # then select AG from onlineG, the rest of them are BG
        # if mg.sum_mix_bw(onlineG_list) <= guard_threshold*mixnet.total_bw:
        #     # put all onlineG to AG set
        #     mixnet.GG_set['AG'] = onlineG_list
        #     mixnet.GG_set['BG'] = [] # BG is emptyl_bw:
        # else:
        #     """select AG from all onlineGs when onlineGs are sufficient:
        #     1. copy old AG that are still alive--delete this in new version
        #     2. sort by AGT * stab in descending order
        #     3. pick nodes from top to bottom until reach the layer_threshold
        #     """
        #     # # # # step 1 keep using old online AG
        #     # old_AG_ids = [m.mix_id for m in mixnet.GG_set['AG']]
        #     # new_AG     = [m for m in onlineG_list if m.mix_id in old_AG_ids]

        #     # step 2 normalize the stab of rest nodes (0-1)
        #     # rest_onlineG = [m for m in onlineG_list if m not in new_AG]

        #     # step 1 normalize stab of all online GG to range(0-1)
        #     # normalize_stab(onlineG_list)

        #     # setp 2 sort onlineG by AGT*stab, and break ties by bandwidth*stab
        #     # sorted_rest_onlineG = sorted(onlineG_list,
        #     #                             key=lambda m:(m.AGT*m.norm_stab, m.bandwidth*m.norm_stab),
        #     #                             reverse=True)

        #     # step 3 pick nodes to AG, left of them are BG
        #     # new_AG = []
        #     # i = 0
        #     # while mg.sum_mix_bw(new_AG) < guard_threshold*mixnet.total_bw:
        #     #     new_AG.append(sorted_rest_onlineG[i])
        #     #     i += 1

        #     # just use all old online guards
        #     new_AG = [m for m in onlineG_list if m.stab > 0.01 and m.AGT > 0]

    # print(f'\n>>>EPOCH {current_epoch} GG as below')
    # print(f">>>{len(mixnet.GG_set['AG'])} nodes in AG:")
    # mc.disp_mixes(mixnet.GG_set['AG'])
    # print("\n")
    # print(f">>>{len(mixnet.GG_set['BG'])} nodes in BG:")
    # mc.disp_mixes(mixnet.GG_set['BG'])
    # print('\n')
    # print(f">>>{len(mixnet.GG_set['DG'])} nodes in DG:")
    # mc.disp_mixes(mixnet.GG_set['DG'])
    # print(f">>>total guard nodes in EPOCH-{current_epoch}: {len([m for m in mixnet.mix_pool if m.GG])}")
    # mc.disp_mixes([m for m in mixnet.mix_pool if m.GG])
    try:
        assert (len(mixnet.GG_set['AG']) + len(mixnet.GG_set['BG']) + len(
            mixnet.GG_set['DG']) == len([m for m in mixnet.mix_pool if m.GG]))
    except AssertionError as e:
        print(e)
        sys.exit("Error occurred!")


def check_guard_churn(mixnet, low_bound, high_bound, current_epoch):  # low:23%, high:27%
    # move offline nodes, back nodes to corresponding set
    # make sure all nodes are fetch from mix_pool which is the most updated
    DownG_list = [
        m for m in mixnet.mix_pool if not m.online and m.GG]  # DG of GG
    mixnet.GG_set['DG'] = DownG_list

    onlineG_list = [m for m in mixnet.mix_pool if m.online and m.GG]  # AG+BG
    # check if onlineG too few
    bw_goal = sumup.sum_mix_bw(onlineG_list) - low_bound*mixnet.total_bw
    print(f'>>>check-mixnet total bw: {mixnet.total_bw}')
    print(f'>>>check-low_bound: {low_bound}, {low_bound*mixnet.total_bw}')
    print(f'>>>bw sum: {sumup.sum_mix_bw(onlineG_list)}')
    print(f'>>>bw_diff with low bound: {bw_goal}')

    if bw_goal < 0:
        # too few onlineG, bw+stab select new guards from mix pool
        newGG_select_pool = get_non_guard_mixes(
            get_online_mixes(mixnet.mix_pool))
        normalize_stab(newGG_select_pool)
        sorted_newGG_select_pool = sorted(newGG_select_pool, key=lambda m: (m.bandwidth*m.norm_stab),
                                          reverse=True)
        # pick newGG according to bw*stab
        newGG = []
        i = 0
        while sumup.sum_mix_bw(newGG) < abs(bw_goal):
            newGG.append(sorted_newGG_select_pool[i])
            i += 1

        print(f">>>Too few GG, add {len(newGG)} new GG")
        mc.disp_mixes(newGG)
        # label GG each time introduce new GG
        label_GG(newGG, mixnet, current_epoch)
        onlineG_list.extend(newGG)

    else:  # check if onlineG too many
        bw_goal = sumup.sum_mix_bw(onlineG_list) - high_bound*mixnet.total_bw
        print(
            f">>>check-high bound: {high_bound}, {high_bound*mixnet.total_bw}")
        print(f">>>bw_diff with high bound: {bw_goal}")
        if bw_goal > 0:
            # too many onlineG, remove active BG such that they can in other layers
            elim_pool = [m for m in onlineG_list if m.AGT == 0]
            if elim_pool:
                sorted_elim_pool = sorted(elim_pool, key=lambda m: m.stab)
                elim_GG = []
                for i, m in enumerate(sorted_elim_pool):
                    elim_GG.append(m)
                    if sumup.sum_mix_bw(elim_GG) >= bw_goal:
                        break
                if elim_GG:
                    print(f">>>Too many GG, eliminate {len(elim_GG)} guards.")
                    mc.disp_mixes(elim_GG)
                    unlabel_GG(elim_GG, mixnet)
                    onlineG_list = mng.remove_mix(onlineG_list, elim_GG)

    return onlineG_list


def periodic_guard_elimination(mixnet, guard_eliminate_stab):
    """
    eliminate nodes with stab lower than x TODO: x= 0/0.2 ? 
    """
    old_DG = [m for m in mixnet.GG_set['DG']]
    eliminated_DG = [m for m in old_DG if m.stab < guard_eliminate_stab]
    if len(eliminated_DG):
        print(
            f">>>Periodical elimination: {len(eliminated_DG)} DG has been removed from Guard set.")
        mc.disp_mixes(eliminated_DG)
        unlabel_GG(eliminated_DG, mixnet)
        mixnet.GG_set['GG'] = mng.remove_mix(old_DG, eliminated_DG)

    # stab_sorted_DG = sorted(old_DG, key=lambda m: (m.stab, m.bandwidth)) # bw & stab
    # eliminate_num = round(guard_eliminate_rate *
    #                     (len(mixnet.GG_set['AG'] + mixnet.GG_set['BG'] + mixnet.GG_set['DG'])))
    # eliminate_num = min(eliminate_num, len(stab_sorted_DG))
    # if eliminate_num > 0:
    #     print(f">>>{eliminate_num} Down Guards are removed in periodic elimination.")
    #     eliminated_DG = [stab_sorted_DG[i] for i in range(eliminate_num)]
    #     mc.disp_mixes(eliminated_DG)
    #     unlabel_GG(eliminated_DG, mixnet)
    #     mixnet.GG_set['GG'] = stab_sorted_DG[eliminate_num:]


def normalize_stab(mix_list):
    all_stabs = [m.stab for m in mix_list]
    try:
        norm_stabs = [(s-min(all_stabs))/(max(all_stabs)-min(all_stabs))
                      for s in all_stabs]
    except ZeroDivisionError as e:
        print(e)
        print(all_stabs)
        norm_stabs = all_stabs
    for m, ns in zip(mix_list, norm_stabs):
        m.set_norm_stab(ns)


def select_by_bwstab(select_pool, bw_goal):
    # select mixes by bw and stab until reach bw_goal
    selected_mixes = []
    while True:
        weights = [bw_stab_weight(m, select_pool) for m in select_pool]
        sample_mix = np.random.choice(
            select_pool, 1, replace=False, p=weights).tolist()
        selected_mixes.extend(sample_mix)
        select_pool = mng.remove_mix(select_pool, sample_mix)
        if sumup.sum_mix_bw(selected_mixes) >= bw_goal:
            break
    return selected_mixes


def bw_stab_weight(mix, mix_list):
    weight = 0.5 * mix.bandwidth / \
        sumup.sum_mix_bw(mix_list) + 0.5 * mix.stab / \
        sumup.sum_mix_stab(mix_list)
    return weight


def select_by_bw(select_pool, bw_goal):
    # select mixes until they reach bw_goal
    selected_mixes = []
    while True:
        weights = [m.bandwidth /
                   sumup.sum_mix_bw(select_pool) for m in select_pool]
        sample_mix = np.random.choice(
            select_pool, 1, replace=False, p=weights).tolist()
        selected_mixes.extend(sample_mix)
        select_pool = mng.remove_mix(select_pool, sample_mix)
        if sumup.sum_mix_bw(selected_mixes) >= bw_goal:
            break
    return selected_mixes


def label_GG(guard_list, mixnet, current_epoch):
    for m in mixnet.mix_pool:
        if m in guard_list:
            m.as_GG(current_epoch)


def label_AG(AG_list, mixnet):
    for m in mixnet.mix_pool:
        if m in AG_list:
            m.as_AG()


def unlabel_GG(elmt_list, mixnet):
    for m in mixnet.mix_pool:
        if m in elmt_list:
            m.no_more_GG()
