'''
Author: Ahmad Shah

Contact: ahmad.shah@mail.utoronto.ca

Created: August, 2018

Given the predicted promoter region outputs from WEKA, utilize DNAse data to
further refine the boundaries to where DNAse peaks are seen (furthest upstream
and downstream within the identified boundaries).
'''

import sqlite3
import sys
import csv
import os


def refine_promoter_dnase():
    conn_user_peaks = sqlite3.connect('user_define_promoter_peaks.sqlite3')
    cur_user_peaks = conn_user_peaks.cursor()
    delete = "DROP TABLE IF EXISTS predicted_promoter_dnase_peaks_user;"
    cur_user_peaks.execute(delete)
    create = "CREATE TABLE predicted_promoter_dnase_peaks_user (prom_pkey INT, chr INT, dnase_file VARCHAR(10), start_pos INT, end_pos INT, peak FLOAT, strand VARCHAR(10));"
    cur_user_peaks.execute(create)

    conn_peaks = sqlite3.connect('dnase_tables.sqlite3')
    cur_peaks = conn_peaks.cursor()

    dnase_files = []
    dnaseFile = "dnase_files.csv"
    file_object = open(dnaseFile, 'r')
    full_dnaseFile = file_object.read()
    split_dnaseFile = full_dnaseFile.split('\n')
    for cur_line in split_dnaseFile:
        if cur_line != '':
          dnase_files.append(cur_line)

    filename = "generated_files%suser_define_kmers_promoter_prediction_coordinates.csv" % (os.path.sep)
    file_object = open(filename, 'r')
    full_file = file_object.read()
    split_file = full_file.split('\n')
    temp_pkey = 1
    all_proms = {}
    no_peak_proms = []
    for cur_line in split_file:
        cur_line = cur_line.rstrip()
        if cur_line == '':
            continue;
        split_line = cur_line.split(',')
        cur_chr = split_line[0]
        if cur_chr == 'chrom':
            continue;
        prom_start = split_line[1]
        prom_end = split_line[2]
        strand = '+'
        all_proms[temp_pkey] = [cur_chr, prom_start, prom_end, strand]
        no_peak_proms.append(temp_pkey)
        for cur_file in dnase_files:
            select =  "select start_pos, end_pos, peak from dnase_peaks_" + cur_file + "_" + str(cur_chr) + " where chr = '" + str(cur_chr) + "' and start_pos >= " + prom_start + " AND end_pos <= " + prom_end + ";"
            cur_peaks.execute(select)
            result = cur_peaks.fetchall()
            for row in result:
                start_pos = row[0]
                end_pos = row[1]
                peak = row[2]
                insert = "INSERT INTO predicted_promoter_dnase_peaks_user VALUES (%(promoter_pkey)s,%(chr)s,'%(dnase_file)s',%(start_pos)s,%(end_pos)s,%(peak)s,'%(strand)s')" \
                % {"promoter_pkey" : temp_pkey,"chr" : cur_chr,"dnase_file" : cur_file,"start_pos": start_pos, "end_pos": end_pos, "peak": peak, "strand": strand}
                cur_user_peaks.execute(insert)
                if temp_pkey in no_peak_proms:
                    no_peak_proms.remove(temp_pkey)

        temp_pkey += 1
        conn_user_peaks.commit()

    info_arr = [["chrom", "promoter_start", "promoter_end", "evidence"]]
    select = "SELECT prom_pkey, chr, min(start_pos), max(end_pos), strand FROM predicted_promoter_dnase_peaks_user GROUP BY prom_pkey"
    cur_user_peaks.execute(select)
    result = cur_user_peaks.fetchall()
    for row in result:
        pkey = row[0]
        cur_chr = row[1]
        new_start_pos = row[2]
        new_end_pos = row[3]
        strand = row[4]
        source = "DNAse peaks"
        info_arr.append([cur_chr, new_start_pos, new_end_pos, source])

    for cur_key in no_peak_proms:
        cur_prom = all_proms[cur_key]
        cur_chr = cur_prom[0]
        start_pos = cur_prom[1]
        end_pos = cur_prom[2]
        strand = cur_prom[3]
        source = "raw predictor output"
        info_arr.append([cur_chr, start_pos, end_pos, source])

        #Write predicted promoter coordinates to a .csv file
        with open("generated_files%sDNAse_promoter_prediction_coordinates.csv" % (os.path.sep), 'wb') as fp:
            a = csv.writer(fp, delimiter=',')
            a.writerows(info_arr)
