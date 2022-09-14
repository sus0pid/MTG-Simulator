import sys
sys.path.append("../classes")
sys.path.append("../simulation")
from dynamic_simulator import *
from static_simulator import *
from tee import Tee
# sys.path.append("../utilities")
# sys.path.append("../constructions")

f = open('logs/console_log.txt', 'w')
original = sys.stdout
sys.stdout = Tee(sys.stdout, f)

print("*"*50)
print(">>>Running the example of algorithm_1: bwrand...")
dynamic_simulation("bwrand")
static_simulation("bwrand")

print("*"*50)
print(">>>Running the example of algorithm_2: bowtie...")
dynamic_simulation("bowtie")
static_simulation("bowtie")

print("*"*50)
print(">>>Running the example of algorithm_3: randrand...")
dynamic_simulation("randrand")
static_simulation("randrand")

print("*"*50)
print(">>>Running the example of algorithm_4: randbp...")
dynamic_simulation("randbp")
static_simulation("randbp")
