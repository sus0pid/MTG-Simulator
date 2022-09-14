import sys
sys.path.append("../simulation")
from dynamic_simulator import *
from static_simulator import *
# sys.path.append("../utilities")
# sys.path.append("../constructions")

dynamic_simulation("bwrand")
static_simulation("bwrand")

dynamic_simulation("bowtie")
static_simulation("bowtie") # TODO: a bug in ouput file: two extra 0s in bad_bw_l0 & bad_bw_l1

dynamic_simulation("randrand")
static_simulation("randrand")

dynamic_simulation("randbp")
static_simulation("randbp")