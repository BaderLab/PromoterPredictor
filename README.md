# PromoterPredictor
Using a SVM and 5 identified features, scan genomic coordinates for putative promoter regions

'''
Author: Ahmad Shah

Contact: ahmad.shah@mail.utoronto.ca

Created: August, 2018

'''

=====PROMOTER PREDICTOR SOFTWARE=====

This folder contains the necessary files for running the promoter region predictor
curated in the associated study. The package contains several python scripts,
SQLite3 databases and a WEKA model file containing the resulting model. All
instructions pertaining to which packages must be installed and how to run the
predictor on your own data or on the provided example data set can be found in
"instructions.txt". It is recommended that the predictor be run on the example
data first in order to better understand the required format for the input data
as well as the expected outcome.

This package also gives users the ability to update the input data used by the
learner for the 5 input features. In order to achieve this please follow
the guide lines in the "instructions_data_update.txt" file.
