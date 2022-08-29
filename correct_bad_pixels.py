#import py4DSTEM
import math
import os
import numpy as np
import math
import hyperspy.api as hs
from converter_nord import save_signal
import pyxem as pxm
import os
import yaml
from yacs.config import CfgNode as CN
import datetime


# config_file = 'configs/config_federico.yml'
config_file = './configs/config_gulnaz_new_dataset.yml'
NEEDS_RESHAPING = True
os.chdir('.')
print(os.getcwd())

# Load config file
with open(config_file, "r") as stream:
    try:
        cfg = yaml.safe_load(stream)

    except yaml.YAMLError as exc:
        print(exc)
cfg = CN(cfg)
print(cfg)



# Reshape the dataset to the right format
dir, filename = os.path.split(cfg.SETUP.DATA_PATH)
filename = os.path.splitext(filename)[0]  # remove extension
reshaped_path = dir + '/' + filename + '_reshaped.hspy'

if NEEDS_RESHAPING:
    start_time = datetime.datetime.now()
    print(f'Reshaping dataset... ({start_time})')
    # TODO: make sure the dimensions of the dataset are correct
    save_signal(cfg.SETUP.DATA_PATH, reshaped_path, 640, 640, 1)
    end_time = datetime.datetime.now()
    print(f'Reshaping done! (it took {end_time-start_time})')


# Load the reshaped dataset
dp = hs.load(reshaped_path, lazy=True)

# Convert reshaped dataset to .zspy format
converted_path = reshaped_path[:-5] + '.zspy'
start_time = datetime.datetime.now()
print(f'Converting to .zspy format... ({start_time})')
dp.save(converted_path)
end_time = datetime.datetime.now()
print(f'Converting done! (it took {end_time-start_time})')
dp = hs.load(converted_path, lazy=True)

# fix the bad pixels
start_time = datetime.datetime.now()
print(f'Finding dead pixels... ({start_time})')
s_dead_pixels = dp.find_dead_pixels(dead_pixel_value=0)
end_time = datetime.datetime.now()
print(f'Done! (it took {end_time-start_time})')

start_time = datetime.datetime.now()
print(f'Finding hot pixels... ({start_time})')
s_hot_pixels = dp.find_hot_pixels(show_progressbar=True, threshold_multiplier=10)
end_time = datetime.datetime.now()
print(f'Done! (it took {end_time-start_time})')

# correct for bad pixels (dead and hot)
start_time = datetime.datetime.now()
print(f'Correcting bad pixels... ({start_time})')
dp.correct_bad_pixels(s_dead_pixels + s_hot_pixels, show_progressbar=True, inplace=True, lazy_result=True)
end_time = datetime.datetime.now()
print(f'Done! (it took {end_time-start_time})')

# save the corrected dataset
corrected_path = dir + '/' + filename + '_corrected.zspy'
start_time = datetime.datetime.now()
print(f'Saving corrected dataset... ({start_time})')
dp.save(corrected_path)
end_time = datetime.datetime.now()
print(f'Done! (it took {end_time-start_time})')
