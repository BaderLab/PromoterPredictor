import sqlite3
import sys
import csv
import os

#==== Function call to parse file into SQLite table
def parse_epigroadmap_chipseq(filename, chip_file):

    conn_local = sqlite3.connect('user_define_kmers_feature_values.sqlite3')
    cur_local = conn_local.cursor()
    cur_local.execute("DROP TABLE IF EXISTS chipseq_peaks_roadmap_epig_" + chip_file)
    cur_local.execute("CREATE TABLE chipseq_peaks_roadmap_epig_" + chip_file + " (chr VARCHAR(10), start_pos INT, end_pos INT, signal_value FLOAT, qvalue FLOAT)")

    file_object = open(filename, 'r')

    full_file = file_object.read()
    split_file = full_file.split('\n')

    header_keys = {}
    header_arr = ["chrom","chromStart","chromEnd","rank","score","strand","signal_value","pvalue","qvalue" ,"peak"]
    i=0

    for header in header_arr:
        header = header
        header_keys[header] = i
        i += 1

    for i in range(1,len(split_file)):
        if split_file[i] == "":
            continue;
        line = split_file[i].split('\t')
        chr = line[header_keys['chrom']]
        start_pos = line[header_keys['chromStart']]
        end_pos = line[header_keys['chromEnd']]
        score = line[header_keys['score']]
        signal_value = line[header_keys['signal_value']]
        pvalue = line[header_keys['pvalue']]
        qvalue = line[header_keys['qvalue']]
        peak = line[header_keys['peak']]
        chr = chr[3:]
        if chr == 'X':
            chr = '23'
        if chr == 'Y':
            chr = '24'

        try:
            int_chrom = int(chr)
        except:
            continue;

        insert = "INSERT INTO chipseq_peaks_roadmap_epig_" + chip_file + " (chr, start_pos, end_pos, signal_value, qvalue) VALUES ('%(chr)s','%(start_pos)s',%(end_pos)s,%(signal_value)s,%(qvalue)s)"\
                % {"chr" : chr ,"start_pos": start_pos, "end_pos": end_pos, "signal_value": signal_value, "qvalue": qvalue}
        cur_local.execute(insert)

    conn_local.commit()

#==== Call function on feature selected files ====
chip_hist_files = ['E118_H3K36me3','E037_H3K36me3','E029_H3K36me3']
for chip_hist_file in chip_hist_files:
    cwd = os.getcwd()
    file_sub = chip_hist_file.replace('_', '-')
    filename = cwd + "%sdata%s" % (os.path.sep, os.path.sep) + file_sub + ".narrowPeak"
    parse_epigroadmap_chipseq(filename, chip_hist_file)

print("===ChIP-Seq peaks SQLite tables has been updated===")
