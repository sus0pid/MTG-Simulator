import sys
sys.path.append("../constructions")
import mix_gen as mg
import os
import json
import glob
from bowtie import *
from bwrand import *
from randrand import *
from randbp import *
from datetime import datetime

def static_simulation(algorithm):
    print(f">>>Generating stratified mixnet using {algorithm} (without network churn)...")
    now = datetime.now()
    print(f">>>{now.strftime('%d-%m-%Y %H:%M:%S')}")
    with open('config_template.json') as json_file:
        config = json.load(json_file)
    
    # reset the config file of this simulation test
    benign_mixes_dir = "../Benign_Mixes"
    config["benign_mixes_num"] = 1000
    config["algorithm"] = algorithm
    config["network"]["setting"] = "static"
    log_dir = os.path.join("../integration_test/logs", algorithm+"_"+config["network"]["setting"])
    config["log_dir"] = log_dir

    if not os.path.exists(log_dir):
        print(">>> Create new log directory.")
        os.makedirs(log_dir)
    else:
        try: # empty the whole directory
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
        config["adversary"]["num_malicious_nodes"] = 110
        config["network"]["guard"]["enabled"] = True
        static_bowtie(mix_pool, config)
        # mng.hybrid_mixnet(mixnet, args.batch_threshold, args.binpack_solver, e)
    elif config["algorithm"].lower() == "bwrand":
        config["adversary"]["num_malicious_nodes"] = 32
        config["network"]["guard"]["enabled"] = False
        static_bwrand(mix_pool, config)
        # mng.mix_select(args.select_mode, mixnet, args.batch_threshold)
        # mng.mix_place(args.place_mode, mixnet, args.batch_threshold, args.binpack_solver) # bp_method: ffd, wfd, bfd, lp
    elif config["algorithm"].lower() == "randrand":
        config["adversary"]["num_malicious_nodes"] = 192
        config["network"]["guard"]["enabled"] = False
        static_randrand(mix_pool, config)
    elif config["algorithm"].lower() == "randbp":
        config["adversary"]["num_malicious_nodes"] = 194
        config["network"]["guard"]["enabled"] = False
        static_randbp(mix_pool, config)
    else:
        print("Incorrect algorithm.")
        exit()
    
        
