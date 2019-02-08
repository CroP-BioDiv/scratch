#!/usr/bin/python3

import os.path
import itertools
from Bio import SeqIO
from BCBio import GFF

# Anotacije
#  - /home/ante/Programs/alignment/BAli_Phy/bali-phy-3.4.1/bin/bali-phy <fajl>
#  - Force pool za anotacije


class AnnotatedSeq:
    def __init__(self, file_id, seq_file, gff_file):
        self.file_id = file_id
        self.seq_file = seq_file
        self.gff_file = gff_file
        #
        with open(seq_file, 'r') as seq:
            self.seq_dict = SeqIO.to_dict(SeqIO.parse(seq, "fasta"))
        if len(self.seq_dict) != 1:
            print('Input file {} has more seqeuces {}!'.format(seq_file, len(self.seq_dict)))
        self.sequence = next(iter(self.seq_dict.values()))
        self.sequence_name = next(iter(self.seq_dict.keys()))

        with open(gff_file, 'r') as gff:
            # self.annotation = list(GFF.parse(gff))
            self.features = None
            for rec in GFF.parse(gff, base_dict=self.seq_dict):
                if self.features is None:
                    self.record = rec
                    self.features = rec.features
                else:
                    print('More records in GFF file!')

        self._id_2_feature = dict((f.id, (i, f)) for i, f in enumerate(self.features) if f.type == 'gene')

    def num_features(self):
        return len(self._id_2_feature)

    def all_features(self):
        return set(self._id_2_feature.keys())

    def num_genes(self):
        return len(self.all_genes())

    def all_genes(self):
        genes = set(self._id_2_feature.keys())
        # For chloroplast genomes
        genes.difference_update(('IRA', 'IRB', 'LSC', 'SSC'))
        return genes

    def extract_feature(self, feature):
        feature = self._id_2_feature.get(feature)
        if feature:
            seq = feature[1].extract(self.sequence)
            return str(seq.seq)

    def extract_features(self, features):
        ret = ''
        for f in features:
            s = self.extract_feature(f)
            if s:
                ret += s
        return ret


def common_genes(annotated_files):
    ret = annotated_files[0].all_genes()
    for a in annotated_files[1:]:
        ret &= a.all_genes()
    return sorted(ret)


def common_features(annotated_files):
    ret = annotated_files[0].all_features()
    for a in annotated_files[1:]:
        ret &= a.all_features()
    return sorted(ret)


def ensure_directory(d):
    if not os.path.exists(d):
        os.makedirs(d)
    else:
        if os.path.isfile(d):
            raise CreateDirectoryError(
                "Can't create directory, file exists with same name (%s)!" % d)


def _write_seq(output_dir, a, feature):
    # Writes one or more sequences
    if isinstance(feature, str):
        seq = a.extract_feature(feature)
    else:
        seq = a.extract_features(feature)
    if seq:
        ensure_directory(output_dir)
        output_file = os.path.join(output_dir, a.file_id + '.fa')
        with open(output_file, 'w') as output:
            output.write('>{}\n'.format(a.sequence_name))
            output.write(seq)
            output.write('\n')


def _extract_features_concatenate(output_dir, annotated_files, extract_features):
    for a in annotated_files:
        _write_seq(output_dir, a, extract_features)


def _extract_features_separate(output_dir, annotated_files, extract_features):
    for feature in extract_features:
        d = os.path.join(output_dir, feature)
        for a in annotated_files:
            _write_seq(d, a, feature)


# --------------------------------------------------------
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Extract genome data from annotated genomes.")

    # Input
    parser.add_argument('-S', '--sequence-dir', default='seq_files', help='Directory with sequence files')
    parser.add_argument('--sequence-ext', default='fsa', help='Sequence file extension')
    parser.add_argument('-G', '--gff-dir', default='gff3_files', help='Directory with gff files')
    parser.add_argument('--gff-ext', default='gff3', help='GFF file extension')
    # Output
    parser.add_argument('-O', '--output-dir', default='output_files', help='Directory with output files')

    # Info
    parser.add_argument('-N', '--num-genes', action='store_true', help='Print number of genes in genomes')
    parser.add_argument('-F', '--num-features', action='store_true', help='Print number of features in genomes')
    parser.add_argument('-C', '--common-genes', action='store_true', help='Print common genes in genomes')
    # Extract
    parser.add_argument('-l', '--extract-features', help='Extract feature(s). Comma separated.')
    parser.add_argument('-g', '--extract-common-genes', action='store_true', help='Extract common genes into a directory')
    parser.add_argument('-f', '--extract-common-features', action='store_true', help='Extract common features into a directory')
    parser.add_argument('-a', '--extract-all-genes', action='store_true',
                        help='Extract all genes in different subdirectories')
    parser.add_argument('-b', '--extract-all-features', action='store_true',
                        help='Extract all features in different subdirectories')

    params = parser.parse_args()

    # Read data
    annotated_files = []
    sequence_ext = '.' + params.sequence_ext
    gff_ext = '.' + params.gff_ext
    cut = -len(sequence_ext)

    for seq in os.listdir(params.sequence_dir):
        if seq.endswith(sequence_ext):
            base_file = seq[:cut]
            gff = os.path.join(params.gff_dir, base_file + gff_ext)
            if os.path.isfile(gff):
                annotated_files.append(
                    AnnotatedSeq(base_file, os.path.join(params.sequence_dir, seq), gff))
            else:
                print('No gff file {}!'.format(gff))

    if not annotated_files:
        print('No input data!')
        sys.exit(0)

    # Execute something
    if params.num_features:
        print('Number of features per sequence:')
        for a in sorted(annotated_files, key=lambda x: x.file_id):
            print('{:>4}  {}'.format(a.num_features(), a.file_id))

    if params.num_genes:
        print('Number of genes per sequence:')
        for a in sorted(annotated_files, key=lambda x: x.file_id):
            print('{:>4}  {}'.format(a.num_genes(), a.file_id))

    if params.common_genes:
        genes = common_genes(annotated_files)
        print('Number of same genes {}.'.format(len(genes)))
        print(genes)

    if params.extract_features:
        _extract_features_concatenate(params.output_dir, annotated_files, params.extract_features.split(','))

    if params.extract_common_genes:
        _extract_features_concatenate(params.output_dir, annotated_files, common_genes(annotated_files))

    if params.extract_common_features:
        _extract_features_concatenate(
            params.output_dir, annotated_files, common_features(annotated_files))

    if params.extract_all_genes:
        _extract_features_separate(params.output_dir, annotated_files, common_genes(annotated_files))

    if params.extract_all_features:
        _extract_features_separate(params.output_dir, annotated_files, common_features(annotated_files))
