from re import L
import sys
sys.path.append("../classes")
sys.path.append("../utilities")
sys.path.append("../constructions")
import mix_churn as mc
import output
import proc_log as pl
import mixnet_gen as mng
import sumup
from mixnet import Mixnet

def dynamic_randrand(mix_pool, config):
    mixnet = Mixnet(mix_pool, 
                    sumup.sum_mix_bw(mix_pool),
                    config["benign_mixes_num"], 
                    guard=False)
    atk_logs = []
    layouts = []
    on_offs = []
    for e in range(config["epoch_num"]):   
        print(
            '\n\n==============================================================================')
        print(f'>>>EPOCH-{e}')

        # 0. check mix_id duplication
        mixnet.check_id()

        # 1. mixnet construction
        print(">>>Constructing the mixnet with online nodes.")
        mng.mix_select('rand', mixnet, config["construction"]["sample_fraction"], config["network"]["setting"])
        mng.mix_place("rand", mixnet, config["construction"])
        attack_row, layout_col, on_off_col = pl.cmpLog(mixnet, 
                                            config["adversary"]["bw_fraction"],
                                            config["construction"]["sample_fraction"], 
                                            setting = config["network"]["setting"])
        # 2. natural churn
        print(">>>Natural churn is happening.")
        print(
            f">>>number of online mixes before churn: {mixnet.get_online_counts()}")
        mc.natural_churn(mixnet, 
                        e+1, 
                        is_poisson=False,
                        churn_nums=mc.constant_churn_nums(config["network"]["churn_rate"], 
                        mixnet.get_online_counts()))
        # nodes go offline, nodes go back, new nodes joining for the next epoch
        # dob of new nodes == e+1 rather than e
        print(
            '\n==============================================================================\n\n')
        attack_row.insert(0, e)
        atk_logs.append(attack_row)
        layouts.append(layout_col)
        on_offs.append(on_off_col)
    # write attack_log
    output.write_attack_log(config, atk_logs)
    # write layout
    output.write_layout(config, layouts, mixnet.mix_pool)
    # write online/offline status
    output.write_onoff(config, on_offs,  mixnet)

def static_randrand(mix_pool, config):
    atk_logs = []
    layouts = []
    for e in range(config["epoch_num"]):   
        print(
            '\n\n==============================================================================')
        print(f'>>>EPOCH-{e}')
        mixnet = Mixnet(mix_pool, 
                    sumup.sum_mix_bw(mix_pool),
                    config["benign_mixes_num"], 
                    guard=False)

        # 0. check mix_id duplication
        # mixnet.check_id()

        # 1. mixnet construction
        print(">>>Constructing the mixnet with online nodes.")
        mng.mix_select('rand', mixnet, config["construction"]["sample_fraction"], config["network"]["setting"])
        mng.mix_place("rand", mixnet, config["construction"])
        attack_row, layout_col = pl.cmpLog(mixnet, 
                                            config["adversary"]["bw_fraction"],
                                            config["construction"]["sample_fraction"], 
                                            setting = config["network"]["setting"])
        # 2. natural churn
        # print(">>>Natural churn is happening.")
        # print(
        #     f">>>number of online mixes before churn: {mixnet.get_online_counts()}")
        # mc.natural_churn(mixnet, 
        #                 e+1, 
        #                 is_poisson=False,
        #                 churn_nums=mc.constant_churn_nums(config["network"]["churn_rate"], 
        #                 mixnet.get_online_counts()))
        # nodes go offline, nodes go back, new nodes joining for the next epoch
        # dob of new nodes == e+1 rather than e
        print(
            '\n==============================================================================\n\n')
        attack_row.insert(0, e)
        atk_logs.append(attack_row)
        layouts.append(layout_col)
    # write attack_log
    output.write_attack_log(config, atk_logs)
    # write layout
    output.write_layout(config, layouts, mixnet.mix_pool)
