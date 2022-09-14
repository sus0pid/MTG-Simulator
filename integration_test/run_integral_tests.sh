# Test: 
#     Static Setting: 
#		1) BwRand, 
#		2) RandRand, 
#		3) RandBP,
#		4) BowTie;
#     Dynamic Setting:
#		1) BwRand,
#		2) RandRand,
#		3) RandBP,
#		4) BowTie.
# Adversary: naive
# Mal_fraction: 0.2
# Epoch_Num: 100 
# Parallel: true for static; false for dynamic
# processors: 4
# Bp_solver: LP
# output_dir: recoded (different test writes to different directory)
# batch threshold: 0.75

python3 test_1_static_BwRand.py || exit 1
python3 test_2_static_RandRand.py || exit
python3 test_3_static_RandBP.py || exit 1
python3 test_4_static_BowTie.py || exit 1
python3 test_5_dynamic_BwRand.py || exit 1
python3 test_6_dynamic_RandRand.py || exit 1
python3 test_7_dynamic_RandBP.py || exit 1
python3 test_8_dynamic_BowTie.py || exit 1
