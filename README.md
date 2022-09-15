# MTG (Mixnet Topology Generator)

## Introduction
This is the simulator for simulating mixnet topological construction algorithms.
We implemented a scalable Mixnet construction model with the four mixnet construction 
algorithms (i.e., bwrand, randrand, randbp, and bowtie) in Python. We use Gurobi 
optimizer to solve the linear bin-packing 
optimization problem.

The bandwidths of Mixnodes are generated by fitting to the bandwidth distribution of 
Tor relays from its historical data. We used a R package 
to fit the 
bandwidth data captured from [Tor](https://metrics.torproject.org/rs.html#search) consensus documents and server descriptors 
from January 2021 to March 2021.
Among three common right-skewed distributions
we choose the gamma distribution as the best-fitted via maximum 
likelihood estimation (MLE) method. Given the number of mixes, MTG can generate a pool of mix nodes in any size. In order to show the comparison between four algorithms, we run the simulator with the same set of benign mix nodes (i.e., data from `Benign_Mixes/1000_benignmix.csv`).

## Technical goal
The objective of this tool is to generate the mixnet topologies assuming a strategic adversary who has a fixed budget to operate mixnodes with different construction algorithm. The generated topological configuration is determined by the construction algorithm, clearly showing the position of each mixnodes in every epoch. The detailed topological configuration data is stored in `logs/xxx_layout.csv`

The adversary can deanonymise all messages travel through a path that is composed of all malicious mixes. Thus, the security of the generated network is evaluated by the fraction of total paths in the network topology that are fully compromised (i.e., comprosed entirely of the adversarial relays). This metric is shown in the output log file (`attack_profit` in `logs/xxx_log.csv`).


## Getting started

1. Prerequisite:
    - Python version 3.7+
    - Recent linux/unix operating system (e.g., Ubuntu 20.04 or Mac os 12+)
2. Install [Gurobi](https://www.gurobi.com/academia/academic-program-and-licenses/)
    1. download [Gurobi Optimizer](https://www.gurobi.com/downloads/)
    2. After downloading, follow the instructions in README.txt to install the software.
    3. Once installed, visit the [Free Academic License](https://www.gurobi.com/downloads/end-user-license-agreement-academic/) page to request the free license.
    4. Next, run grbgetkey using the argument provided on the Academic License Detail page (ex: grbgetkey ae36ac20-16e6-acd2-f242-4da6e765fa0a). 
   
   See [Other Installation Methods](https://www.gurobi.com/academia/academic-program-and-licenses/) if
    you're using other licenses.
   
   <!-- python -m pip install gurobipy -->
3. Install dependencies
    ```bash
    bash mtg_install_dependencies.sh
    ```
4. Run examples:
    ```bash
    cd integration_test
    bash run_integration_test.sh
    ```
    Here, four mixnet topological construction algorithms are used to generate mixnet topologies in a dynamic and static setting seperately; the results are saved under the directory of `./integration_test/logs/*algorithm*_dynamic/`. We consider the natural network churn in the dynamic setting (i.e., realistic case), while mixes are assumed to be always online in the static setting (i.e., ideal case). The output of the console is redirected to the text file `./integration_test/logs/console_log.txt`. 

## An example & results

### Example of bowtie topological construction algorithm with network churn
Here, we take *bowtie* in a *static* setting as an example to illustrate the specific details.
After calling the following function in `MTG_test.py`
```bash
dynamic_simulation("bowtie")
```
, MTG generator will simulate the configuration process for *epoch_num* (see `./integration_test/config_template.json`) epochs.
The programing runtime can be reduced with fewer epochs (we have *epoch_num*=20 in the examples). 

Another important parameter in `config_template.json` file is `construction:sample_fraction` that indicates the relative size of mixes' bandwidth being selected into mixnet from mix pool. 

`adversary:bw_fraction` is also important as it sets the bandwidth budget of malicious mixes that the adversary could control/corrupt.

### Output 1: Generated topologies
There are three csv files generated with the path `./integration_test/logs/bowtie_dynamic`. First, we illustrate the file that describes the detailed topologies of mixnet.

`bowtie_dynamic_layout.csv` records the specific topologies of each mix node during every epoch. We use four digits to represent the position of each mix: -1: mix was not in the network, 0/1/2: mix was assigned to layer 0/1/2. Note that ***routsim*** takes this file as the input and evaluate the client's privacy overtime based on the topologies of each epoch.

### Output 2: End-to-end compromised fraction
Under the same directory, `bowtie_dynamic_log.csv` shows the information of the mixnet during each epoch and the definition of important column is listed below:

    | Column_name       | Description |
    | :------           |:------------|
    | num_malicious     |number of malicious mixes |
    | mal_frac          |fraction of malicious bandwidth|
    |batch_th           |sampling fraction|
    |total_bw           |total bandwidth of mix pool|
    |num_bad_l0/guard/l2|number of malicious mix in layer0/1/2|
    |num_lay_l0/guard/l2|number of mixes in layer0/1/2|
    |bad_bw_l0/guard/l2 |sum of bandwidth of malicious mixes in layer0/1/2|
    |lay_bw_l0/guard/l2 |bandwidth of layer0/1/2|
    |bw_frac_l0/guard/l2|fraction of total_bw|
    |attack_profit      |end-to-end compromised fraction of paths|
    |attack_succ        |whether the adversary controls at least one end-to-end path|

    Note that the `attack_profit` is one of our security metric in section 6.2.2.

<!-- - `bowtie_dynamic_onoff.csv`: this file is mainly for tracking the online/offline status of each mix node. -->

### Output 3: Guessing entropy
Guessing entropy, another security metric in section 6.2.3, can be calculated based on the generated topologies in `bowtie_dynamic_layout.csv`. To achieve this, run the following command in your terminal:
```bash
cd metrics
python3 guessing_entropy.py --topology "../integration_test/logs/bowtie_dynamic/bowtie_dynamic_layout.csv"
```
The results show the average guessing entropy over several epochs, along with the sepecific guessing entropy for each epoch.

### Output 4: Expected queuing delay
We also evaluate the expected queuing delay in section 6.2.4, as the performance metric for the topologies generated by different algorithms. To calculate it, run the following command in your terminal:
```bash
cd metrics
python3 proc_waiting_time.py --l 1000 --path "../integration_test/logs/randrand_dynamic/randrand_dynamic_layout.csv"
```
The results show the average queuing delay over several epochs, along with the specific queuing delay for each epoch.





