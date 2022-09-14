from mix import Mix
import sumup


class Mixnet():
    """
    mixnet:
            parameters: 
                    mix_pool: list of all available mixes
                    mix_selected: list of selected mixes
                    mix_net: a dict of 3 layer-mixes

            functions:
                    selection()
                    placement()
    """

    def __init__(self, mix_pool=[], total_bw=0, num_benign=0, guard=False):
        self.mix_pool = mix_pool
        self.guard_pool = []  # general guards
        self.mix_select = []
        self.mix_net = {
            'layer0': [],
            'layer1': [],
            'layer2': []
        }
        self.total_bw = total_bw  # total bw of all online mixes
        self.num_benign = num_benign
        self.bad_num = []  # number of bad nodes in each layer
        self.bad_bw = []  # sum of bad bandwidth in each layer
        self.layer_num = []  # number of nodes in each layer
        self.layer_bw = []  # sum of bandwidth in each layer
        self.layer_index = []  # layer index for each nodes in mix_select
        self.guard = guard
        self.is_dirty = True

        self.GG_set = {
            'AG': [],
            'BG': [],
            'DG': []
        }

    def disp_mixnet(self):
        print('----------MIX NETWORK START----------')
        for layer, mixes in self.mix_net.items():
            print(f'*****{layer}*****')
            print(f'total bw of {layer}: {sumup.sum_mix_bw(mixes)}')
            print(f'number of mixes: {len(mixes)}')
            for m in mixes:
                print(m)
        print('----------MIX NETWORK END----------')

    def disp_mix_select(self, batch_threshold):
        print('----------SELECT MIXES START----------')
        print(
            f'total bw of selected mixes: {sumup.sum_mix_bw(self.mix_select)} MiB/s')
        print(
            f'selection batch threshold: {self.total_bw * batch_threshold} MiB/s')
        print(f'number of selected mixes: {len(self.mix_select)}')
        print(
            f'number of selected malicious mixes: {len(list(filter(lambda m: m.malicious==True, self.mix_select)))}')

        for m in self.mix_select:
            print(m)
        print('----------SELECT MIXES END----------')

    def disp_mix_pool(self, mal_bw_frac):
        print('----------MIX POOL START----------')
        print(f'total number of mixes: {len(self.mix_pool)}')
        # print(f'total bw of all mixes: {self.total_bw} MiB/s')
        # print(f'malicious bw: {self.total_bw * mal_bw_frac} MiB/s')

        print('mix_id,\tbandwidth,\tmalicious,\tonline')
        for m in self.mix_pool:
            print(m)
        print('----------MIX POOL END----------')

    def get_active_mix(self):
        # return [m for m in self.mix_pool if m.online and not m.malicious]
        return [m for m in self.mix_pool if m.online]

    def get_down_mix(self):
        return [m for m in self.mix_pool if not m.online]

    def get_online_counts(self):
        return len([m for m in self.mix_pool if m.online])

    def get_offline_counts(self):
        return len([m for m in self.mix_pool if not m.online])

    def refresh_total_bw(self):
        self.total_bw = sumup.sum_mix_bw([m for m in self.mix_pool if m.online])

    def check_id(self):
        ids = [m.mix_id for m in self.mix_pool]
        assert (len(set(ids)) == len(self.mix_pool))

    def update_mix_stab(self, current_epoch):
        for m in self.mix_pool:
            m.update_stability(current_epoch)

    def disp_mix_stab(self):
        print('mix_id,\tbandwidth,\tmalicious,\tonline,\tif_GG,\tAGT,\tstab,\tuptime,\tpt,\tdown,\tkt')
        for m in self.mix_pool:
            print(m)

    def disp_mix_states(self):
        print('mix_id, \tstates, \t\tstab')
        for m in self.mix_pool:
            print(f'{m.mix_id}, \t{m.states}, \t\t{m.stab}')
