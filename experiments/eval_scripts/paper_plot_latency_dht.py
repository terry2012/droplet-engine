import numpy as np
import os
import re
import math

import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

db_pattern = re.compile("local_dht_benchmark_k(.*)_a(.*)_n(.*)_l(.*).db")
FETCH_CLIENT_DATA = "SELECT time_store_chunk, time_fetch_addr + time_fetch_nonce + time_fetch_chunk " \
                    "FROM CLIENT_STORE_GET " \
                    "WHERE _rowid_>=? AND _rowid_<?;"

FETCH_ADDRESS_STORE = "SELECT time_crawl_nearest " \
                   "FROM ADD_CHUNK " \
                   "WHERE _rowid_>=? AND _rowid_<?;"

FETCH_ADDRESS_GET = "SELECT time_fetch_addr " \
                   "FROM CLIENT_STORE_GET " \
                   "WHERE _rowid_>=? AND _rowid_<?;"

data_path_s3 = "../data/local_s3_benchmark/local_s3_benchmark.db"

FETCH_S3_DATA_PLAIN = "SELECT time_s3_store_chunk, time_s3_get_chunk FROM CLIENT_S3_SYNC_PLAIN WHERE _rowid_>=? AND _rowid_<?;"
FETCH_S3_DATA_TALOS = "SELECT time_s3_store_chunk, time_s3_get_chunk FROM CLIENT_S3_SYNC_TALOS WHERE _rowid_>=? AND _rowid_<?;"


def fetch_s3_data_from_db(db_path, from_row, to_row):
    with sqlite3.connect(db_path) as conn:
        plain_data = np.asarray(conn.execute(FETCH_S3_DATA_PLAIN, (from_row, to_row)).fetchall())
        talos_data = np.asarray(conn.execute(FETCH_S3_DATA_TALOS, (from_row, to_row)).fetchall())
        return plain_data, talos_data


def extract_client_data_from_db(db_path, start_data, end_data):
    with sqlite3.connect(db_path) as conn:
        data = np.asarray(conn.execute(FETCH_CLIENT_DATA, (start_data, end_data)).fetchall())
        return data[:, 0], data[:, 1]


def extract_address_data_from_db(query, db_path, start_data, end_data):
    with sqlite3.connect(db_path) as conn:
        list_data = conn.execute(query, (start_data, end_data)).fetchall()
        list_data = [0.0 if x[0] is None else x[0] for x in list_data]
        return np.asarray(list_data)


def extract_address_all_data_from_db(db_path, start_data, end_data):
    res1 = extract_address_data_from_db(FETCH_ADDRESS_STORE, db_path, start_data, end_data)
    res2 = extract_address_data_from_db(FETCH_ADDRESS_GET, db_path, start_data, end_data)
    return res1, res2

