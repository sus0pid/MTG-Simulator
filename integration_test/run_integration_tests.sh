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

echo "MTG Simulator: running examples"
echo ""

python3 MTG_test.py || exit 1
# python3 test_scripts/test_2_RandRand.py || exit
# python3 test_scripts/test_3_RandBP.py || exit 1
# python3 test_scripts/test_4_BowTie.py || exit 1
echo ""
echo "MTG Simulator: All examples run successfully!"

