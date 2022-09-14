import sys
sys.path.append("../classes")
sys.path.append("../simulation")
from dynamic_simulator import *
from static_simulator import *
from tee import Tee
import os
# sys.path.append("../utilities")
# sys.path.append("../constructions")

if not os.path.exists("logs/"):
        print(">>> Create new log directory.")
        os.makedirs("logs/")

f = open('logs/console_log.txt', 'w')
original = sys.stdout
sys.stdout = Tee(sys.stdout, f)

print('\n'+"*"*50)
print(">>>Running the examples of algorithm_1: bwrand...")
print("*"*50+'\n')
dynamic_simulation("bwrand")
print(">>>bwrand dynamic runs successfully!\n")
static_simulation("bwrand")
print(">>>bwrand static runs successfully!\n")


print('\n'+"*"*50)
print(">>>Running the examples of algorithm_2: bowtie...")
print("*"*50+'\n')
dynamic_simulation("bowtie")
print(">>>bowtie dynamic runs successfully!\n")
static_simulation("bowtie")
print(">>>bowtie static runs successfully!\n")


print('\n'+"*"*50)
print(">>>Running the examples of algorithm_3: randrand...")
print("*"*50+'\n')
dynamic_simulation("randrand")
print(">>>randrand dynamic runs successfully\n")
static_simulation("randrand")
print(">>>randrand runs successfully!\n")


print('\n'+"*"*50)
print(">>>Running the examples of algorithm_4: randbp...")
print("*"*50+'\n')
dynamic_simulation("randbp")
print(">>>randbp dynamic runs successfullt!\n")
static_simulation("randbp")
print(">>>randbp static runs successfully!\n")
