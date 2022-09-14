BENIGN_DIR=../Benign_Mixes
BENIGN_NUM=100
SELECT_MODE=hyper
PLACE_MODE=hyper
MAL_FRAC=0.2
OUTPUT_DIR=results/test_temp
EPOCH_NUM=4
PROCESSES=4
MAL_NUM=60
ADV_TYPE=naive
BP_SOLVER=lp
FIXED=yes
B_THRESHOLD=0.75
SETTING=dynamic
MAX_ROW=2000


# for BP_SOLVER in ffd wfd bfd lp; do
    # for B_THRESHOLD in $(seq 0.65 0.1 0.7)
    # for MAL_NUM in $(seq 3 1 3)
    # do
        # mkdir $OUTPUT_DIR
        python3 ../simulation/shrink_simulator.py --benign_mixes_dir $BENIGN_DIR --select_mode $SELECT_MODE --place_mode $PLACE_MODE --mal_bw_frac $MAL_FRAC --benign_num $BENIGN_NUM --batch_threshold $B_THRESHOLD --output_dir $OUTPUT_DIR --binpack_solver $BP_SOLVER --epoch_num $EPOCH_NUM --processes $PROCESSES --adv_type $ADV_TYPE --mal_num $MAL_NUM --fixed $FIXED --setting $SETTING --max_row_num $MAX_ROW
        # echo "......Bp_solver: $BP_SOLVER......"
        # echo "========Batch_threshold: $B_THRESHOLD========"
        # echo "......is_Fixed: $FIXED......"
        echo "========WHOLE SIMULATION ENDS========"
    # done
# done
