#!/usr/bin/python3

import sys
import subprocess
import argparse


parser = argparse.ArgumentParser(description='Run sparse SOAPdenovo version')

parser.add_argument('-s', help="Config file")
parser.add_argument('-K', help="kmer")
parser.add_argument('-R', action='store_true', default=False,
                    help="resolve repeats by reads")
parser.add_argument('-p', help="n_cpu: number of cpu for use")
parser.add_argument(
    '-o', default='graph', help="outputGraph: prefix of output graph file name")
parser.add_argument(
    '-z', help="genomeSize(mandatory): estimated genome size")

params = parser.parse_args()

if not params.s or not params.z:
    print('No parameters!')
else:
    # Pregraph
    cmd = ['SOAPdenovo-63mer', 'sparse_pregraph',
           '-s', params.s,
           '-z', params.z,
           '-o', params.o]
    if params.R:
        cmd.append('-R')
    if params.K:
        cmd.extend(['-K', params.K])
    print(cmd)
    subprocess.call(cmd)

    # Contig
    cmd = ['SOAPdenovo-63mer', 'contig']
    if params.R:
        cmd.append('-R')
    print(cmd)
    subprocess.call(cmd)

    # Map
    cmd = ['SOAPdenovo-63mer', 'map', '-s', params.s, '-g', params.o]
    print(cmd)
    subprocess.call(cmd)

    # Scaffold
    cmd = ['SOAPdenovo-63mer', 'scaff', '-g', params.o, '-F']
    print(cmd)
    subprocess.call(cmd)
