import argparse
from util import parse_topology
import pprint

parser = argparse.ArgumentParser(description="Computes how many nodes the\
                                 adversary requires to sequentially compromise to deanonymize\
                                 a message, on average")

parser.add_argument("--topology", help="path to the topology file containing\
                    the mix network")


def compute_guessing_entropy(topology):
    """
    This selection process corresponds to a monotonic strategy in which the
    adversary compromises mixes one after the other, looks then for the best
    choice based on mixes already compromised, and does so until the attack
    succeeds.

    This captures a worst-case scenario in which a given attacker invests into
    hacking as many nodes as required until he successfully deanonymize a given
    target, on average

    """
    j = 0
    guessing_entropies = {}
    while 'epoch_'+str(j) in topology:
        print("Computing for epoch"+str(j))
        layer0 = [x[0] for x in topology['epoch_'+str(j)]['0'].values()]
        layer0.sort()
        layer1 = [x[0] for x in topology['epoch_'+str(j)]['1'].values()]
        layer1.sort()
        layer2 = [x[0] for x in topology['epoch_'+str(j)]['2'].values()]
        layer2.sort()
        layer0_tot = sum(layer0)
        layer1_tot = sum(layer1)
        layer2_tot = sum(layer2)
        # calculate the bandwidth weight for each node
        pr_layer0 = [x/layer0_tot for x in layer0]
        pr_layer1 = [x/layer1_tot for x in layer1]
        pr_layer2 = [x/layer2_tot for x in layer2]

        guessing_entropy = 0
        pr_layer0_cumul = {'cumul': pr_layer0.pop()}
        pr_layer1_cumul = {'cumul': pr_layer1.pop()}
        pr_layer2_cumul = {'cumul': pr_layer2.pop()}
        print(f'pr_layer0_cumul:{pr_layer0_cumul}, \npr_layer1_cumul:{pr_layer1_cumul}, \npr_layer2_cumul:{pr_layer2_cumul}')
        print("Computing Guessing Entropy. Layer 0 has {0} nodes, layer 1 has {1} nodes, layer 2 has {2} nodes".format(len(layer0), len(layer1), len(layer2)))
        for i in range(3, len(layer0)+len(layer1)+len(layer2)):

            max_pr_layer0 = pr_layer0[-1] if len(pr_layer0) > 0 else 0
            max_pr_layer1 = pr_layer1[-1] if len(pr_layer1) > 0 else 0
            max_pr_layer2 = pr_layer2[-1] if len(pr_layer2) > 0 else 0
            # print(f'max_pr_layer0:{max_pr_layer0}, \nmax_pr_layer1:{max_pr_layer1}, \nmax_pr_layer2:{max_pr_layer2}')

            max_pr_layer = pr_layer0
            tmp_pr_cumul_a = pr_layer1_cumul
            tmp_pr_cumul_b = pr_layer2_cumul
            tmp_cumul_layer = pr_layer0_cumul
            if  max_pr_layer0 <= max_pr_layer1:
                max_pr_layer = pr_layer1
                tmp_pr_cumul_a = pr_layer0_cumul
                tmp_pr_cumul_b = pr_layer2_cumul
                tmp_cumul_layer = pr_layer1_cumul
                if max_pr_layer1 <= max_pr_layer2:
                    max_pr_layer = pr_layer2
                    tmp_pr_cumul_a = pr_layer0_cumul
                    tmp_pr_cumul_b = pr_layer1_cumul
                    tmp_cumul_layer = pr_layer2_cumul
                    print("this turn max_pr in layer2")
                else:
                    print("this turn max_pr in layer1")
            elif max_pr_layer0 <=  max_pr_layer2:
                max_pr_layer = pr_layer2
                tmp_pr_cumul_a = pr_layer0_cumul
                tmp_pr_cumul_b = pr_layer1_cumul
                tmp_cumul_layer = pr_layer2_cumul
                print("this turn max_pr in layer2")
            else:
                print("this turn max_pr in layer0")

            pr_ith_compromised_node = max_pr_layer.pop()
            guessing_entropy += (i+1)*pr_ith_compromised_node*tmp_pr_cumul_a['cumul']*tmp_pr_cumul_b['cumul']
            tmp_cumul_layer['cumul'] += pr_ith_compromised_node
            # print(f'pr_layer0_cumul:{pr_layer0_cumul}, \npr_layer1_cumul:{pr_layer1_cumul}, \npr_layer2_cumul:{pr_layer2_cumul}')
            # print(f'-----i = {i}-----')

        print("This topology requires {0} compromised nodes to succeeds at deanonymizing a message, on average".format(guessing_entropy))
        guessing_entropies['epoch_'+str(j)] = guessing_entropy
        j+=1
    return guessing_entropies





if __name__ == "__main__":

    args = parser.parse_args()

    topology = parse_topology(args.topology)

    gentropies = compute_guessing_entropy(topology)
    print(gentropies)
