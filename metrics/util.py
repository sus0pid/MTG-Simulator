import csv

def parse_topology(topo_path):
    """
    parse file containing information
    mix_id,bandwidth,malicious,layer

    outputs a dict {'config0':{'layer':{'mix_id':[bandwidth, malicious]},
    'config1': {...}, ..., 'configN':{...}}}

    """
    topology = {'epoch_0': {'-1':{}, '0':{}, '1':{}, '2':{}}}
    with open(topo_path) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'layer' in row:
                topology['epoch_0'][row['layer']][row['mix_id']] = [float(row['bandwidth']),\
                                                     row['malicious']]
            elif 'epoch_0' in row:
                #parse configs
                i = 0
                while 'epoch_'+str(i) in row:
                    if 'epoch_'+str(i) not in topology:
                        topology['epoch_'+str(i)] = {'-1':{}, '0':{}, '1':{}, '2':{}}
                    topology['epoch_'+str(i)][row['epoch_'+str(i)]][row['mix_id']] = [float(row['bandwidth']), row['malicious']]
                    i+=1
    return topology
