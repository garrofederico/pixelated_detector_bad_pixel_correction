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
import os
import sys
import argparse
from pathlib import Path

# Create the parser
my_parser = argparse.ArgumentParser(description='Corrects the bad pixels of a pixem 4D dataset and outputs a .zspy file')

# Add the arguments
my_parser.add_argument('-p', '--paths', metavar='path/to/dataset(s)', nargs='+', type=str, required=True,
                       help='the path(s) to the 4D dataset (can be multiple paths separated by space)')
my_parser.add_argument('-d', '--dimensions', metavar='dimension', nargs=2, type=int, required=True,
                       help='dimensions of the dataset (without including the flyback pixel) e.g. 640 640')

# Execute the parse_args() method
args = my_parser.parse_args()

input_paths = [Path(x) for x in args.paths]
input_dims = args.dimensions

for i, path in enumerate(input_paths):
    print(f"the path {i + 1} is {path}")

    if not path.exists():
        print('The path specified does not exist')
        sys.exit()

    print(input_dims)
reshaped_path = path.with_name(path.name + '_reshaped.hspy')
converted_path = reshaped_path.with_suffix('.zspy')
corrected_path = converted_path.with_name(converted_path.stem+ '_corrected.zspy')




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