import sqlite3
import sys
import csv
import os

#========================CREATE CPG FEATURE VALUES TABLES=======================

conn_local = sqlite3.connect('user_define_kmers_feature_values.sqlite3')
cur_local = conn_local.cursor()

cur_local.execute('DROP TABLE IF EXISTS UCSC_cpg ')
cur_local.execute('CREATE TABLE UCSC_cpg (chrom VARCHAR(10), chromstart INT, chromend INT)')

cwd = os.getcwd()
filename = cwd + "%sdata%s" % (os.path.sep, os.path.sep) + "cpg_island.txt"
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
    chromStart = line[header_keys['chromStart']]
    chromEnd = line[header_keys['chromEnd']]
    name = line[header_keys['name']]
    length = line[header_keys['length']]
    cpgNum = line[header_keys['cpgNum']]
    gcNum = line[header_keys['gcNum']]
    perCpg = line[header_keys['perCpg']]
    perGc = line[header_keys['perGc']]
    obsExp = line[header_keys['obsExp']]
    chrom = line[header_keys['chrom']]
    chrom = chrom[3:]
    insert = "INSERT INTO UCSC_cpg (chrom, chromstart, chromend) VALUES ('%(chrom)s','%(chromstart)s',%(chromend)s)"\
            % {"chrom" : chrom ,"chromstart": chromStart, "chromend": chromEnd}
    cur_local.execute(insert)

conn_local.commit()

print("===CpG island SQLite table has been updated===")
