'''
Author: Ahmad Shah

Contact: ahmad.shah@mail.utoronto.ca

Created: August, 2018

This file will call all the necessary functions in order to parse the user input
file and run the promoter region predictor.
'''

from optparse import OptionParser
import parse_user_input_file
import generate_feature_value_files
import parse_weka_output
import refine_promoter_dnase

#!/usr/bin/python

import sys, getopt

#USAGE: python run_package.py -f PATH_TO_YOUR_FILE
def main(argv):
   inputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hf:",["file="])
   except getopt.GetoptError:
      print 'USAGE: run_package.py -f <inputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'USAGE: run_package.py -f <inputfile>'
         sys.exit()
      elif opt in ("-f", "--file"):
         inputfile = arg
   print 'Input file is :', inputfile
   return inputfile

# if __name__ == "__main__":
input_file = main(sys.argv[1:])

#Call function to parse user's input coordinates into k-mer's that the learner will recognize
print "Parsing user input, creating k-mers"
parse_user_input_file.parse_user_input(str(input_file));

#For each k-mer produced, generate feature values for the 5 given features
print "Generating feature values"
generate_feature_value_files.generate_feature_value_files()

#Hold the script while work is executed using WEKA
raw_input("Please generate WEKA output file and then press Enter to continue...")

#Parse WEKA output to extract predicted promoter coordinates
print "Parsing weka output"
parse_weka_output.parse_weka_output()

#Parse predicted promoter coordinates and refine them using DNAse data
print "Refining promoter boundaries using DNAse data"
refine_promoter_dnase.refine_promoter_dnase()

print "===Predictions completed, find results in generated_files folder==="
