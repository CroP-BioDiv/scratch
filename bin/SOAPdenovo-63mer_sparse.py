#!/usr/bin/python3

import sys
import subprocess
import argparse


parser = argparse.ArgumentParser(description='Run sparse SOAPdenovo version')

parser.add_argument('-s', help="Config file")
parser.add_argument('-K', type=int, help="kmer")
parser.add_argument('-R', action='store_true', default=False,
                    help="resolve repeats by reads")
parser.add_argument('-p', type=int, help="n_cpu: number of cpu for use")
parser.add_argument(
    '-o', default='graph', help="outputGraph: prefix of output graph file name")
parser.add_argument(
    '-z', type=int, help="genomeSize(mandatory): estimated genome size")

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
    subprocess.call(cmd)

    # Contig
    cmd = ['SOAPdenovo-63mer', 'contig']
    if params.R:
        cmd.append('-R')
    subprocess.call(cmd)

    # Map
    cmd = ['SOAPdenovo-63mer', 'map', '-s', params.s, '-g', params.o]
    subprocess.call(cmd)

    # Scaffold
    cmd = ['SOAPdenovo-63mer', 'scaff', '-g', params.o, '-F']
    subprocess.call(cmd)
