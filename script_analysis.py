#!/usr/bin/env python3

import os
from argparse import ArgumentParser
from itertools import product
from collections import defaultdict

method_list_LPNO = ['LPNO-MkCCSD', 'LPNO-BWCCSD', 'LPNOCCSD']
method_list_canonical = ['MkCCSD', 'BWCCSD', 'CCSD']
dictionary_lpno_and_can = {'LPNO-MkCCSD': 'MkCCSD', 'LPNO-BWCCSD': 'BWCCSD', 'LPNOCCSD': 'CCSD'}


class Point:
    def __init__(self):
        self.geom1 = -10
        self.e_tot = 10000
        self.e_scf = 10000
        self.basis = ''
        self.aux_basis = ''
        self.t_cut_pno = 3.3e-7
        self.t_cut_pairs = 1.0e-4
        self.method = ''
        self.count = 100

    @property
    def e_corr(self):
        return self.e_tot - self.e_scf

    def print_energy(self):
        print('Angle {} \t E_tot {:10.3f}\t E_scf {:10.3f}\t E_corr {:10.3f}'.format(
            self.geom1, self.e_tot, self.e_scf, self.e_corr))
        print('TCutPNO {:e}'.format(self.t_cut_pno))
        print('Fraction_of_corr_energy {}'.format(self.count))
        print('Method {}'.format(self.method))

    def print_parameters_of_calculation(self):
        print('Use basis {}'.format(self.basis))
        print('AuxBasis {}'.format(self.aux_basis))
        print('TCutPairs {}'.format(self.t_cut_pairs))


def get_argument():
    parser = ArgumentParser()
    parser.add_argument("-d", "--dir", dest="mydirvariable",
                        help="Choose dir", metavar="DIR", required=True)
    parser.add_argument("--verbose", help="increase output verbosity", action="store_true")

    return parser.parse_args()


def find_clean_epsilon_and_twist(filename, points):
    numbers = []
    angles = []
    with open(filename, encoding='iso8859-1') as f:
        for line in f:
            if 'CleanEpsilon0' in line:
                numbers.append(float(line[16:])),
            if 'TWIST  :' in line:
                angles.append(float(line[23:]))

    if len(numbers) == len(angles):
        for number, angle in zip(numbers, angles):
            point = Point()
            point.e_tot = number
            point.geom1 = angle
            points.append(point)
    else:
        print("Error in number of angles or energies")


def find_basis(filename, points):
    bases = 'no base'
    with open(filename, encoding='iso8859-1') as f:
        for line in f:
            if 'Your calculation utilizes' in line:
                bases = line[line.index(":") + 2:].strip()
    for point in points:
        point.basis = bases


def find_cutpno(reduced_text, points):
    for point in points:
        if point.method in method_list_canonical:
            point.t_cut_pno = -1
        else:
            for line in reduced_text.split('\n'):
                if 'tcutpno' in line:
                    point.t_cut_pno = float(line[line.index('tcutpno') + len('tcutpno') + 1:])
                    break


def find_cutpairs(reduced_text, points):
    value_cutpairs = 0
    for line in reduced_text.split('\n'):
        if '> tcutpairs' in line:
            value_cutpairs = int(line[line.index('> tcutpairs') + len('> tcutpairs') + 1:])

    for point in points:
        point.t_cut_pairs = value_cutpairs


def find_scf_energy(filename, points):
    scf_energies = []
    with open(filename, encoding='iso8859-1') as f:
        for line in f:
            if 'Total Energy ' in line:
                scf_energies.append(float(line[20:line.index('Eh')]))

    for point, energy in zip(points, scf_energies):
        point.e_scf = energy


def find_auxbasis(filename, points):
    auxbases = 'not given'
    with open(filename, encoding='iso8859-1') as f:
        for line in f:
            if 'Auxbasis "' in line:
                auxbases = line[line.index('"') + 1:len(line) - 2]
                break

    for point in points:
        point.aux_basis = auxbases


def print_points(points):
    for point in points:
        point.print_energy()
        point.print_parameters_of_calculation()
        print('')


def find_reduced_text(filename):
    with open(filename, encoding='iso8859-1') as f:
        string = f.read()
        k = string.find('INPUT FILE')
        j = string.find('****END OF INPUT****')
        return string[k: j]


def find_method(reduced_text, points):
    prefix1 = ''
    prefix2 = ''
    lines = reduced_text.split('\n')
    for line in lines:
        if '> !' in line:
            if 'lpno-ccsd' in line:
                prefix1 = 'LPNO-'
            elif ' ccsd ' in line:
                prefix1 = ''
            else:
                raise NotImplementedError('Invalid method.')
        elif 'mrcc on' in line:
            for line2 in lines:
                if 'mrcctype mkcc' in line2:
                    prefix2 = 'Mk'
                    break
                elif 'mrcctype BWCC' in line2:
                    prefix2 = 'BW'
                    break
                elif 'mrcctype' in line2:
                    raise NotImplementedError('Unkwnown mrcctype.')
            else:
                raise RuntimeError('mrcctype is required if mrcc on is used.')

    method_name = prefix1 + prefix2 + 'CCSD'

    for point in points:
        point.method = method_name


def count_correlation_energy(points):
    points_all_lpno = [p for p in points if p.method in method_list_LPNO]
    points_all_canonical = [p for p in points if p.method in method_list_canonical]

    for point1 in points_all_lpno:
        for point2 in points_all_canonical:
            if point1.method == 'LPNO-' + point2.method and \
                            point1.basis == point2.basis and \
                            point1.geom1 == point2.geom1:
                point1.count = point1.e_corr / point2.e_corr


def prepare_data_for_plot(basis_list, method_list, tcutpno_list, points_all, args):
    data = defaultdict(list)
    for p in points_all:
        if p.t_cut_pno != -1:
            data[(p.basis, p.method, p.t_cut_pno)].append(p)

    for key, points in data.items():
        print('{} {} {}: {}'.format(*key, len(points)))

        if args.verbose:
            print_points(points)

        make_result_file(*key, points)


def make_result_file(basis, method, tcutpno, points_final):
    geometries = [p.geom1 for p in points_final]
    energies = [p.e_tot for p in points_final]
    with open('result_{}_{}_{:e}'.format(basis, method, tcutpno), 'w') as f:
        f.write('{:10s}'.format('Geometry'))
        for geometry in geometries:
            f.write('{:10}'.format(geometry))
        f.write('\n')
        f.write('{:10s}'.format('Energy'))
        for energy in energies:
            f.write('{:10.3f}'.format(energy))


def main():
    args = get_argument()
    files = [os.path.join(args.mydirvariable, filename) for filename in os.listdir(args.mydirvariable) if
             filename.startswith('output')]
    points_all = []
    for file in files:
        points = []
        find_clean_epsilon_and_twist(file, points)
        find_auxbasis(file, points)
        find_basis(file, points)
        reduced_text = find_reduced_text(file)
        find_method(reduced_text, points)
        find_cutpairs(reduced_text, points)
        find_cutpno(reduced_text, points)
        find_scf_energy(file, points)

        points_all += points

    count_correlation_energy(points_all)

    basis_list = {p.basis for p in points_all}
    method_list = {p.method for p in points_all}
    tcutpno_list = {p.t_cut_pno for p in points_all if p.t_cut_pno != -1}

    prepare_data_for_plot(basis_list, method_list, tcutpno_list, points_all, args)


if __name__ == '__main__':
    main()
