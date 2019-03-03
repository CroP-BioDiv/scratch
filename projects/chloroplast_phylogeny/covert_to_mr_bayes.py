import os
from Bio import AlignIO, Alphabet

_NEXUS_DATA = """
begin mrbayes;
set autoclose=yes nowarn=yes autoreplace=no;
lset Nst=6 Rates=gamma;
mcmcp ngen=10000000 printfreq=1000 samplefreq=1000 nchains=4
savebrlens=yes filename={filename};
mcmc;
sumt filename={filename} burnin=2500 contype=halfcompat;
end;

"""


def ensure_directory(d):
    if not os.path.exists(d):
        os.makedirs(d)
    else:
        if os.path.isfile(d):
            raise CreateDirectoryError("Can't create directory, file exists with same name (%s)!" % d)


def convert(alignment_dir, bayes_dir):
    ensure_directory(bayes_dir)
    for f in os.listdir(alignment_dir):
        if f.endswith('.phy'):
            alignment = os.path.join(alignment_dir, f)
            prefix = f.replace('.phy', '')
            bayes = os.path.join(bayes_dir, prefix + '.nex')
            AlignIO.convert(alignment, 'phylip', bayes, 'nexus', alphabet=Alphabet.generic_dna)
            # Add
            with open(bayes, 'a') as output:
                output.write(_NEXUS_DATA.format(filename=prefix))


if __name__ == '__main__':
    import sys
    alignment_dir = sys.argv[1]
    bayes_dir = sys.argv[2]
    convert(alignment_dir, bayes_dir)
