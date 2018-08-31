import sqlite3
import sys
import csv
import os

#================== GENERATE METH PROBES FEATURE VALUES TABLES==================

conn_local = sqlite3.connect('user_define_kmers_feature_values.sqlite3')
cur_local = conn_local.cursor()

cur_local.execute('DROP TABLE IF EXISTS meth_probes ')
cur_local.execute('CREATE TABLE meth_probes (gene_name VARCHAR(1000), chrom VARCHAR(10), position INT)')


cwd = os.getcwd()
filename = cwd + "%sdata%smethylation_probes.txt" % (os.path.sep, os.path.sep)
file_object = open(filename, 'r')

full_file = file_object.read()
split_file = full_file.split('\n')

header_keys = {}
header_arr = split_file[0].split("\t")

i=0
for header in header_arr:
    header = header
    header_keys[header] = i
    i += 1

for i in range(1,len(split_file)):
    line = split_file[i].split('\t')
    probe = line[header_keys['Composite Element REF']]
    Gene_Symbol = line[header_keys['Gene_Symbol']]
    Gene_Symbol = Gene_Symbol.split(';')[0]
    Chromosome = line[header_keys['Chromosome']]

    Genomic_Coordinate = line[header_keys['Genomic_Coordinate']]
    insert = "INSERT INTO meth_probes VALUES ('%(Gene_Symbol)s','%(Chromosome)s',%(Genomic_Coordinate)s)" \
	% {"Gene_Symbol": Gene_Symbol, "Chromosome": Chromosome, "Genomic_Coordinate": Genomic_Coordinate}
    cur_local.execute(insert)

conn_local.commit()

print("===Methylation probes SQLite table has been updated===")
