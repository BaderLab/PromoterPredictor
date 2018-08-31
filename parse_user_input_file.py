'''
Author: Ahmad Shah

Contact: ahmad.shah@mail.utoronto.ca

Created: August, 2018

Parse the input coordiantes given by the user and generate the necessary k-mers
to cover these regions. Store results in SQLite database.
'''

import sys
import csv
import sqlite3


def parse_user_input(filename):
    #Create local sqlite files
    conn_local = sqlite3.connect('gene_information.sqlite3')
    cur_local = conn_local.cursor()

    conn_kmer = sqlite3.connect('user_define_kmers_feature_values.sqlite3')
    cur_kmer = conn_kmer.cursor()

    cur_kmer.execute('DROP TABLE IF EXISTS user_define_kmers_feature_values ')
    cur_kmer.execute('CREATE TABLE user_define_kmers_feature_values (chrom VARCHAR(10), strand VARCHAR(10), interval_start INT, interval_end INT, pkey BIGSERIAL PRIMARY KEY)')

    #Parse user given file and break into 2500bp k-mers, iterating by 100bp
    pkey_index = 1
    with open(filename) as f:
        for line in f:
            line.strip()
            line_arr = line.split(',')

            #Check that the input file is a CSV
            if pkey_index == 1 and len(line_arr) == 1:
                print "ERROR: Please ensure that input file is a CSV"
                sys.exit()

            if len(line_arr) == 1:
                continue;

            chromosome = line_arr[0].strip()
            start_pos = int(line_arr[1].strip())
            end_pos = int(line_arr[2].strip())
            strand = '+'

            if end_pos - start_pos < 2500:
                print "Region too small, skipped:" + str(start_pos) + ", " + str(end_pos)
                continue;

            current_pos = int(start_pos) + 2500
            previous_pos = int(start_pos)
            while current_pos <= end_pos:

                if strand == '+':
                    select = "SELECT * FROM biomart_genes_whole_genome WHERE chrom = '" + str(chromosome) + "' and (((txstart - " + str(previous_pos) + " < 2500) and (txstart - " + str(previous_pos) + " > 0) and strand = '1') OR (" + str(previous_pos) + " >= txstart and " + str(previous_pos) + " <= txend))";
                    cur_local.execute(select)
                    result = cur_local.fetchall()
                else:
                    select = "SELECT * FROM biomart_genes_whole_genome WHERE chrom = '" + str(chromosome) + "' and (((txstart - " + str(previous_pos) + " < 2500) and (txstart - " + str(previous_pos) + " > 0) and strand = '-1') OR (" + str(previous_pos) + " >= txstart and " + str(previous_pos) + " <= txend))";
                    cur_local.execute(select)
                    result = cur_local.fetchall()

                select2 = "SELECT * FROM refseq_genes WHERE chrom = '" + str(chromosome) + "' and (((txstart - " + str(previous_pos) + " < 2500) and (txstart - " + str(previous_pos) + " > 0) and strand = '" + strand + "') OR (" + str(previous_pos) + " >= txstart and " + str(previous_pos) + " <= txend))";
                cur_local.execute(select2)
                result2 = cur_local.fetchall()
                if (len(result) > 0) or (len(result2) > 0):
                    print "OVERLAPPING PROMOTER OR GENE BODY: SKIPPED-------------" + str(previous_pos) + ", " + str(current_pos)
                    previous_pos = previous_pos + 100
                    current_pos = current_pos + 100
                    continue;

                #Store all created k-mers in an SQLite table
                insert = "INSERT INTO user_define_kmers_feature_values VALUES ('%(chromosome)s','%(strand)s','%(previous_pos)s','%(current_pos)s',%(pkey_index)s)" \
                    % {"chromosome" : chromosome , "strand": strand, "previous_pos": previous_pos, "current_pos": current_pos, "pkey_index": pkey_index}
                cur_kmer.execute(insert)
                pkey_index = pkey_index + 1
                previous_pos = previous_pos + 100
                current_pos = current_pos + 100
                conn_kmer.commit()
