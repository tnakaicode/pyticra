import numpy as np
import matplotlib.pyplot as plt
import sys
import time
import os
import subprocess
import argparse


def split_filename(filename="../temp_20200408000/not_ignore.txt"):
    name = os.path.basename(filename)
    dir_name = os.path.dirname(filename)
    sub_name = os.path.basename(os.path.dirname(filename))
    rootname, ext_name = os.path.splitext(name)
    return rootname, dir_name, sub_name


if __name__ == "__main__":
    argvs = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", dest="job",
                      default="../Project/Job_01/Job_01.tor")
    opt = parser.parse_args()
    print(argc, opt)

    ticra_tool = r'ticra-tools.exe'

    root_dir = os.getcwd()
    tor_file = root_dir + opt.job
    rootname, dir_name, sub_name = split_filename(opt.job)
    print(dir_name, sub_name)
    print(rootname)

    os.chdir("{}/{}".format(root_dir, dir_name))
    subprocess.call(
        ticra_tool + " batch.gxp {}.out {}.log -nif".format(sub_name, sub_name))
    os.chdir("{}".format(root_dir))
