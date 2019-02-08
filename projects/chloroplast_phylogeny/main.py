import os
import argparse
import subprocess
import yaml
from Bio import Entrez, SeqIO
from inverted_repeats import find_chloroplast_irs
from genes import extract_genes

Entrez.email = "ante.turudic@gmail.com"


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description="""
Reproduces steps used to produce final result (of the paper?).

Script has to be run from a directory that contains input data,
a file (default: accessions.txt) that contains list of NCBI accession numbers.
Steps create data and store it in current directory. Steps mostly create
subdirectory for it's output.

Script can run all steps at once (switch -a/--all) or some of steps.
Each step is described by switch(es) used to run step separately.

Steps:
- Download chloroplast genomes in GenBank format.
  Data stored in subdirectory sequences.
  Switches: -s/--sequences

- Finding location of inverted regions.
  Data stored in subdirectory parts.
  Switches: -parts/--parts

""")


#
parser.add_argument('--accessions', default='accessions.txt',
                    help='Filename with list of accessions')


# Steps
parser.add_argument('-a', '--all', action='store_true', default=False,
                    help='Process all steps')
parser.add_argument('-s', '--sequences', action='store_true', default=False,
                    help='Step: download chloroplast genomes')
parser.add_argument('--fasta', action='store_true', default=False,
                    help='Step: store fasta files')

parser.add_argument('-p', '--parts', action='store_true', default=False,
                    help='Step: Find chloroplast DNA structure')

parser.add_argument('-g', '--genes', action='store_true', default=False,
                    help='Step: Extract list of genes')

parser.add_argument('--gb-dir', default='sequences',
                    help='Directory with GenBank files')

#
params = parser.parse_args()


_genbank_f = (params.gb_dir, 'gb')
_fasta_f = ('fasta', 'fa')
_parts_f = ('parts', 'yml')
_genes_f = ('genes', 'txt')


def ensure_directory(d):
    if d == '':  # Current directory
        return
    if not os.path.exists(d):
        os.makedirs(d)
    else:
        if os.path.isfile(d):
            raise OSError(
                "Can't create directory, file exists with same name (%s)!" % d)


def silent_remove_file(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise


#
def _result_filename(accession, dir_, ext):
    # Returns result filename
    return os.path.join(dir_, '{}.{}'.format(accession, ext))


def _result_filename_check(accession, dir_, ext):
    # Returns result filename or None if filename exists
    filename = _result_filename(accession, dir_, ext)
    if os.path.exists(filename):
        return

    ensure_directory(os.path.dirname(filename))
    return filename


def _download_genbank(accession):
    filename = _result_filename_check(accession, *_genbank_f)
    if filename:
        print('Fetching GenBank for accession {}.'.format(accession))
        with Entrez.efetch(db="nuccore",  id=str(accession),
                           rettype="gb", retmode="text") as handle:
            with open(filename, 'w') as f:
                f.write(handle.read())


#
def _genbank_2_fasta(gb_filename, fa_filename):
    with open(gb_filename) as gb:
        with open(fa_filename, 'w') as fa:
            sequences = list(SeqIO.parse(gb, "genbank"))
            for seq_record in sequences:
                fa.write(">%s %s\n%s\n" % (
                       seq_record.id,
                       seq_record.description,
                       seq_record.seq))
    return sequences


def _find_dna_parts(accession):
    parts_filename = _result_filename_check(accession, *_parts_f)
    if parts_filename:
        print('Finding inverted repeats {}.'.format(accession))
        gb_filename = _result_filename(accession, *_genbank_f)
        fa_filename = '_tmp.fa'
        sequences = _genbank_2_fasta(gb_filename, fa_filename)
        sequence = sequences[0]
        repeats = find_chloroplast_irs(fa_filename, len(sequence))
        silent_remove_file(fa_filename)
        #
        if repeats:
            # ToDo: Naci pocetak gena ycf1 kojim pocinje IRb, tu cemo sjeci
            # Find start of gene ycf1 that start IRb part.
            cut_position = repeats.second_start - repeats.length
            for feature in sequence.features:
                if feature.type == 'gene' and 'ycf1' in feature.qualifiers.get('gene', []):
                    print('ycf1', cut_position, (feature.location.start, feature.location.end))
                #     if feature.location.start <= cut_position <= feature.location.end:
                #         print('   xxxx')
                if feature.type == 'gene' and feature.location.start <= cut_position <= feature.location.end:
                    print('  aaa', cut_position, (feature.location.start, feature.location.end), feature.qualifiers.get('gene'))

            with open(parts_filename, 'w') as out:
                yaml.dump(dict(
                        ira_start=repeats.first_start,
                        ira_end=repeats.first_start + repeats.length,
                        irb_start=repeats.second_start - repeats.length),
                    out, Dumper=yaml.CDumper, default_flow_style=False)
        else:
            print('No repeats found {}'.format(accession))


with open(params.accessions, 'r') as f:
    accessions = list(filter(None, (l.strip() for l in f)))

# Download sequences
if params.all or params.sequences or params.fasta:
    for acc in accessions:
        _download_genbank(acc)

if params.all or params.fasta:
    for acc in accessions:
        fa_filename = _result_filename_check(acc, *_fasta_f)
        if fa_filename:
            _genbank_2_fasta(_result_filename(acc, *_genbank_f), fa_filename)


# Find chloroplast DNA structure
if params.all or params.parts:
    for acc in accessions:
        _find_dna_parts(acc)

# Extract list of genes
if params.all or params.genes:
    ensure_directory(_genes_f[0])
    for acc in accessions:
        extract_genes(_result_filename(acc, *_genbank_f),
                      _result_filename(acc, *_genes_f))
