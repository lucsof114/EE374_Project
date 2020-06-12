import numpy as np
import matplotlib.pyplot as plt

def labelplt(x, y, beta, str1, str2, ry, rx ) : 
    # x values (list)
    # y values (list)
    # beta (list)
    # xlabel (string)
    # ylabel (string)
    # minx (int/float)
    # miny (int/float)
    for xs,ys,b in zip(x,y,beta): 
        plt.annotate(r'$\beta$: ' + str(b), (xs,ys),
                 textcoords="offset points", # how to position the text
                 xytext=(0,10), # distance from text to points (x,y)
                 ha='center') # horizontal alignment can be left, right or center
        plt.plot(xs,ys, "r*")
    plt.xlim((rx, np.max(x) + 20))
    plt.xlabel(str1)
    plt.ylabel(str2)
    plt.ylim((ry, np.max(y) + 20))

    plt.show()

def plot(x, y1, y2, y3, l1, l2, l3, title, xl, yl, xmin, xmax, ymin, ymax, loc, svf):
    fig, ax = plt.subplots()

    # Using set_dashes() to modify dashing of an existing line
    line1, = ax.plot(x, y1, 'bo', dashes=[6, 2], label=l1)
    plt.xlabel(xl)
    plt.ylabel(yl)
    plt.xlim((xmin, xmax))
    plt.ylim((ymin, ymax))
    plt.title(title)
    #line1.set_dashes([2, 2, 10, 2])  # 2pt line, 2pt break, 10pt line, 2pt break

    # Using plot(..., dashes=...) to set the dashing when creating a line
    line2, = ax.plot(x, y2, 'ro', dashes=[6, 2], label=l2,)
    line3, = ax.plot(x, y3, 'go', dashes=[6, 2], label=l3,)

    ax.legend(loc=loc)
    plt.savefig(svf)

def vary_n():
    n_vals = [500, 1000, 1500, 2000, 4000, 7000, 10000]
    l1 = "Beta = 0"
    l2 = "Beta = 0.1"
    l3 = "Beta = 0.2"
    #pwr = n_vals / 100
    y1_throughput = [23.9272357271,  53.2248429901,  95.372481817,  113.907705284,  236.794848305,  424.14155015, 611.616]
    y2_throughput = [24.4430844735,  51.8189133958,  93.7532457967,  112.577048721,  234.110144015,  418.741932294, 612.9876]
    y3_throughput = [23.5134039504,  50.4943017463,  91.9905837088,  112.590186574,  239.735346739,  424.283118615, 607.4589]
    title_thru = "Elastico Throughput vs Size of Network (bpe = 50, c = 100)"
    yl_thru = "Throughput (TXs per second)"
    xl_thru = "Number of Nodes (100x mining rate)"
    plot(n_vals, y1_throughput, y2_throughput, y3_throughput, l1, l2, l3, title_thru, xl_thru, yl_thru, 0, 11000, 0, 700, 'lower right', 'one')

    y1_latency = [1.19431750426,  1.21999322756,  1.22220508486,  1.23088373824,  1.23495411738,  1.25218613204, 1.243]
    y2_latency = [1.4099739445,  1.46227068345,  1.48301892511,  1.54790991273,  1.59859782302,  1.57956471009, 1.604]
    y3_latency = [1.81701336312,  1.84078462207,  1.88524701037,  1.90540553201,  1.98923511351,  2.05782317287, 2.054]
    title_lat = "Elastico Latency vs Size of Network (bpe = 50, c = 100)"
    yl_lat = "Latency (seconds)"
    xl_lat = "Number of Nodes (100x mining rate)"
    plot(n_vals, y1_latency, y2_latency, y3_latency, l1, l2, l3, title_thru, xl_lat, yl_lat, 0, 11000, 0, 3, 'lower right', 'two')

    y1_comm = [22852.046,  39168.644,  41046.0053333,  44884.7695,  47732.01775,  48912.3865714, 49441.796]
    y2_comm = [20716.72,  35299.075,  37167.5273333,  40484.504,  43001.4125,  44092.6321429, 44567.7262]
    y3_comm = [17515.742,  31307.581,  33014.738,  36101.465,  38288.017,  39313.1842857, 39709.8979]
    for i in range(7):
        y2_comm[i] = y2_comm[i] / 0.9
        y3_comm[i] = y3_comm[i] / 0.8
    title_comm = "Elastico Communication vs Size of Network (bpe = 50, c = 100)"
    yl_comm = "Communication per Node (# of messages)"
    xl_comm = "Number of Nodes"
    plot(n_vals, y1_comm, y2_comm, y3_comm, l1, l2, l3, title_comm, xl_comm, yl_comm, 0, 11000, 10000, 50000, 'lower right', 'three')

    y1_down = [103.2,  181.95,  191.1,  209.1,  222.6375,  228.328571429, 230.75]
    y2_down = [103.5,  181.85,  191.466666667,  209.2,  222.55,  228.292857143, 230.74]
    y3_down = [101.5,  181.8,  191.233333333,  209.275,  222.3625,  228.314285714, 230.795]
    title_down = "Elastico Downloads vs Size of Network (bpe = 50, c = 100)"
    yl_down = "Downloads per node (# of blks downloaded)"
    xl_down = "Number of Nodes"
    plot(n_vals, y1_down, y2_down, y3_down, l1, l2, l3, title_down, xl_down, yl_down, 0, 11000, 0, 300, 'lower right', 'four')

