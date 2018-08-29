#!/usr/bin/python3

# Data format:

# Linux 4.4.0-134-generic (dinsdale)  08/29/2018  _x86_64_    (4 CPU)
#
# #      Time   UID       PID    %usr %system  %guest    %CPU   CPU  minflt/s  majflt/s     VSZ     RSS   %MEM   kB_rd/s   kB_wr/s kB_ccwr/s iodelay  Command
#  1535527947  1000      6172  297.06    0.00    0.00  297.06     1    206.86      0.00   28548    2204   0.02      0.00      3.92      0.00       0  sysbench

# or

# # Time        UID       PID    %usr %system  %guest   %wait    %CPU   CPU  minflt/s  majflt/s     VSZ     RSS   %MEM   kB_rd/s   kB_wr/s kB_ccwr/s iodelay  Command
# 03:23:18 PM  1000     23660  100.00   64.65    0.00    0.82  100.00     5 182166.53      0.00 43002060 41166852   7.81      0.00      0.20      0.00       0  SOAPdenovo-63me


def analyze(filename):
    file_data = open(filename)
    file_data.readline()  # Skip first line
    #
    max_cpu = None
    sum_cpu = 0
    num_cpu = 0
    max_vsz_mem = None

    for l in file_data:
        # Empty line
        if len(l) == 1:
            continue
        if l[0] == '#':
            indices = dict((k, i) for i, k in enumerate(l[1:-1].split()))
        else:
            data = l.split()
            # Check is time in int or string format
            if data[0].isdigit():
                offset = 0
            else:
                offset = 1

            # CPU
            cpu_idx = indices.get('CPU')
            if cpu_idx is not None:
                num_cpu += 1
                n_cpu = int(data[cpu_idx + offset])
                p_cpu = float(data[indices['%CPU'] + offset])
                cpu = n_cpu * p_cpu
                if max_cpu is None or max_cpu < cpu:
                    max_cpu = cpu
                sum_cpu += cpu
            #
            mem_idx = indices.get('VSZ')
            if mem_idx is not None:
                m = int(data[mem_idx + offset])
                if max_vsz_mem is None or max_vsz_mem < m:
                    max_vsz_mem = m
    #
    print('Max CPU {0:.2f}%'.format(max_cpu))
    print('Average CPU {0:.2f}%'.format(sum_cpu / num_cpu))
    print('Max memory {0:.1f} GB'.format(max_vsz_mem / (1024 * 1024)))


if __name__ == '__main__':
    import sys
    analyze(sys.argv[1])
