import numpy as np
import sumup
import pprint as pp
import sys
sys.path.append("../constructions")
import mix_gen as mg


def poisson_churn_nums(epoch_num, churn_rates):
    """
    We suppose malicious mixes never go offline, only honest nodes go offline
    epoch_num = 1000(ideally 10000) the larger the better
    """
    leave_per_minute = 16/60  # 1100*0.015
    back_per_minute = 13/60  # 1100*0.012
    new_good_per_minute = 3/60  # 1100*0.003
    new_bad_per_minute = 1/60  # 1100*0.001
    observe_period = 60    # 1 epoch = 60 minutes

    lam_leave = leave_per_minute * observe_period
    lam_back = back_per_minute * observe_period
    lam_new_good = new_good_per_minute * observe_period
    lam_new_bad = new_bad_per_minute * observe_period
    leave_nums = np.random.poisson(lam_leave, epoch_num)
    back_nums = np.random.poisson(lam_back, epoch_num)
    new_good_nums = np.random.poisson(lam_new_good, epoch_num)
    new_bad_nums = np.random.poisson(lam_new_bad, epoch_num)

    return {"leave_nums":    leave_nums,
            "back_nums":     back_nums,
            "new_good_nums": new_good_nums,
            "new_bad_nums":  new_bad_nums
            }  # churn_nums


def constant_churn_nums(churn_rates, total_mixes):
    """
    churn with constant rates
    """
    churn_nums = {
        "leave_num": round(total_mixes * churn_rates["leave_rate"]),
        "back_num": round(total_mixes * churn_rates["back_rate"]),
        "new_good_num": round(total_mixes * churn_rates["new_good_rate"]),
        "new_bad_num": round(total_mixes * churn_rates["new_bad_rate"])
    }
    pp.pprint(churn_nums)
    return churn_nums


def natural_churn(mixnet, epoch_idx, is_poisson, churn_nums):
    # leaving and coming back
    # both mal and honest nodes can go offline
    online_mixes = mixnet.get_active_mix()
    offline_mixes = mixnet.get_down_mix()
    if is_poisson:
        leave_num = churn_nums["leave_nums"][epoch_idx]
        back_num = churn_nums["back_nums"][epoch_idx]
        new_good_num = churn_nums["new_good_nums"][epoch_idx]
        new_bad_num = churn_nums["new_bad_nums"][epoch_idx]
    else:
        leave_num = churn_nums["leave_num"]
        back_num = churn_nums["back_num"]
        new_good_num = churn_nums["new_good_num"]
        new_bad_num = churn_nums["new_bad_num"]

    leave_this_epoch = np.random.choice(online_mixes, min(
        leave_num, mixnet.get_online_counts()), replace=False).tolist()

    if len(offline_mixes):
        back_this_epoch = np.random.choice(offline_mixes, min(back_num, len(offline_mixes)),
                                           replace=False).tolist()
    else:
        back_this_epoch = []

    for m in mixnet.mix_pool:
        if m in leave_this_epoch:
            m.go_down()
        elif m in back_this_epoch:
            m.go_back()

    # new mixes joining
    new_good_this_epoch = mg.gen_new_mixes(
        new_good_num, len(mixnet.mix_pool), False, epoch_idx)
    mixnet.mix_pool.extend(new_good_this_epoch)
    new_bad_this_epoch = mg.gen_new_mixes(
        new_bad_num, len(mixnet.mix_pool), True, epoch_idx)
    mixnet.mix_pool.extend(new_bad_this_epoch)

    print(f'\n>>>EPOCH {epoch_idx} network churn as below')
    print(
        f">>>{len(leave_this_epoch)} nodes leave, which was supposed to be {leave_num} nodes.")
    # disp_mixes(leave_this_epoch)
    # print("\n")
    print(
        f">>>{len(back_this_epoch)} nodes back, which was supposed to be {back_num} nodes.")
    # disp_mixes(back_this_epoch)
    # print('\n')
    print(f">>>{len(new_good_this_epoch)} good nodes join, which was supposed to be {new_good_num} nodes.")
    # disp_mixes(new_good_this_epoch)
    # print('\n')
    print(f">>>{len(new_bad_this_epoch)} bad nodes join, which was supposed to be {new_bad_num} nodes.")
    # disp_mixes(new_bad_this_epoch)
    # print("\n")
    print(
        f">>>Now there are {mixnet.get_offline_counts()} offline nodes, {mixnet.get_online_counts()} online nodes in mix pool.")


def disp_mixes(mix_list):
    print('----------MIX LIST START----------')
    print(f'total number of mixes: {len(mix_list)}')

    print('mix_id,\tbw,\tmal,\tonoff,\tif_GG,\tAGT,\tstab,\tuptime,\tpt,\tdown,\tkt')
    for m in mix_list:
        print(m)
    print('----------MIX LIST END----------')
