"""
learn from hit rate statistics and decide the value of bandwidth
"""
import os
import pandas as pd
import pprint as pp
import matplotlib.pyplot as plt


def get_avg_hitrate():
    # data = pd.DataFrame(data={'bw': get_bw(), 'sum': [0]*1000})
    sum = [0] * 1000 
    for i in range(3, 150):
        # print('\n' + 10 * " > " + f'i = {i}' + 10 * " > ")
        dir1 = '~/OneDrive - University of Edinburgh/Downloads/Downloads/Bw/bwtrust/Hit'
        dir2 = '~/OneDrive - University of Edinburgh/Downloads/Downloads/Bw/bwbp/Hit'
        file1 = os.path.join(dir1, '1000_{}_Bw_Trust_hitrate.csv'.format(i))
        file2 = os.path.join(dir2, '1000_{}_Bw_BP_hitrate.csv'.format(i))

        h1 = pd.read_csv(file1).hit_rate.tolist()[:1000]
        h2 = pd.read_csv(file2).hit_rate.tolist()[:1000]
        avg = [(a+b)/2 for (a, b) in list(zip(h1, h2))]
        sum = [a+b for (a, b) in list(zip(avg, sum))]
    return [s/147/1000 for s in sum]
    
def get_bw():
    with open('Benign_Mixes/1000_benignmix.csv', 'r') as f:
        lines = f.readlines()
        bw = []
        for line in lines[1:]:
            vals = line.strip().split(',')
            bw.append(float(vals[1]))
        return bw

def draw_fig():

    # x axis values
    x = get_bw()
    # corresponding y axis values
    y = get_avg_hitrate()

    # plotting the points
    plt.plot(x, y, color='green', linestyle='dashed', linewidth = 1,
            marker='o', markerfacecolor='blue', markersize=5)


    # setting x and y axis range
    plt.ylim(0, 1)
    plt.xlim(0, 100)

    # naming the x axis
    plt.xlabel('bandwidth(MiB/s)')
    # naming the y axis
    plt.ylabel('hit-rate')

    # giving a title to my graph
    plt.title('Insights of bwSelection')

    # function to show the plot
    plt.show()
    # plt.savefig('figs/hitrate_bw')

if __name__ == '__main__':
    draw_fig()