def vary_c():
    c_vals = [50, 100, 200]
    l1 = "Beta = 0"
    l2 = "Beta = 0.1"
    l3 = "Beta = 0.2"

    y1_thru = [111.6, 52.2, 23.8]
    y2_thru = [110.4, 51.8, 23.6]
    y3_thru = [0, 53.5, 23.7]
    title_thru = "Elastico Throughput vs Shard Size (bpe = 50, n = 1000)"
    yl_thru = "Throughput (TXs per second)"
    xl_thru = "Shard Size"
    plot(c_vals, y1_thru, y2_thru, y3_thru, l1, l2, l3, title_thru, xl_thru, yl_thru, 0, 250, 0, 200, 'upper right', 'five')

    y1_lat = [1.22, 1.22, 1.21]
    y2_lat = [1.56, 1.51, 1.42]
    y3_lat = [99, 1.83, 1.73]
    title_lat = "Elastico Latency vs Shard Size (bpe = 50, n = 1000)"
    yl_lat = "Latency (seconds)"
    xl_lat = "Shard Size"
    plot(c_vals, y1_lat, y2_lat, y3_lat, l1, l2, l3, title_lat, xl_lat, yl_lat, 0, 250, 0, 3, 'upper right', 'six')

    y1_comm = [22651.6, 39251.5, 45557.0]
    y2_comm = [20435.7, 35472.3, 40519.6]
    y3_comm = [18169.8, 31232.1, 36822.7]
    for i in range(3):
        y2_comm[i] = y2_comm[i] / 0.9
        y3_comm[i] = y3_comm[i] / 0.8
    title_comm = "Elastico Communication vs Shard Size (bpe = 50, n = 1000)"
    yl_comm = "Communication per Node (# of messages)"
    xl_comm = "Shard Size"
    plot(c_vals, y1_comm, y2_comm, y3_comm, l1, l2, l3, title_comm, xl_comm, yl_comm, 0, 250, 0, 50000, 'lower right', 'seven')

def plot2(x1, y1, x2, y2, x3, y3, n_vals, l1, l2, l3, title, xmin, xmax, ymin, ymax, xl, yl, loc, svf):
    fig, ax = plt.subplots()

    # Using set_dashes() to modify dashing of an existing line
    line1, = ax.plot(x1, y1, 'bo', dashes=[6, 2], label=l1)
    plt.xlabel(xl)
    plt.ylabel(yl)
    plt.xlim((xmin, xmax))
    plt.ylim((ymin, ymax))
    words = ['n = 500', 'n = 1000', 'n = 1500', 'n = 2000', 'n = 4000', 'n = 7000', 'n = 10000']
    for i in range(len(x1)):
        ax.annotate(words[i], (x1[i],y1[i]), textcoords="offset points", xytext=(10,-4))
    plt.title(title)
    #line1.set_dashes([2, 2, 10, 2])  # 2pt line, 2pt break, 10pt line, 2pt break

    # Using plot(..., dashes=...) to set the dashing when creating a line
    line2, = ax.plot(x2, y2, 'ro', dashes=[6, 2], label=l2,)
    for i in range(len(x2)):
        ax.annotate(words[i], (x2[i],y2[i]), textcoords="offset points", xytext=(10,-4))
    line3, = ax.plot(x3, y3, 'go', dashes=[6, 2], label=l3,)
    for i in range(len(x3)):
        ax.annotate(words[i], (x3[i],y3[i]), textcoords="offset points", xytext=(10,-4))

    ax.legend(loc=loc)
    plt.savefig(svf)


def plot_lat_vs_thru():
    n_vals = [500, 1000, 1500, 2000, 4000, 7000, 10000]
    l1 = "Beta = 0"
    l2 = "Beta = 0.1"
    l3 = "Beta = 0.2"
    #pwr = n_vals / 100
    y1_throughput = [23.9272357271,  53.2248429901,  95.372481817,  113.907705284,  236.794848305,  424.14155015, 611.616]
    y2_throughput = [24.4430844735,  51.8189133958,  93.7532457967,  112.577048721,  234.110144015,  418.741932294, 612.9876]
    y3_throughput = [23.5134039504,  50.4943017463,  91.9905837088,  112.590186574,  239.735346739,  424.283118615, 607.4589]
    
    #title_thru = "Elastico Throughput vs Size of Network (bpe = 100, c = 100)"
    yl_thru = "Throughput (TXs per second)"
    xl_thru = "Number of Nodes"
    #plot(n_vals, y1_throughput, y2_throughput, y3_throughput, l1, l2, l3, title_thru, xl_thru, yl_thru, 0, 8000, 0, 500, 'lower right')

    y1_latency = [1.19431750426,  1.21999322756,  1.22220508486,  1.23088373824,  1.23495411738,  1.25218613204, 1.243]
    y2_latency = [1.4099739445,  1.46227068345,  1.48301892511,  1.54790991273,  1.59859782302,  1.57956471009, 1.604]
    y3_latency = [1.81701336312,  1.84078462207,  1.88524701037,  1.90540553201,  1.98923511351,  2.05782317287, 2.054]
    #title_lat = "Elastico Latency vs Size of Network (bpe = 100, c = 100)"
    yl_lat = "Latency (seconds)"
    xl_lat = "Number of Nodes"
    #plot(n_vals, y1_latency, y2_latency, y3_latency, l1, l2, l3, title_thru, xl_lat, yl_lat, 0, 8000, 0, 3, 'lower right')

    title = "Latency vs Throughput (bpe = 50, c = 100)"
    xl = "Latency (seconds)"
    yl = "Throughput (TXs per second)"

    plot2(y1_latency, y1_throughput, y2_latency, y2_throughput, y3_latency, y3_throughput, n_vals, l1, l2, l3, title, 1.1, 2.6, 0, 700, xl, yl, 'lower right', 'eight')

def main():
    vary_n()
    vary_c()
    plot_lat_vs_thru()

if __name__ == '__main__':
    main()

