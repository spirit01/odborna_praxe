#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from os import listdir
import os
import re
import sys
from argparse import ArgumentParser
import random
import subprocess
from math import sqrt
import ast

class Point:
   def __init__(self, Geom1 = -10, E_tot = 10000, E_scf = 10000, E_corr = 0, Basis="", AugBasis="", TCutPNO=3.3e-7, TCutPairs=1.0e-4):
         self.Geom1 = Geom1
         self.E_tot = E_tot
         self.E_scf = E_scf
         self.E_corr = E_corr
         self.Basis = Basis
         self.AugBasis = AugBasis
         self.TCutPNO = TCutPNO
         self.TCutPairs = TCutPairs

   def CalcE_corr(self):
       self.E_corr = self.E_tot - self.E_scf

   def Print_energy(self):
       print("Angle \t"+  str(self.Geom1) + " \t Etot  \t" + str(self.E_tot))

   def Print_parametrs_of_calculation(self):
       print("Use basis \t" + self.Basis)
       print("TCutPNO \t" + str(self.TCutPNO))


def get_argument():
    parser = ArgumentParser()
    parser.add_argument("-d", "--dir", dest="myDirVariable",
                        help="Choose dir", metavar="DIR", required=True)

    args = parser.parse_args()

    return(args)

def find_clean_epsilon_and_twist(i):
    number=[]
    angle=[]
    c = Point()
    points = []
    with open (i, "r") as f:
        for line in f:
            if 'CleanEpsilon0' in line:
                #energy=re.findall('[CleanEpsilon0]* \d+', line)
                #energy = float(line[line.index(b'is')+1:15])
                #i = str.find("CleanEpsilon0 is", line)
                #k = str.find
                number.append(float(line[16:])),
                #print(number)
            if 'TWIST  :' in line:
                angle.append(float(line[23:]))
                #print(angle)
    if(len(number)) == len(angle):
        #print ("equal")
        for i in range(len(number)):
            #c = Point()
            c.E_tot = number[i]
            c.Geom1 = angle[i]
            points.append(c)
    else:
        print("Error in number of angle or energy")
    for point in points:
        point.Print_energy()
    return(points)


def find_basis(i,points):
    #file = listdir(args.myDirVariable)
    #c = Point()
    #points = []
    bases = []
    with open(i,"r") as f:
        for line in f:
            if 'Your calculation utilizes polarization functions from the basis:' in line:
                #print("HERE")
                bases = line[65:]
                #print(bases)
                #c = Point()
                #c.Basis = bases
                #points.append(c)
    for point in points:
        point.Basis = bases
        #print(len(points))
    #point.Print_parametrs_of_calculation()
    return(points)

def find_cutpno(i, points):
    #c = Point()
    #points = []
    value_cutpno = []
    with open(i,"r") as f:
        for line in f:
            if '| 43> ' in line:
                value_cutpno = line[14:]
    for point in points:
        point.TCutPNO =  value_cutpno
        #print(len(points))
    point.Print_parametrs_of_calculation()
    return(points)
#def find_cutpairs():



if __name__ == '__main__':
    args=get_argument()
    list_of_file = []
    print(args)
    files = listdir(args.myDirVariable)
    print(files)

    for line in files:
        line = line.rstrip()
        if re.search('test_.', line):
            list_of_file.append(line)
    number_of_file = len(list_of_file)
    print("Number of file for analysis:", number_of_file)

    for i in list_of_file:
        points = find_clean_epsilon_and_twist(i)

        find_basis(i, points)
        find_cutpno(i,points)
