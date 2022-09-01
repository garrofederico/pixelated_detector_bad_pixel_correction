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


def get_args():
    # Create the parser
    parser = argparse.ArgumentParser(
        description='Corrects the bad pixels of a pixem 4D dataset and outputs a .zspy file')
    # Add the arguments
    parser.add_argument('-p', '--paths', metavar='path/to/dataset(s)', nargs='+', type=str, required=True,
                        help='the path(s) to the 4D dataset (can be multiple paths separated by space)')
    parser.add_argument('-d', '--dimensions', metavar='dimension', nargs=2, type=int, required=True,
                        help='dimensions of the dataset (without including the flyback pixel) e.g. 640 640')

    # Execute the parse_args() method
    args = parser.parse_args()
    return args

# TODO: Refactor: use a library to time code or use a decorator to avoid copies

def main():
    args = get_args()
    input_paths = [Path(x) for x in args.paths]
    input_dims = args.dimensions

    total_time_start = datetime.datetime.now()
    for i, path in enumerate(input_paths):
        print(f"the path {i + 1} is {path}")

        if not path.exists():
            print('The path specified does not exist')
            sys.exit()

        # Reshape the dataset to the right format
        reshaped_path = path.with_name(path.name + '_reshaped.hspy')

        start_time = datetime.datetime.now()
        print(f'Reshaping dataset... ({start_time})')
        if reshaped_path.exists():
            reshaped_path.unlink(missing_ok=True)

        save_signal(str(path), str(reshaped_path), input_dims[0], input_dims[1], 1)
        end_time = datetime.datetime.now()
        print(f'Reshaping done! (it took {end_time - start_time})')

        # Convert reshaped dataset to .zspy format
        converted_path = reshaped_path.with_suffix('.zspy')
        print(f'Converting to .zspy format... ({start_time})')
        start_time = datetime.datetime.now()
        # Load the reshaped dataset
        dp = hs.load(str(reshaped_path), lazy=True)

        dp.save(converted_path)
        end_time = datetime.datetime.now()
        print(f'Converting done! (it took {end_time - start_time})')

        # fix the bad pixels
        start_time = datetime.datetime.now()
        dp = hs.load(converted_path, lazy=True)
        print(f'Finding dead pixels... ({start_time})')
        s_dead_pixels = dp.find_dead_pixels(dead_pixel_value=0)
        end_time = datetime.datetime.now()
        print(f'Done! (it took {end_time - start_time})')

        start_time = datetime.datetime.now()
        print(f'Finding hot pixels... ({start_time})')
        s_hot_pixels = dp.find_hot_pixels(show_progressbar=True, threshold_multiplier=10)
        end_time = datetime.datetime.now()
        print(f'Done! (it took {end_time - start_time})')

        # correct for bad pixels (dead and hot)
        start_time = datetime.datetime.now()
        print(f'Correcting bad pixels... ({start_time})')
        dp.correct_bad_pixels(s_dead_pixels + s_hot_pixels, show_progressbar=True, inplace=True, lazy_result=True)
        end_time = datetime.datetime.now()
        print(f'Done! (it took {end_time - start_time})')

        # save the corrected dataset
        corrected_path = converted_path.with_name(converted_path.stem + '_corrected.zspy')
        start_time = datetime.datetime.now()
        print(f'Saving corrected dataset... ({start_time})')
        dp.save(corrected_path)
        end_time = datetime.datetime.now()
        print(f'Done! (it took {end_time - start_time})')

        # remove reshaped intermediate
        reshaped_path.unlink()
        converted_path.unlink()
    # Calculate total time
    end_time = datetime.datetime.now()
    print(f'Complete processing done! Total time: {end_time - total_time_start}')


if __name__ == '__main__':
    main()
