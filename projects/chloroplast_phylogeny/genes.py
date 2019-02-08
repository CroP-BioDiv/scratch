from Bio import SeqIO


def extract_genes(gb_filename, output_filename):
    genes = []
    with open(gb_filename) as gb:
        for sequence in SeqIO.parse(gb, "genbank"):
            for feature in sequence.features:
                if feature.type == 'gene':
                    genes.append(feature)

    # for feature in genes:
    #     print(feature.qualifiers.get('gene'), feature.location)
    diff_gene_names = set()
    for feature in genes:
        qs = feature.qualifiers.get('gene')
        if qs:
            diff_gene_names.add(qs[0])

    print(output_filename, len(genes), len(diff_gene_names))
    with open(output_filename, 'w') as f:
        f.write('\n'.join(diff_gene_names))
