#!/usr/bin/python3

import os
import datetime
from multiprocessing import Process
import subprocess


class RunWithPerformance:
    """
    Runs given shell command and stores perfomance data.
    Performance data is stored in given output directory or in
    current working directory.

    Files created
    -------------
    _times.out : time_if parameter
        start and end time
    _performance.out : performance parameter
        pidstat output
    _stdout.out, _stderr.out : std parameter
        command's stdout and stderr outputs
    """
    def __init__(self,
                 command=None,
                 output_directory=None,
                 time_it=True,
                 std=True,
                 performance=True,
                 perf_seconds=60,
                 **kwargs):  # Other not used parameters
        assert command
        assert type(command) is str, command

        self.command = command
        if output_directory:
            self.output_directory = os.path.abspath(output_directory)
        else:
            self.output_directory = os.getcwd()
        self.time_it = time_it
        # self.std = std
        self.performance = performance
        self.perf_seconds = perf_seconds
        #
        o = self.output_directory
        self._times = os.path.join(o, '_times.out')
        self._performance = os.path.join(o, '_performance.out')
        if self.std:
            self._stdout = os.path.join(o, '_stdout.out')
            self._stderr = os.path.join(o, '_stderr.out')
        else:
            self._stdout = None
            self._stderr = None

    def _run_command(self):
        subprocess.call(self.command, stdout=self._stdout, stderr=self._stderr)

    def _run_pidstat(self):
        # pid = os.getpid()
        pid = self._p_run.pid
        cmd = 'pidstat {} -rud -p {}'.format(self.perf_seconds, pid)
        subprocess.call(cmd, stdout=self._performance)

    def run(self):
        if self.time_it:
            with open(self._times, 'w') as f:
                f.write("started: %s\n".format(
                    datetime.datetime.now().isoformat()))

        self._p_run = Process(target=self._run_command)
        self._p_run.run()

        if self.performance:
            self._p_pidstat = Process(target=self._run_pidstat)
            self._p_pidstat.run()

        self._p_run.join()

        if self.performance:
            self._p_pidstat.terminate()

        if self.time_it:
            with open(self._times, 'a') as f:
                f.write("ended: %s\n".format(
                    datetime.datetime.now().isoformat()))


if __name__ == '__main__':
    import sys
    import yaml
    with open(sys.argv[1], "r") as f:
        data = yaml.load(f, yaml.CLoader)
    RunWithPerformance(**data).run()
