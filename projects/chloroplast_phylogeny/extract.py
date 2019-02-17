#!/usr/bin/python3

import os
import itertools
from Bio import SeqIO
from BCBio import GFF

_MUSCLE_EXE = '/home/ante/Programs/alignment/MUSCLE/muscle3.8.31/muscle'
_CLUSTALO_EXE = '/home/ante/bin/clustalo'


def _align(job_ind, input_file, output_dir):
    _, output_file = os.path.split(input_file)
    # Muscle
    # output_file = os.path.join(output_dir, output_file)
    # cmd = f"{_MUSCLE_EXE} -in {input_file} -out {output_file}"
    # Clustalo
    output_file = os.path.join(output_dir, output_file.replace('.fa', '.phy'))
    # --threads=n
    cmd = f"{_CLUSTALO_EXE} -i {input_file} -o {output_file} --outfmt=phy"
    print(f"Job {job_ind} started: {cmd}")
    os.system(cmd)


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
        sequence_name = next(iter(self.seq_dict.keys()))
        # Artemisia_annua_Anthemideae_Asteroideae_Asteraceae_Asterales_NC034683_GenBank -> NC034683
        # Tanacetum_cinerariifolium_Anthemideae_Asteroideae_Asteraceae_Asterales_ZCI0001_ZCI -> ZCI_0001
        nc_num = sequence_name.split('_')[-2]
        self.sequence_name = ('NC_' + nc_num[2:]) if nc_num.startswith('NC') else ('ZCI_' + nc_num[3:])

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
        assert isinstance(features, (list, tuple)), type(features)
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


def _write_sequences(output_file, annotated_files, features, index_file=None):
    # Writes one or more sequences
    data = [[] for _ in annotated_files]  # By input files
    output_features = []
    for f in features:
        seqs = [a.extract_feature(f) for a in annotated_files]
        lens = list(map(len, seqs))
        if min(lens) * 2 < max(lens):  # 1.5 izbaci jos atpB, 1.3 izbaci jos psbT
            print('Sequences have quite different lengths', f, lens)
        elif max(lens) == 0:
            print('All sequences are empty quite different lengths', f)
        else:
            output_features.append(f)
            for d, seq in zip(data, seqs):
                # data.append('>' + a.sequence_name)
                d.append(seq)

    if data[0]:
        with open(output_file, 'w') as output:
            for a, d in zip(annotated_files, data):
                output.write('>{}\n'.format(a.sequence_name))
                output.writelines("%s\n" % l for l in d)
        if index_file:
            with open(index_file, 'w') as output:
                for a, d in zip(annotated_files, data):
                    last_ind = 1
                    for f, seq in zip(output_features, d):
                        next_ind = last_ind + len(seq) - 1
                        output.write(f"{a.sequence_name} {f} {last_ind} {next_ind}\n")
                        last_ind = next_ind + 1
        return True
    return False


# --------------------------------------------------------
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Extract genome data from annotated genomes.")

    # Input
    parser.add_argument('-S', '--sequence-dir', default='seq_files', help='Directory with sequence files')
    parser.add_argument('--sequence-ext', default='fsa', help='Sequence file extension')
    parser.add_argument('-G', '--gff-dir', default='gff3_files', help='Directory with gff files')
    parser.add_argument('--gff-ext', default='gff3', help='GFF file extension')

    # Info
    parser.add_argument('-N', '--num-genes', action='store_true', help='Print number of genes in genomes')
    parser.add_argument('-F', '--num-features', action='store_true', help='Print number of features in genomes')
    parser.add_argument('-C', '--print-common-genes', action='store_true', help='Print common genes in genomes')

    # Extract
    # Features to extract
    parser.add_argument('-l', '--features', help='Extract feature(s). Comma separated.')
    parser.add_argument('-g', '--common-genes', action='store_true', help='Extract common genes')
    parser.add_argument('-f', '--common-features', action='store_true', help='Extract common features')
    # How and where to save
    parser.add_argument('-s', '--in-separate-files', help='Directory for separate files')
    parser.add_argument('-o', '--output-file', default='output.fa', help='Output file for concatenated data')
    parser.add_argument('-i', '--index-file', default='index.txt', help='Output file indexing genes')
    # Alignment
    parser.add_argument('-a', '--alignment-directory', help='Make alignment')

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

    if params.print_common_genes:
        genes = common_genes(annotated_files)
        print('Number of same genes {}.'.format(len(genes)))
        print(genes)

    # Find what to extract
    features = set()
    if params.features:
        features.update(params.features.split(','))
    if params.common_genes:
        features.update(common_genes(annotated_files))
    if params.common_features:
        features.update(common_features(annotated_files))

    # Extract
    if params.in_separate_files:
        ensure_directory(params.in_separate_files)
        sequences = []
        for f in sorted(features):
            seq_file = os.path.join(params.in_separate_files, f) + '.fa'
            if _write_sequences(seq_file, annotated_files, [f]):
                sequences.append(seq_file)
    else:
        _write_sequences(params.output_file, annotated_files, sorted(features), index_file=params.index_file)
        sequences = [params.output_file]

    if params.alignment_directory:
        ensure_directory(params.alignment_directory)
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=4) as executor:
            for job_ind, seq in enumerate(sequences):
                future = executor.submit(_align, job_ind, seq, params.alignment_directory)
