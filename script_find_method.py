#!/usr/bin/env python3

from os import listdir
import os
import re
import sys
from argparse import ArgumentParser
import random
import subprocess
from math import sqrt
import ast
from itertools import islice
import pickle


def get_argument():
    parser = ArgumentParser()
    parser.add_argument("-d", "--dir", dest="myDirVariable",
                        help="Choose dir", metavar="DIR", required=True)
    parser.add_argument("--verbose", help="increase output verbosity", action="store_true")

    args = parser.parse_args()
    return(args)

def find_reduced_text(i):
    list_of_method = []
    string = []
    reduced_text = []
    with open(i, encoding='iso8859-1') as f:
        string = f.read()
        k = int(string.find('INPUT FILE'))
        j = int(string.find('****END OF INPUT****'))
        reduced_text = string[k : j]
    #print(reduced_text)
    return(reduced_text)

if __name__ == '__main__':
    args = get_argument()
    list_of_file = []
    files = listdir(args.myDirVariable)
    for line in files:
        line = line.rstrip()
        if re.search('test_output', line):
            list_of_file.append(line)
    number_of_file = len(list_of_file)

    print("Number of file for analysis:", number_of_file)
    list_of_all_basis = []
    points_all = []
    reduced_text = []
    print(list_of_file)

    for file in list_of_file:
        reduced_text = find_reduced_text(file)
        #print(list_of_file)
        #print(reduced_text)


    with open('workfile','w') as f:
            f.write(reduced_text)
    #print(reduced_text)

    with open('workfile', 'r') as f:
        for line in f:
            if '> !' in line:
                if 'lpno-ccsd' in line:
                    #print(line)
                    for line in f:
                        if 'mrcc on' in line:
                            print('There is mrcc on')
                            for line in f:
                                if 'mrcctype mkcc' in line:
                                    print('LPNO-MkCCSD')
                                if 'mrcctype BWCC' in line:
                                    print('LPNO-BWCCSD')

                        if 'mrcc off' in line:
                            print("LPNOCCSD")
                if ' ccsd ' in line:
                    print('ccsd')
                    for line in f:
                        if 'mrcc on' in line:
                            for line in f:
                                if 'mrcctype mkcc' in line:
                                    print('MkCCSD')
                                if 'mrcctype BWCC' in line:
                                    print('BWCCSD')
                        if 'mrcc off' in line:
                            print('CCSD')
