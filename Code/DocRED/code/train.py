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

parser.add_argument('--train_prefix', type = str, default = 'dev_train')
parser.add_argument('--test_prefix', type = str, default = 'dev_dev')


args = parser.parse_args()

con = config.Config(args)
con.set_max_epoch(10000)
con.load_train_data()
con.load_test_data()
con.train(models.BiLSTM, args.save_name)
