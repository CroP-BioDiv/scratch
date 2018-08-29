#!/usr/bin/python3

import sys
import subprocess
import argparse


parser = argparse.ArgumentParser(description='Run sparse SOAPdenovo version')

parser.add_argument('-s', description="Config file")
parser.add_argument('-K', type='int', description="kmer")
parser.add_argument('-R', action='store_true', default=False,
                    description="resolve repeats by reads")
parser.add_argument(
    '-p', type='int', description="n_cpu: number of cpu for use")
parser.add_argument(
    '-o', default='graph',
    description="outputGraph: prefix of output graph file name")
parser.add_argument(
    '-z', type='int',
    description="genomeSize(mandatory): estimated genome size")

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
