import sys
sys.path.append("../classes")
sys.path.append("../utilities")
sys.path.append("../constructions")
import mix_churn as mc
import guard_maintain as gm
import output
import proc_log as pl
import mixnet_gen as mng
import sumup
from mixnet import Mixnet
import time
import os

def dynamic_bowtie(mix_pool, config):

    mixnet = Mixnet(mix_pool, 
                    sumup.sum_mix_bw(mix_pool),
                    config["benign_mixes_num"], 
                    guard=True)
    atk_logs = []
    layouts = []
    on_offs = []
    for e in range(config["epoch_num"]):   
        print('\n'+'='*20)
        print(f'>>>EPOCH-{e}')

        # 0. check mix_id duplication
        mixnet.check_id()

        # 1. guard set maintainance
        print(">>>Constructing and maintaining GUARD layer.")
        guard_threshold = config["construction"]["sample_fraction"] / 3
        # percentage of total_bw
        BG_threshold = config["network"]["churn_rate"]["leave_rate"] / 2
        gm.build_guard_set(mixnet, 
                            e, 
                            config["construction"]["sample_fraction"]/3, BG_threshold)

        # periodically elimination
        if e > 0 and e % config["network"]["guard"]["eliminate_interval"] == 0:
            gm.periodic_guard_elimination(
                                        mixnet, 
                                        config["network"]["guard"]["stability_lower_bound"])

        # 2. other layers reconfiguration
        print(">>>Configure the other two layers.")
        mng.build_other_layers(
            mixnet, config["construction"]["sample_fraction"], "lp") # lp: bin-packing solver

        attack_row, layout_col, on_off_col = pl.cmpLog(mixnet, 
                                            config["adversary"]["bw_fraction"],
                                            config["construction"]["sample_fraction"], 
                                            setting = config["network"]["setting"])

        # 3. mix stability info update happens at the end of the epoch
        print(f">>>Updating mix uptime and stability information.")
        mixnet.update_mix_stab(e)
        # mixnet.disp_mix_stab()

        # 4. natural churn
        print(">>>Natural churn is happening.")
        # print(
        #     f">>>number of online mixes before churn: {mixnet.get_online_counts()}")
        mc.natural_churn(mixnet, 
                        e+1, 
                        is_poisson=False,
                        churn_nums=mc.constant_churn_nums(config["network"]["churn_rate"], 
                        mixnet.get_online_counts()))
        # nodes go offline, nodes go back, new nodes joining for the next epoch
        # dob of new nodes == e+1 rather than e
        # print('\n'+'='*20)

        attack_row.insert(0, e)
        atk_logs.append(attack_row)
        layouts.append(layout_col)
        on_offs.append(on_off_col)

    # write attack_log
    output.write_attack_log(config, atk_logs)
    # write layout
    output.write_layout(config, layouts, mixnet.mix_pool)
    # write on_off
    output.write_onoff(config, on_offs,  mixnet)
    # # write GG_times
    # output.write_gg_times(config, mixnet)

def static_bowtie(mix_pool, config):
    start = time.time()
    atk_logs = []
    layouts  = []
    mixnet = Mixnet(mix_pool, 
                    sumup.sum_mix_bw(mix_pool), 
                    config["benign_mixes_num"], 
                    True)
    for e in range(config["epoch_num"]):
        print('\n'+'='*20)
        print(f'>>>EPOCH-{e}')
        mng.hybrid_mixnet(mixnet, 
                        config["construction"]["sample_fraction"],
                        e, 
                        "constraint") # selection mode for other two layers
                    
        attack_row, layout_col = pl.cmpLog(mixnet, 
                                        config["adversary"]["bw_fraction"], config["construction"]["sample_fraction"],
                                        config["network"]["setting"])
        # print('\n'+'='*20)
        attack_row.insert(0, e)
        atk_logs.append(attack_row)
        layouts.append(layout_col)

    output.write_attack_log(config, atk_logs)
    # write layout
    output.write_layout(config, layouts, mixnet.mix_pool)

    done = time.time() - start
    # print(f'bowtie simulation spent {done} seconds')
    # res = [attack_row, 
    #         layout_col, 
    #         [config["adversary"]["num_malicious_nodes"], done], 
    #         config["adversary"]["num_malicious_nodes"],
    #         e]
    # return res