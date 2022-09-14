import sys
sys.path.append("../constructions")
import mix_gen as mg
import time
import os
import json
import glob
from bowtie import *
from bwrand import *
from randrand import *
from randbp import *
import multiprocessing as mp
import csv
import pandas as pd


# def static_simulation(mix_pool, config, e, q):
#     if config["algorithm"].lower() == "bowtie":
#         res = static_bowtie(mix_pool, config, e)
#         # mng.hybrid_mixnet(mixnet, args.batch_threshold, args.binpack_solver, e)
#     elif config["algorithm"].lower() == "bwrand":
#         res = static_bwrand()
#         # mng.mix_select(args.select_mode, mixnet, args.batch_threshold)
#         # mng.mix_place(args.place_mode, mixnet, args.batch_threshold, args.binpack_solver) # bp_method: ffd, wfd, bfd, lp
#     elif config["algorithm"].lower() == "randrand":
#         res = static_randrand()
#     elif config["algorithm"].lower() == "randbp":
#         res = static_randbp()
#     else:
#         print("Incorrect algorithm.")
#         exit()
#     q.put(res)
#     return res

# def listener(q, config):
#     """listens for messages on the q, writes to file"""

#     print('.'*10 + 'listening' + '.'*10)
#     with open(os.path.join(config["log_dir"], '{0}_{1}_log.csv'.\
#                             format(config["algorithm"],
#                             config["network"]["setting"])), 'a') as attackfile,open(os.path.join(config["log_dir"], '{0}_{1}_time.csv'.\
#                             format(config["algorithm"],
#                             config["network"]["setting"])), 'a', newline='') as timefile:
#         while True:
#             logs = q.get()
#             if logs == 'kill':
#                 print('Listener has been killed...')
#                 break
#             else:
#                 print("+++++++++++++++++++++++++++++++++++++++++++")
#                 print(logs)
#                 print("+++++++++++++++++++++++++++++++++++++++++++")
#                 atk_log = logs[0]
#                 lay_log = logs[1]
#                 time_log = logs[2]
#                 num_mal = logs[3]
#                 current_epoch = logs[4]
#                 at_writer = csv.writer(attackfile)
#                 at_writer.writerows(atk_log)
#                 t_writer = csv.writer(timefile)
#                 t_writer.writerow(time_log)
#                 assert (len(logs[1]) >= 2)

#                  # write layout file
#                 path = os.path.join(config["log_dir"], "{0}_{1}_layout.csv".format(config["algorithm"], config["network"]["setting"]))
#                 df_layout = pd.read_csv(path)

#                 # provided that their lengths match
#                 df_layout.insert(loc=current_epoch+3, column='epoch_{}'.format(current_epoch), value=lay_log)

#                 df_layout.to_csv(path, index=False)

#                 # layout_data = {}
#                 # num_mix = len(mix_pool)
#                 # for idx, layout_col in enumerate(lay_log):
#                 #     if len(layout_col) < num_mix:
#                 #         layout_col.extend([-2]*(num_mix-len(layout_col)))
#                 #     layout_data["epoch_{}".format(idx)] = layout_col
#                 # df = pd.DataFrame(layout_data)
                
#                 # # add columns of mix_id, bw, and malicious
#                 # df.insert(loc=0, column='mix_id', value=[i for i in range(num_mix)])
#                 # bws  = [0] * num_mix # nodes that are not existed
#                 # mals = [False] * num_mix
#                 # for m in mix_pool:
#                 #     bws[m.mix_id] = m.bandwidth
#                 #     mals[m.mix_id] = m.malicious
#                 # df.insert(loc=1, column='bandwidth', value=bws)
#                 # df.insert(loc=2, column='malicious', value=mals)
                
#                 # path = os.path.join(config["log_dir"], "{0}_{1}_layout.csv".format(config["algorithm"], config["network"]["setting"]))
#                 # df.to_csv(path, index=False)



               


# def run(algorithm):
#     # use Manager queue
#     manager  = mp.Manager()
#     q        = manager.Queue()

#     with open('test_config.json') as json_file:
#         config = json.load(json_file)

