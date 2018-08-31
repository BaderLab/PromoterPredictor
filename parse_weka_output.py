'''
Author: Ahmad Shah

Contact: ahmad.shah@mail.utoronto.ca

Created: August, 2018

Parse output from WEKA and extract the predicted promoter coordinates and write
to file
'''

import sqlite3
import sys
import csv
import os


def parse_weka_output():
    conn_kmer = sqlite3.connect('user_define_kmers_feature_values.sqlite3')
    cur_kmer = conn_kmer.cursor()

    filename = "generated_files%suser_define_kmers_feature_values_predictions.csv" % (os.path.sep)
    file_object = open(filename, 'r')

    full_file = file_object.read()
    split_file = full_file.split('\n')

    promo_region_dict = {}

    prev_region = ""
    i = 5

    pkey_checker = []
    special_case = "no"

    #Coordinates are extracted by matching pkey values between the WEKA output and the
    #data store when the k-mers were created
    pkey_chrom_dict = {}
    select = "SELECT pkey, chrom FROM user_define_kmers_feature_values;"
    cur_kmer.execute(select)
    result = cur_kmer.fetchall()
    for row in result:
        pkey = row[0]
        chrom = row[1]
        pkey_chrom_dict[pkey] = chrom

    pkey_counter = 0
    done_loops = "no"
    while i < len(split_file):
        if done_loops == "yes":
            break;
        if split_file[i] == '':
            i = i + 1
            continue;
        split_line = split_file[i].split(',')
        pkey = split_line[0].strip()
        pkey = int(pkey)
        region = split_line[2].strip().split(':')[1]
        if i == 5:
            prev_region = region

        if prev_region == "random_region" and region == "promoter" or (prev_region == "promoter" and special_case == "yes"):

            select = "SELECT interval_start, interval_end, strand FROM user_define_kmers_feature_values WHERE pkey = " + str(pkey) + ";"
            cur_kmer.execute(select)
            result = cur_kmer.fetchall()
            for row in result:
                int_start = row[0]
                int_end = row[1]
                strand = row[2]

            promo_region_dict[pkey] = [int_start]
            starter_pkey = pkey
            stay_in = "yes"
            special_case = "no"
            last_int_start = int_start
            while stay_in == "yes":
                next_line = split_file[i+1].split(',')
                if next_line[0] == "":
                    stay_in = "no"
                    i = i + 1
                    done_loops = "yes"
                    break

                check_pkey = next_line[0].strip()
                next_region = next_line[2].strip().split(':')[1]
                if next_region == "promoter":
                    select = "SELECT interval_start FROM user_define_kmers_feature_values WHERE pkey = " + str(check_pkey) + ";"
                    cur_kmer.execute(select)
                    result = cur_kmer.fetchall()
                    for row in result:
                        int_start = row[0]

                    if int_start - last_int_start != 100:
                        stay_in = "no"
                        special_case = "yes"
                        last_int_start = int_start
                    else:
                        last_int_start = int_start

                    i = i + 1
                else:
                    stay_in = "no"
                    i = i + 1

            split_line = split_file[i-1].split(',')
            pkey = split_line[0].strip()
            select = "SELECT interval_start, interval_end, strand FROM user_define_kmers_feature_values WHERE pkey = " + str(pkey)
            cur_kmer.execute(select)
            result = cur_kmer.fetchall()
            for row in result:
                int_start = row[0]
                int_end = row[1]
                strand = row[2]

            promo_region_dict[starter_pkey].append(int_end)
            promo_region_dict[starter_pkey].append(pkey)
            promo_region_dict[starter_pkey].append(strand)
            pkey_checker.append(int(pkey)-int(starter_pkey))
        else:
            prev_region = region
            i = i + 1

    pkey_checker.sort()

    info_arr = [["chrom", "promoter_start", "promoter_end"]]
    for key, value in promo_region_dict.iteritems():
        chrom = pkey_chrom_dict[key]
        promoter_start = value[0]
        promoter_end = value[1]
        strand = value[3]
        info_arr.append([chrom, promoter_start, promoter_end])

    #Write predicted promoter coordinates to a .csv file
    with open("generated_files%suser_define_kmers_promoter_prediction_coordinates.csv" % (os.path.sep), 'wb') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(info_arr)
