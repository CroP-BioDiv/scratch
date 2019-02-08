from Bio import SeqIO
from BCBio import GFF


class AnnotatedSeq:
    def __init__(self, file_id, seq_file, gff_file):
        self.file_id = file_id
        self.seq_file = seq_file
        self.gff_file = gff_file
        #
        with open(seq_file, 'r') as seq:
            self.seq_dict = SeqIO.to_dict(SeqIO.parse(seq, "fasta"))
        self.sequence = next(iter(self.seq_dict.values()))

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
