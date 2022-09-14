DEFAULT_WINDOW_LEN = 15
class Mix:
    def __init__(self, mix_id, bandwidth, sk, malicious = False, epoch_of_birth=0):
        self.mix_id = mix_id # int
        self.bandwidth = bandwidth # float
        self.malicious = malicious
        self.sk        = sk # int
        self.online    = True # all nodes are supposed to be online when it join the network
        
        self.down_edge = 0 # number of times going down
        self.perst     = 0 # persistence of each node
        self.AGT       = 0 # number of epochs for AG
        self.uptime    = 0 # uptime since KnownTime (the first time joining the network)
        self.stab      = 0

        self.known_time = epoch_of_birth # the epoch when the node joins network
        self.guard_time = None # the epoch when the node becomes a guard
        self.GG        = False # whether is a GG
        self.AG        = False # whether active Guard

        self.states    = [] # record the on/off status of nodes
        self.norm_stab = 0

        self.GG_times  = 0 # track how many times a node has been a GG

    def __str__(self):
        on_off = "--" if self.online else self.online
        ho_mal = "--" if not self.malicious else self.malicious
        if_GG  = '--' if not self.GG else self.GG
        return f'{self.mix_id},\t{round(self.bandwidth, 2)},\t{ho_mal},\t{on_off},\t{if_GG},\t{self.AGT},\t{round(self.stab, 2)},\t{self.uptime}\t{self.perst},\t{self.down_edge},\t{self.known_time}'
    
    def go_down(self):
        self.online = False
        self.down_edge += 1
        # if self.GG:
        #     self.AGTS.append(self.AGT)
        #     self.AGT = 0

    def go_back(self):
        self.online = True

    def as_GG(self, epoch_of_guard): # as an general guard, only do this once
        self.GG = True
        self.guard_time = epoch_of_guard # time when first becomming a guard
        self.GG_times += 1
 
    def no_more_GG(self):
        self.GG = False
    
    def as_AG(self): # as an active guard, do this in each epoch to track the AGT
        # self.AG = True # no chance to remove AG label so leave this
        if self.AGT == None:
            self.AGT = 1
        else:
            self.AGT += 1

    def update_stability(self, current_epoch): # (uptime, persistent, down_edge)
        if self.online:
            self.uptime += 1
            self.perst  += 1
            self.states.append(1)
        else:
            self.perst  += -1
            self.states.append(-1)
        if len(self.states) > DEFAULT_WINDOW_LEN:
            self.states.pop(0)

        # calculate stability = (uptime+pert)/(down+1)
        # self.stab = (self.uptime + self.perst) / (self.down_edge + 1)
        # self.stab = 2 ** (self.perst - self.down_edge) * self.uptime / \
        #             (current_epoch - self.known_time + 1)
        # self.stab = (self.uptime + self.perst - 1.5*self.down_edge) / (current_epoch - self.known_time + 1)
        # w = a*i + b mono increasing function
        a, b = 1/2, 1/4
        if len(self.states) >= DEFAULT_WINDOW_LEN:
            ws = [a*i+b for i in range(DEFAULT_WINDOW_LEN)]
        else:
            ws = [a*i+b for i in range(len(self.states))]
        weights = [w/sum(ws) for w in ws] # scale weight to (0-1)

        self.stab = 0
        for s, w in zip(self.states, weights):
            self.stab += s*w
    
    def set_norm_stab(self, norm_stab):
        self.norm_stab = norm_stab






    