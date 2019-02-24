import os
import multiprocessing
import sys


def ensure_directory(d):
    if not os.path.exists(d):
        os.makedirs(d)
    else:
        if os.path.isfile(d):
            raise CreateDirectoryError("Can't create directory, file exists with same name (%s)!" % d)


input_dir = '.' if len(sys.argv) < 2 else sys.argv[1]
input_dir = os.path.abspath(input_dir)
num_threads = multiprocessing.cpu_count()

for f in os.listdir(input_dir):
    if f.endswith('.phy') and not f.startswith('concaten'):
        seq_id = f.replace('.phy', '')
        output_dir = os.path.join(input_dir, seq_id)
        ensure_directory(output_dir)
        os.chdir(output_dir)
        cmd = f"raxmlHPC-PTHREADS-AVX -s ../{f} -n {seq_id}.output -m GTRGAMMA -f a -# 1000 -x 12345 -p 12345 -T {num_threads}"
        print(f"Cmd: {cmd}")
        os.system(cmd)
