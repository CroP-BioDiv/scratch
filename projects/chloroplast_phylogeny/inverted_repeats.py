import os.path
import subprocess

"""
Test methods for finding inverted repeats.
Used for finding IRs in chloroplast sequences.
"""

"""
Methods that search for repeats in given file.
They are implementation of different approaches.
Methods return list of repeats (Repeat object).
"""

# Probati:
#  + mummer. Brzo radi sa spajanjem
#  - IRF - Inverted Repeats Finder
#    ./irf307.linux.exe /home/ante/Agro/ZCI/Zadaci/009_GFF/sequences/NC_034826.fa 1 4 4 2 2 3000 30000 70000 -d -h -t7 70000
#    15tak sec.
#  - EMBROSS einvert
#    einverted /home/ante/Agro/ZCI/Zadaci/009_GFF/sequences/NC_034826.fa -maxrepeat 70000
#    Skrsi se na velikom parametru maxrepeat a treba imati barem 70000. Max uspio 50000
#  - self-Blast

MUMMER_BIN_DIR = '/home/ante/Programs/alignment/mummer/bin'
EMBROSS_BIN_DIR = '/home/ante/Programs/EMBROSS/bin'


class Repeat:
    def __init__(self, first_start, second_start, length, inverted=False):
        self.first_start = first_start
        self.second_start = second_start
        self.length = length
        self.inverted = inverted

    def __str__(self):
        return '<Repeat {}, {}{}, {}>'.format(
            self.first_start, self.second_start,
            '-' if self.inverted else '+', self.length)

    __repr__ = __str__

    # def join(self, b, max_gap=3):
    #     if self.inverted == b.inverted:
    #         my_end = self.first_start + self.length
    #         gap = b.first_start - my_end
    #         if gap <= max_gap:
    #             return Repeat(
    #                 self.first_start, self.second_start,
    #                 self.length + b.length + gap, inverted=self.inverted)
    #     return self


# def _exact_to_not_exact_match(
#         method, seq_filename, check_length=3000, max_gap=3):
#     # Try match with smaller min length and joins result
#     repeats = method(seq_filename, check_length)
#     print(repeats)
#     if repeats:
#         repeats.sort(key=lambda r: r.first_start)
#         result = repeats[0]
#         for r in repeats[1:]:
#             result = result.join(r, max_gap=max_gap)
#         return result

def _concatenate_repeats(repeats):
    if repeats:
        if len(repeats) == 1:
            return repeats[0]

        repeats.sort(key=lambda r: r.first_start)
        first = repeats[0]
        last = repeats[-1]
        return Repeat(
            first.first_start, first.second_start,
            last.first_start - first.first_start + last.length,
            inverted=first.inverted)


#
def mummer_exact(seq_filename, min_length=3000):
    # Note: repeat-match finds exact repeats within a single sequence.
    # To find not exact match run it with smaller min_length and concatenate results
    exe_loc = os.path.join(MUMMER_BIN_DIR, 'repeat-match')
    r = subprocess.run(
        [exe_loc, '-n', str(min_length), seq_filename],
        stdout=subprocess.PIPE)
    output = r.stdout.decode('utf-8')
    #
    res = []
    read = False
    for line in output.splitlines():
        fields = line.split()
        if read:
            if fields[1][-1] == 'r':
                s2 = int(fields[1][:-1])
                inverted = True
            else:
                s2 = int(fields[1])
                inverted = False
            res.append(Repeat(
                int(fields[0]), s2, int(fields[2]), inverted=inverted))
        else:
            if fields[0] == 'Start1':
                read = True
    return res


def mummer(seq_filename, min_length=15000):
    return _concatenate_repeats(
        mummer_exact(seq_filename, min_length=min_length//20))


def find_chloroplast_irs(seq_filename, seq_length):
    repeat = mummer(seq_filename, min_length=15000)

    if repeat:
        # Check is chloroplast sequence structured in standard way:
        # LSC, IRa, SSC, IRb

        # Is first part LSC?
        if repeat.first_start < seq_length // 2:
            raise ValueError('Wrong sequence structure, start! {} {} {}'.format(
                repeat.first_start, repeat.second_start, repeat.length))

        # Does IRb ends on sequence end?
        if repeat.second_start < seq_length - 10:  # Leave some margine
            raise ValueError('Wrong sequence structure, end! {} {} {} : {}'.format(
                repeat.first_start, repeat.second_start, repeat.length,
                seq_length))

    return repeat


#
# def embross(seq_filename, min_length=15000):
#     exe_loc = os.path.join(EMBROSS_BIN_DIR, 'einverted')


if __name__ == '__main__':
    import sys

    # Mummer svi
    for f in sys.argv[1:]:
        print(os.path.basename(f), mummer(f))
