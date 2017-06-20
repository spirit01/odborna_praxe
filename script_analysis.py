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


class Point:
   def __init__(self, Geom1 = -10, E_tot = 10000, E_scf = 10000, E_corr = 5,
                Basis="", AuxBasis="", TCutPNO=3.3e-7, TCutPairs=1.0e-4):
         self.Geom1 = Geom1
         self.E_tot = E_tot
         self.E_scf = E_scf
         self.E_corr = E_corr
         self.Basis = Basis
         self.AuxBasis = AuxBasis
         self.TCutPNO = TCutPNO
         self.TCutPairs = TCutPairs

   def CalcE_corr(self):
       self.E_corr = self.E_tot - self.E_scf

   def Print_energy(self):
       print("Angle \t"+  str(self.Geom1) + " \t E_tot  \t" + str(self.E_tot)+
             "\t E_scf \t" + str(self.E_scf) + " \t E_corr \t" + str(self.E_corr))
       print("TCutPNO \t" + str(self.TCutPNO))

   def Print_parametrs_of_calculation(self):
       print("Use basis \t" + self.Basis)
       print("AuxBasis \t" + self.AuxBasis)
       print("TCutPairs \t" + str(self.TCutPairs))



def get_argument():
    parser = ArgumentParser()
    parser.add_argument("-d", "--dir", dest="myDirVariable",
                        help="Choose dir", metavar="DIR", required=True)

    args = parser.parse_args()

    return(args)

def find_clean_epsilon_and_twist(file):
    number = []
    angle = []
    points = []
    with open (file,encoding='iso8859-1') as f:
        for line in f:
            if 'CleanEpsilon0' in line:
                number.append(float(line[16:])),
            if 'TWIST  :' in line:
                angle.append(float(line[23:]))

    if(len(number)) == len(angle):
        for i in range(len(number)):
            c = Point()
            c.E_tot = number[i]
            c.Geom1 = angle[i]
            points.append(c)

    else:
        print("Error in number of angle or energy")
    return(points)


def find_basis(i,points):
    bases = []
    with open(i,encoding='iso8859-1') as f:
        for line in f:
            if 'Your calculation utilizes' in line:
                bases = line[line.index(":")+1:line.index("\n")]
    for point in points:
        point.Basis = str(bases)
    return(points)

def find_cutpno(i, points):
    with open(i,encoding = 'iso8859-1') as f:
        for line in f:
            if '| 46> tcutpno' in line:
                value_cutpno = float(line[14:])
    for point in points:
        point.TCutPNO = value_cutpno
    return(points)

def find_cutpairs(i, point):
    with open(i,encoding='iso8859-1') as f:
        for line in f:
            if 'tcutpairs' in line:
                if '#' in line:
                    print(" ")
                else:
                    value_cutpairs = float(line[16:])

                    for point in points:
                        point.TCutPairs =  value_cutpairs
    return(points)

def find_SCF_energy(i, points):
    value_SCF_energy = []
    with open(i, encoding = 'iso8859-1') as f:
        for line in f:
            if 'Total Energy ' in line:
                value_SCF_energy.append(float(line[20:line.index('Eh')]))
    i=0
    for point in points:
        point.E_scf = value_SCF_energy[i]
        i = i+1
    return(points)

def calculate_corr_E(i, points):
    for point in points:
        point.CalcE_corr()
    return(points)

def find_auxbasis(i,points):
    auxbases = []
    with open(i,encoding='iso8859-1') as f:
        for line in f:
            if '| 19> Auxbasis "' in line:
                auxbases = line[16:len(line)-2]
    for point in points:
        point.AuxBasis = auxbases

    return(points)
"""
def filter_by_basis(i, points):

    list_of_all_basis = []
    list_of_filtred_basis_631g = []
    if re.search('.6-31g.', i):
        list_of_filtred_basis.append(i)
        print(list_of_filtred_basis)

    return(points,list_of_filtred_basis)
"""
def make_list_of_basis(i,points):
    a = []
    a = (i[7:i.index("_pno")])


def print_points(points):
    for point in points:
        point.Print_energy()
        point.Print_parametrs_of_calculation()

if __name__ == '__main__':

    args = get_argument()
    list_of_file = []

    files = listdir(args.myDirVariable)
    for line in files:
        line = line.rstrip()
        if re.search('output.', line):
            list_of_file.append(line)

    number_of_file = len(list_of_file)
    print("Number of file for analysis:", number_of_file)

    points_all = []
    for file in list_of_file:

        points = find_clean_epsilon_and_twist(file)
        points = find_auxbasis(file, points)
        points = find_basis(file, points)
        points = find_cutpairs(file,points)
        points = find_cutpno(file,points)
        points = find_SCF_energy(file, points)
        points = calculate_corr_E(file, points)
        #filter_by_basis(file, points)
        points_all += points
        make_list_of_basis(file,points)
        print_points(points)
