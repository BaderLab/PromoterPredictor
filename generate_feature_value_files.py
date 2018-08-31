'''
Author: Ahmad Shah

Contact: ahmad.shah@mail.utoronto.ca

Created: August, 2018

Using the k-mers generated for the user input data, generate feature vectors for
each containing values for the 5 identified features.
'''

import sys
import csv
import sqlite3
import os

def generate_feature_value_files():
    #Generate feature values per k-mer, for all 5 features
    conn_kmer = sqlite3.connect('user_define_kmers_feature_values.sqlite3')
    cur_kmer = conn_kmer.cursor()

    num_features = 5
    select = "SELECT pkey FROM user_define_kmers_feature_values;"
    cur_kmer.execute(select)
    result = cur_kmer.fetchall()
    gene_body_dict = {}
    for row in result:
        gene = row[0]
        gene_body_dict[gene] = []
        for i in range(num_features):
            gene_body_dict[gene].append(0)

    #CpG island feature using 450k array data
    feature_number = 0
    select = "SELECT distinct b.pkey FROM user_define_kmers_feature_values b, (SELECT gene_name, chrom, position FROM meth_probes) a WHERE a.chrom = b.chrom and a.position >= b.interval_start and a.position <= b.interval_end;"
    cur_kmer.execute(select)
    result = cur_kmer.fetchall()
    for row in result:
        gene = row[0]
        gene_body_dict[gene][feature_number] = 1

    feature_number = feature_number + 1

    #CpG island data from UCSC
    select = "SELECT distinct b.pkey FROM user_define_kmers_feature_values b, (SELECT chrom, chromstart, chromend FROM UCSC_cpg) a WHERE a.chrom = b.chrom and (a.chromstart >= b.interval_start and a.chromstart <= b.interval_end);"
    cur_kmer.execute(select)
    result = cur_kmer.fetchall()
    for row in result:
        gene = row[0]
        gene_body_dict[gene][feature_number] = 1

    feature_number = feature_number + 1

    #ChIP-Seq histone data from the roadmap epigenomics project
    chip_hist_files = ['E118_H3K36me3','E037_H3K36me3','E029_H3K36me3']
    for chip_hist_file in chip_hist_files:
        select = "SELECT b.pkey, signal_value FROM user_define_kmers_feature_values b, (SELECT chr, start_pos, end_pos, signal_value, qvalue FROM chipseq_peaks_roadmap_epig_" + chip_hist_file + ") a WHERE a.chr = b.chrom and a.start_pos >= b.interval_start and a.start_pos <= b.interval_end and qvalue >= 1.301 order by signal_value asc;"
        cur_kmer.execute(select)
        result = cur_kmer.fetchall()
        for row in result:
            gene = row[0]
            signal_value = row[1]
            gene_body_dict[gene][feature_number] = signal_value

        feature_number = feature_number + 1

    csv_data = []

    for key, value in gene_body_dict.iteritems():
        info_arr = []
        for data in value:
            info_arr.append(data)
        info_arr.append("?")
        csv_data.append(info_arr)

   #Write all data to a .arff that is readily recognizable by WEKA
    f = open("generated_files%suser_define_kmers_feature_values.arff" % (os.path.sep),'w')
    f.write("@relation user_define_kmers_feature_values\n\n@attribute CpG numeric\n@attribute UCSC_cpg numeric\n@attribute E118_H3K36me3 numeric\n@attribute E037_H3K36me3 numeric\n@attribute E029_H3K36me3 numeric\n@attribute region {promoter,random_region}\n\n@data\n")
    f.close()

    with open("generated_files%suser_define_kmers_feature_values.arff" % (os.path.sep), 'ab') as fp:
        a = csv.writer(fp, delimiter=',')
        a.writerows(csv_data)
