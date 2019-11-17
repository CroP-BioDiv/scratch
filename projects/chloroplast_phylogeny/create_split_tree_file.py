import os.path

_START = """#nexus
BEGIN taxa;
DIMENSIONS ntax=12;
TAXLABELS
'NC_034683'
'NC_031399'
'NC_031400'
'NC_034848'
'NC_020607'
'NC_025910'
'NC_030785'
'ZCI_0001'
'NC_020092'
'NC_020320'
'NC_034996'
'NC_034851'
;
END [taxa];
BEGIN trees;
"""
_END = "END [trees];"


def create_split_tree_file(input_dir, output_file):
    with open(output_file, 'w') as output:
        output.write(_START)
        for f in sorted(os.listdir(input_dir)):
            if f.startswith('concat'):
                continue
            r_dir = os.path.join(input_dir, f)
            if os.path.isdir(r_dir):
                output.write(f'Tree\n{f}=')
                with open(os.path.join(r_dir, f'RAxML_bipartitionsBranchLabels.{f}.output'), 'r') as raxml:
                    output.writelines(l for l in raxml)
        output.write(_END)


if __name__ == '__main__':
    import sys
    create_split_tree_file(sys.argv[1], sys.argv[2])