def plot_dht_latency():
    path = "../data/local_dht_benchmark_k10_a3"

    data_store = []
    data_get = []
    data_get_addr = []
    data_store_addr = []
    for filename in os.listdir(path):
        if filename.endswith(".db"):
            matching = db_pattern.match(filename)
            if matching:
                num_nodes = int(matching.group(3))
                latency = int(matching.group(4)) * 2
                store_data, get_data = extract_client_data_from_db(os.path.join(path, filename), 25, 1025)
                data_store.append([num_nodes, latency] + store_data.tolist())
                data_get.append([num_nodes, latency] + get_data.tolist())

                store_data_addr, get_data_addr = extract_address_all_data_from_db(os.path.join(path, filename), 25, 1025)
                data_store_addr.append([num_nodes, latency] + store_data_addr.tolist())
                data_get_addr.append([num_nodes, latency] + get_data_addr.tolist())

    data_store = np.asarray(data_store)
    data_get = np.asarray(data_get)
    data_get_addr = np.asarray(data_get_addr)
    data_store_addr = np.asarray(data_store_addr)

    data_store = data_store[data_store[:, 0].argsort()]
    data_get = data_get[data_get[:, 0].argsort()]
    data_get_addr = data_get_addr[data_get_addr[:, 0].argsort()]
    data_store_addr = data_store_addr[data_store_addr[:, 0].argsort()]



    print data_store.shape
    print data_get.shape
    print data_get_addr.shape
    print data_store_addr.shape

    s3_plain_data, s3_enc_data = fetch_s3_data_from_db(data_path_s3, 300, 600)

    def compute_latency(data):
        avg_latency = np.average(data, axis=0)
        std_latency = np.std(data, axis=0)
        return avg_latency, std_latency


    def get_data_for_latency(latency, data):
        temp = data[data[:, 1] == latency]
        temp = temp[temp[:, 0].argsort()]
        return temp[:, 0], temp[:, 2:]



    #########
    # PLOTS #
    #########

    #---------------------------- GLOBAL VARIABLES --------------------------------#
    # figure settings
    fig_width_pt = 300.0                        # Get this from LaTeX using \showthe
    inches_per_pt = 1.0/72.27*2                 # Convert pt to inches
    golden_mean = ((math.sqrt(5)-1.0)/2.0)*.8   # Aesthetic ratio
    fig_width = fig_width_pt*inches_per_pt      # width in inches
    fig_height =(fig_width*golden_mean)           # height in inches
    fig_size = [fig_width,fig_height/1.22]

    params = {'backend': 'ps',
        'axes.labelsize': 20,
        'legend.fontsize': 18,
        'xtick.labelsize': 18,
        'ytick.labelsize': 18,
        'font.size': 18,
        'figure.figsize': fig_size,
        'font.family': 'times new roman'}

    pdf_pages = PdfPages('../plots/paper_dht_latency.pdf')
    fig_size = [fig_width*1.1, fig_height / 1.8]

    plt.rcParams.update(params)
    plt.axes([0.12, 0.32, 0.85, 0.63], frameon=True)
    plt.rc('pdf', fonttype=42)  # IMPORTANT to get rid of Type 3


    def compute_avg_std(data):
        return np.average(data, axis=1), np.std(data, axis=1)


    latency = 20

    f,  ax1 = plt.subplots()

    nodes_s, data_s = get_data_for_latency(latency, data_store)
    mean_s, std_s = compute_avg_std(data_s)
    nodes_g, data_g = get_data_for_latency(latency, data_get)
    mean_g, std_g = compute_avg_std(data_g)

    _, addr_data_s = get_data_for_latency(latency, data_store_addr)
    addr_mean_s, addr_std_s = compute_avg_std(addr_data_s)
    _, addr_data_g = get_data_for_latency(latency, data_get_addr)
    addr_mean_g, addr_std_g = compute_avg_std(addr_data_g)

    avg_plain_l, std_plain_l = compute_latency(s3_plain_data)
    avg_enc_l, std_enc_l = compute_latency(s3_enc_data)

    mean_s = np.append(mean_s, (avg_plain_l[0], avg_enc_l[0]))
    std_s = np.append(std_s, (std_plain_l[0], std_enc_l[0]))

    mean_g = np.append(mean_g, (avg_plain_l[1], avg_enc_l[1]))
    std_g = np.append(std_g, (std_plain_l[1], std_enc_l[1]))

    ind_long = np.arange(1, len(nodes_g.tolist()) + 3)
    ind = np.arange(1, len(nodes_g.tolist())+1)
    width = 0.25

    colours = ['0.25', '0.4', '0.7', '0.9']
    hatch_style='\\\\\\\\'

    ax1.grid(True, linestyle=':', color='0.8' , axis='y')
    rects1 = ax1.bar(ind_long, mean_s, width, color=colours[0], yerr=std_s, error_kw=dict(ecolor='0.6', lw=1, capsize=4, capthick=1))
    rects2 = ax1.bar(ind_long + width, mean_g, width, hatch=hatch_style, color=colours[1], yerr=std_g, error_kw=dict(ecolor='0.6', lw=1, capsize=5, capthick=1))
    print "store: ", mean_s
    print "get: ",mean_g
    
    rects3 = ax1.bar(ind, addr_mean_s, width, color=colours[2], zorder=3) #, yerr=addr_std_s, error_kw=dict(ecolor='0.75', lw=2, capsize=5, capthick=2))
    rects4 = ax1.bar(ind + width, addr_mean_g, width, color=colours[3], hatch=hatch_style, zorder=3) #, yerr=addr_std_g, error_kw=dict(ecolor='0.25', lw=2, capsize=5, capthick=2))


    ax1.set_ylabel("Time [ms]")
    ax1.set_xticks(ind_long + width)
    ax1.set_xticklabels((map(lambda x: str(int(x)), nodes_g.tolist())) + ["Vanilla", "Secure"])
    ax1.set_xlabel("       Number of nodes                                   Amazon S3")

    #ax1.legend((rects1[0], rects2[0], rects3[0], rects4[0]), ('Store', 'Get', 'Routing Store', 'Routing Get'), loc="upper left", ncol=2)
    legend = ax1.legend((rects1[0], rects2[0], rects3[0], rects4[0]), ('store', 'get', 'routing store', 'routing get'), bbox_to_anchor=(-0.02, .845, 1., .102), loc=6, ncol=4, columnspacing=1)

    legend.get_frame().set_facecolor('none')
    legend.get_frame().set_linewidth(0.0)
    
    #handletextpad=0.5, labelspacing=0.2, borderaxespad=0.2, borderpad=0.3)

    #f.suptitle("RTT-%d average latency DHT operations" % latency, fontsize=24, y=1.02)
    ax1.set_ylim([0, 230])
    ax1.yaxis.set_ticks(np.arange(0, 201, 30.0))
    


    F = plt.gcf()
    F.set_size_inches(fig_size)
    pdf_pages.savefig(F, bbox_inches='tight', dpi=300)
    plt.clf()
    pdf_pages.close()

if __name__ == "__main__":
    plot_dht_latency()