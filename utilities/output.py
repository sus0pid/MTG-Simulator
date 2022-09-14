import os
import csv
import pandas as pd

def create_log_csv(config):
    attack_header = ['epoch', 'num_malicious', 'mal_frac', 'batch_th', 'total_bw', 
                'num_bad_l0', 'num_bad_guard', 'num_bad_l2',
                'num_lay_l0', 'num_guard', 'num_lay_l2', 
                'bad_bw_l0', 'bad_bw_guard', 'bad_bw_l2', 
                'lay_bw_l0', 'lay_guard', 'lay_bw_l2',
                'bw_frac_l0', 'bw_frac_guard', 'bw_frac_l2', 
                'circuit_controlled', 'attack_profit', 'attack_succ', 
                'num_guards']

    with open(os.path.join(config["log_dir"], '{0}_{1}_log.csv'.format(config["algorithm"], config["network"]["setting"])), 'w') as atfile:
        row = (',').join(attack_header)
        atfile.write(row)
        atfile.write('\n')

    time_column   = ['num_malicious', 'time_spent(second)']
    with open(os.path.join(config["log_dir"], '{0}_{1}_time.csv'.format(config["algorithm"], config["network"]["setting"])), 'w') as tfile:
        row = (',').join(time_column)
        tfile.write(row)
        tfile.write('\n')

def create_layout_csv(config, mix_pool):
    # df.insert(loc=0, column='mix_id', value=[i for i in range(num_mix)])
    mix_ids = [i for i in range(len(mix_pool))]
    bws  = [0] * len(mix_pool) # nodes that are not existed
    mals = [False] * len(mix_pool)
    for m in mix_pool:
        bws[m.mix_id] = m.bandwidth
        mals[m.mix_id] = m.malicious
    data = {
        "mix_id": mix_ids,
        "bandwidth": bws,
        "malicious": mals
    }
    # df.insert(loc=1, column='bandwidth', value=bws)
    # df.insert(loc=2, column='malicious', value=mals)
    df = pd.DataFrame(data)
    path = os.path.join(config["log_dir"], "{0}_{1}_layout.csv".format(config["algorithm"], config["network"]["setting"]))
    df.to_csv(path, index=False)

    

def create_batch_log_csv(args):
    attack_header = ['epoch', 'num_malicious', 'mal_frac', 'batch_th', 'total_bw', 
            'num_bad_l0', 'num_bad_guard', 'num_bad_l2',
            'num_lay_l0', 'num_guard', 'num_lay_l2', 
            'bad_bw_l0', 'bad_bw_guard', 'bad_bw_l2', 
            'lay_bw_l0', 'lay_guard', 'lay_bw_l2',
            'bw_frac_l0', 'bw_frac_guard', 'bw_frac_l2', 
            'circuit_controlled', 'attack_profit', 'attack_succ', 
            'num_guards']

    with open(os.path.join(args.output_dir, '{0}_{1}_{2}_{3}_{4}_log.csv'.\
                            format(args.adv_type, args.select_mode, args.place_mode, args.batch_threshold, args.binpack_solver)), 'w') as atfile:
        row = (',').join(attack_header)
        atfile.write(row)
        atfile.write('\n')

    time_column   = ['num_malicious', 'time_spent(second)']
    with open(os.path.join(args.output_dir, '{0}_{1}_{2}_{3}_{4}_time.csv'.\
                            format(args.adv_type, args.select_mode, args.place_mode, args.batch_threshold, args.binpack_solver)), 'w') as tfile:
        row = (',').join(time_column)
        tfile.write(row)
        tfile.write('\n')


def create_nym_log_csv(args):
    attack_header = ['epoch', 'num_malicious', 'mal_frac', 'batch_th', 'total_bw', 
                'num_bad_l0', 'num_bad_guard', 'num_bad_l2',
                'num_lay_l0', 'num_guard', 'num_lay_l2', 
                'bad_bw_l0', 'bad_bw_guard', 'bad_bw_l2', 
                'lay_bw_l0', 'lay_guard', 'lay_bw_l2',
                'bw_frac_l0', 'bw_frac_guard', 'bw_frac_l2', 
                'circuit_controlled', 'attack_profit', 'attack_succ', 
                'num_guards']

    with open(os.path.join(args.output_dir, '{0}_{1}_{2}_{3}_log.csv'.\
                            format(args.adv_type, args.select_mode, args.place_mode, args.mal_num)), 'w') as atfile:
        row = (',').join(attack_header)
        atfile.write(row)
        atfile.write('\n')

    time_column   = ['num_malicious', 'time_spent(second)']
    with open(os.path.join(args.output_dir, '{0}_{1}_{2}_{3}_time.csv'.\
                            format(args.adv_type, args.select_mode, args.place_mode, args.mal_num)), 'w') as tfile:
        row = (',').join(time_column)
        tfile.write(row)
        tfile.write('\n')





