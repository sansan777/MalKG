import config
import models
import numpy as np
import os
import time
import datetime
import json
from sklearn.metrics import average_precision_score
import sys
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--save_name', type = str)

parser.add_argument('--train_prefix', type = str, default = 'train')
parser.add_argument('--test_prefix', type = str, default = 'dev_dev')
parser.add_argument('--input_theta', type = float, default = -1)


args = parser.parse_args()

con = config.Config(args)
con.load_test_data()
con.testall(models.BiLSTM, args.save_name, args.input_theta)
