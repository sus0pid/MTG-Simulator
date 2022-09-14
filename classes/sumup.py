


def sum_mix_bw(mix_list):
    try:
        bw = [m.bandwidth for m in mix_list if m.online]
        return sum(bw)
    except TypeError as e:
        print(f'mix_list: {mix_list}')
        print(e)
        return 0