def write_all_mix(args, nm, mix_pool):
    # if args.adv_type == 'naive':
    label = nm
    # else:
        # label = args.batch_threshold
        
    with open(os.path.join(args.output_dir, '{0}_{1}_{2}_{3}_{4}_mixpool.csv'.\
                            format(args.adv_type, args.select_mode, args.place_mode, label, args.binpack_solver)), 'w') as f:
        header = (',').join(['MixID', 'Bandwidth', 'Malicious'])
        f.write(header)
        f.write('\n')
        for m in mix_pool:
            f.write(str(m))
            f.write('\n')

def write_attack_log(config, atk_logs):
    # write attack_log
    attack_header = ['epoch', 'num_malicious', 'mal_frac', 'batch_th', 'total_bw', 
                    'num_bad_l0', 'num_bad_guard', 'num_bad_l2',
                    'num_lay_l0', 'num_guard', 'num_lay_l2', 
                    'bad_bw_l0', 'bad_bw_guard', 'bad_bw_l2', 
                    'lay_bw_l0', 'lay_guard', 'lay_bw_l2',
                    'bw_frac_l0', 'bw_frac_guard', 'bw_frac_l2', 
                    'circuit_controlled', 'attack_profit', 'attack_succ']
    if config["network"]["setting"] == "dynamic":
        with open(os.path.join(config["log_dir"], '{0}_{1}_log.csv'.\
                            format( config["algorithm"], 
                                    config["network"]["setting"]
                                    # config["network"]["churn_rate"]["leave_rate"]
                                    )), 'w') as attackfile:
                                            atk_logs.insert(0, attack_header)
                                            at_writer = csv.writer(attackfile)
                                            at_writer.writerows(atk_logs)
    else:
        with open(os.path.join(config["log_dir"], '{0}_{1}_log.csv'.\
                    format( config["algorithm"], 
                            config["network"]["setting"])), 'w') as attackfile:
                                    atk_logs.insert(0, attack_header)
                                    at_writer = csv.writer(attackfile)
                                    at_writer.writerows(atk_logs)

def write_layout(config, layouts, mix_pool):
    layout_data = {}
    num_mix = len(mix_pool)
    for idx, layout_col in enumerate(layouts):
        if len(layout_col) < num_mix:
            layout_col.extend([-2]*(num_mix-len(layout_col)))
        layout_data["epoch_{}".format(idx)] = layout_col
    df = pd.DataFrame(layout_data)
    
    # add columns of mix_id, bw, and malicious
    df.insert(loc=0, column='mix_id', value=[i for i in range(num_mix)])
    bws  = [0] * num_mix # nodes that are not exited
    mals = [False] * num_mix
    for m in mix_pool:
        bws[m.mix_id] = m.bandwidth
        mals[m.mix_id] = m.malicious
    df.insert(loc=1, column='bandwidth', value=bws)
    df.insert(loc=2, column='malicious', value=mals)
    
    if config["network"]["setting"] == "dynamic":
        path = os.path.join(config["log_dir"], "{0}_{1}_layout.csv".format(config["algorithm"], config["network"]["setting"]
        # , config["network"]["churn_rate"]["leave_rate"]
        ))
    elif config["network"]["setting"] == "static":
        path = os.path.join(config["log_dir"], "{0}_{1}_layout.csv".format(config["algorithm"], config["network"]["setting"]))
    df.to_csv(path, index=False)

def write_onoff(config, on_offs, mixnet):
    on_off_data = {}
    num_mix = len(mixnet.mix_pool)
    for idx, on_off_col in enumerate(on_offs):
        if len(on_off_col) < num_mix:
            on_off_col.extend([0] * (num_mix - len(on_off_col)))
        on_off_data["epoch_{}".format(idx)] = on_off_col
    df = pd.DataFrame(on_off_data)
    df.insert(loc=0, column='mix_id', value=[i for i in range(num_mix)])
    path = os.path.join(config["log_dir"], "{0}_{1}_{2}_onoff.csv".format(config["algorithm"], config["network"]["setting"], config["network"]["churn_rate"]["leave_rate"]))
    df.to_csv(path, index=False)

def write_gg_times(config, mixnet):
    data = {
        "mix_id": [m.mix_id for m in mixnet.mix_pool],
        "gg_times": [m.GG_times for m in mixnet.mix_pool]
    }
    df = pd.DataFrame(data)
    path = os.path.join(config["log_dir"], "{0}_{1}_{2}_ggtimes.csv".format(config["algorithm"], config["network"]["setting"], config["network"]["churn_rate"]["leave_rate"]))
    df.to_csv(path, index=False)