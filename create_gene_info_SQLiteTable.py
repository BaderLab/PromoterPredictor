import sqlite3
import sys
import csv
import os

conn_local = sqlite3.connect('gene_information.sqlite3')
cur_local = conn_local.cursor()

cur_local.execute('DROP TABLE IF EXISTS refseq_genes ')
cur_local.execute('CREATE TABLE refseq_genes (chrom VARCHAR(10), strand VARCHAR(10), txstart INT, txend INT)')

cwd = os.getcwd()
filename = cwd + "%sdata%srefseq_genes.txt" % (os.path.sep, os.path.sep)
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
    name = line[header_keys['name']]
    chrom = line[header_keys['chrom']]
    chrom = chrom[3:]
    if chrom == 'X':
        chrom = '23'
    if chrom == 'Y':
        chrom = '24'

    try:
        int_chrom = int(chrom)
    except:
        continue;

    strand = line[header_keys['strand']]
    txStart = line[header_keys['txStart']]
    txEnd = line[header_keys['txEnd']]
    cdsStart = line[header_keys['cdsStart']]
    cdsEnd = line[header_keys['cdsEnd']]
    exonCount = line[header_keys['exonCount']]
    exonStarts = line[header_keys['exonStarts']]
    exonEnds = line[header_keys['exonEnds']]
    name2 = line[header_keys['name2']]
    insert = "INSERT INTO refseq_genes VALUES ('%(name)s','%(chrom)s','%(strand)s',%(txStart)s,%(txEnd)s)" \
	% {"name" : name ,"chrom": chrom, "strand": strand, "txStart": txStart, "txEnd": txEnd}
    cur_local.execute(insert)
conn_local.commit()


#==========================Parse biomart genes==================================


cur_local.execute('DROP TABLE IF EXISTS biomart_genes_whole_genome ')
cur_local.execute('CREATE TABLE biomart_genes_whole_genome (chrom VARCHAR(10), strand VARCHAR(10), txstart INT, txend INT)')

cwd = os.getcwd()
filename = cwd + "%sdata%sbiomart_genes.txt" % (os.path.sep, os.path.sep)
file_object = open(filename, 'r')

full_file = file_object.read()
split_file = full_file.split('\n')

header_keys = {}
header_arr = split_file[0].split(",")

i=0
for header in header_arr:
    header = header
    header_keys[header] = i
    i += 1


inserted_genes = []
for i in range(1,len(split_file)):
    line = split_file[i].split(',')
    name = line[header_keys['Associated Gene Name']]
    txStart = line[header_keys['Transcript Start (bp)']]
    txEnd = line[header_keys['Transcript End (bp)']]
    chrom = line[header_keys['Chromosome Name']]

    if chrom == 'X':
        chrom = '23'
    elif chrom == 'Y':
        chrom = '24'

    if chrom == '23' or chrom == '24':
        print chrom
    else:
        continue;

    strand = line[header_keys['Strand']]
    trans_id = line[header_keys['Ensembl Transcript ID']]


    insert = "INSERT INTO biomart_genes_whole_genome VALUES ('%(name)s','%(chrom)s',%(txStart)s,%(txEnd)s)" \
	% {"name" : name ,"chrom": chrom, "txStart": txStart, "txEnd": txEnd}
    cur_local.execute(insert)
conn_local.commit()

print("===Gene information SQLite tables has been updated===")
