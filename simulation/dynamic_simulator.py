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
from datetime import datetime

def dynamic_simulation(algorithm):
    print(f">>>Generating stratified mixnet using {algorithm} with network churn...")
    now = datetime.now()
    print(f">>>{now.strftime('%d-%m-%Y %H:%M:%S')}")
    with open('config_template.json') as json_file:
        config = json.load(json_file)

    # remove the old log directory and create the new directory
    benign_mixes_dir = "../Benign_Mixes"
    config["benign_mixes_num"] = 1000
    config["algorithm"] = algorithm
    config["network"]["setting"] = "dynamic"
    log_dir = os.path.join("../integration_test/logs", algorithm+"_"+config["network"]["setting"])
    config["log_dir"] = log_dir

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

    # 1. generate mixes
    mix_pool = mg.gen_mixes("naive", 
                            config["adversary"]["num_malicious_nodes"], 
                            benign_mixes_dir,
                            config["benign_mixes_num"], 
                            config["adversary"]["bw_fraction"])

    # 2. construct mixnet using specified algorithm
    start = time.time()
    print(f">>> Simulation of {algorithm} construction.")
    if algorithm.lower() == "bowtie":
        config["adversary"]["num_malicious_nodes"] = 110
        config["network"]["guard"]["enabled"] = True
        dynamic_bowtie(mix_pool, config)
    elif algorithm.lower() == "bwrand":
        config["adversary"]["num_malicious_nodes"] = 32
        config["network"]["guard"]["enabled"] = False
        dynamic_bwrand(mix_pool, config)
    elif algorithm.lower() == "randrand":
        config["adversary"]["num_malicious_nodes"] = 192
        config["network"]["guard"]["enabled"] = False
        dynamic_randrand(mix_pool, config)
    elif algorithm.lower() == "randbp":
        config["adversary"]["num_malicious_nodes"] = 194
        config["network"]["guard"]["enabled"] = False
        dynamic_randbp(mix_pool, config)
    else:
        print("The algorithm does not match!")
    end = time.time() - start


# if __name__ == "__main__":
#     # # run()
#     # args = parser.parse_args()
#     # print(args)
#     # churn_rate = {
#     #     "leave_rate": 0.15,
#     #     "back_rate": 0.12,
#     #     "new_good_rate": 0,
#     #     "new_bad_rate": 0,
#     #     "guard_elim_stab_thresh": 0.1,
#     #     "eliminate_interval": 2
#     # }
#     # # "leave_rate": 0.015,
#     # # "back_rate": 0.012,
#     # # "new_good_rate": 0.003,
#     # # "new_bad_rate": 0.001
#     # # for leave_rate in [0.015, 0.03, 0.05, 0.075, 0.1, 0.125, 0.15]:

#     # for leave_rate in [0.075]:
#     #     churn_rate["leave_rate"] = leave_rate
#     #     churn_rate["back_rate"] = leave_rate * 0.9
#     #     churn_rate["new_good_rate"] = leave_rate * 0.1
#     #     churn_rate["new_bad_rate"] = leave_rate * 0.02
#     dynamic_simulation("randbp")
        