#     # remove the old log directory and create the new directory
#     benign_mixes_dir = "../Benign_Mixes"
#     benign_mixes_num = 1000
#     log_dir = os.path.join("../integration_test/logs", algorithm+"_"+config["network"]["setting"])
#     config["log_dir"] = log_dir
#     config["benign_mixes_num"] = benign_mixes_num
#     config["algorithm"] = algorithm
#     if not os.path.exists(log_dir):
#         print(">>> Create new log directory.")
#         os.makedirs(log_dir)
#     else:
#         try: # remove the whole directory
#             files = glob.glob(log_dir)
#             for f in files:
#                 os.remove(f)
#             print(">>> Remove old log files.")
#         except:
#             pass
    
#     with mp.Pool(processes=config["num_processes"]) as pool:
#         # Put listener to work first
#         watcher = pool.apply_async(listener, (q, config))
#         # TODO: edit listener()

#         #fire off workers
#         jobs = []
#         # if args.fixed.lower() == 'yes':
#         # for nm in range(1, args.mal_num):# for quantity adv, mal_num represents mal_bw 1-15
#             # print(f'---start num_mal = {nm} simulation---')
#         # mix_pool = mg.gen_mixes(args.adv_type, nm, args.benign_mixes_dir, \
#         #                         args.benign_num, args.mal_bw_frac)
#         # 1. generate mixes
#         mix_pool = mg.gen_mixes("naive", 
#                 config["adversary"]["num_malicious_nodes"], 
#                 benign_mixes_dir,
#                 config["benign_mixes_num"], 
#                 config["adversary"]["bw_fraction"])
                    
#         output.create_log_csv(config) # create log files with header for later appendix
#         # output.write_all_mix(args, nm, mix_pool)
#         output.create_layout_csv(config, mix_pool)

#         for e in range(config["epoch_num"]):
#             print(f'>>>---start e = {e} enumeration---')

#             job = pool.apply_async(static_simulation, (mix_pool, config, e, q))
#             jobs.append(job)

#         #collect results from the workers through the pool result queue
#         for job in jobs:
#             job.get()

#         #now we are done, kill the listenser
#         q.put('kill')
#         pool.close()
#         pool.join()

def static_simulation(algorithm):
    with open('config_template.json') as json_file:
        config = json.load(json_file)

    # remove the old log directory and create the new directory
    benign_mixes_dir = "../Benign_Mixes"
    benign_mixes_num = 1000
    log_dir = os.path.join("../integration_test/logs", algorithm+"_"+config["network"]["setting"])
    config["log_dir"] = log_dir
    config["benign_mixes_num"] = benign_mixes_num
    config["algorithm"] = algorithm
    config["network"]["setting"] = "static"
    if not os.path.exists(log_dir):
        print(">>> Create new log directory.")
        os.makedirs(log_dir)
    else:
        try: # remove the whole directory
            files = glob.glob(log_dir)
            for f in files:
                os.remove(f)
            print(">>> Remove old log files.")
        except:
            pass

    mix_pool = mg.gen_mixes("naive", 
        config["adversary"]["num_malicious_nodes"], 
        benign_mixes_dir,
        config["benign_mixes_num"], 
        config["adversary"]["bw_fraction"])

    if config["algorithm"].lower() == "bowtie":
        config["adversary"]["num_malicious_nodes"] = 20 #TODO: set the best
        config["network"]["guard"]["enabled"] = True
        static_bowtie(mix_pool, config)
        # mng.hybrid_mixnet(mixnet, args.batch_threshold, args.binpack_solver, e)
    elif config["algorithm"].lower() == "bwrand":
        config["adversary"]["num_malicious_nodes"] = 20 #TODO: set the best 
        static_bwrand(mix_pool, config)
        # mng.mix_select(args.select_mode, mixnet, args.batch_threshold)
        # mng.mix_place(args.place_mode, mixnet, args.batch_threshold, args.binpack_solver) # bp_method: ffd, wfd, bfd, lp
    elif config["algorithm"].lower() == "randrand":
        config["adversary"]["num_malicious_nodes"] = 20 #TODO: set the best 
        static_randrand(mix_pool, config)
    elif config["algorithm"].lower() == "randbp":
        config["adversary"]["num_malicious_nodes"] = 20 #TODO: set the best 
        static_randbp(mix_pool, config)
    else:
        print("Incorrect algorithm.")
        exit()
    
        
