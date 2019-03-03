import os.path
from concurrent.futures import ThreadPoolExecutor
import multiprocessing

_MR_BAYES_EXE = 'mr_bayes'
_MR_BAYES_THREADS = multiprocessing.cpu_count()


def ensure_directory(d):
    if not os.path.exists(d):
        os.makedirs(d)
    else:
        if os.path.isfile(d):
            raise CreateDirectoryError("Can't create directory, file exists with same name (%s)!" % d)


def _run(job_ind, f, run_dir):
    ensure_directory(run_dir)
    os.chdir(run_dir)
    cmd = f"{_MR_BAYES_EXE} ../{f}"
    print(f"Job {job_ind} started: {cmd}")
    os.system(cmd)


def run_mr_bayes(input_dir):
    input_dir = os.path.abspath(input_dir)

    jobs = []
    for f in os.listdir(input_dir):
        if f.endswith('.nex'):
            run_dir = os.path.join(input_dir, f.replace('.nex', ''))
            jobs.append((f, run_dir))

    if jobs:
        with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
            for job_ind, (f, run_dir) in enumerate(jobs):
                executor.submit(_run, job_ind, f, run_dir)


if __name__ == '__main__':
    import sys
    run_mr_bayes(sys.argv[1])
