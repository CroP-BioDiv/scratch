#!/usr/bin/python3

import os
import datetime
import multiprocessing
import subprocess
import signal


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
        assert isinstance(command, (str, list)), command

        if isinstance(command, str):
            self.commands = [command]
        else:
            self.commands = command

        if output_directory:
            self.output_directory = os.path.abspath(output_directory)
        else:
            self.output_directory = os.getcwd()
        self.time_it = time_it
        self.performance = performance
        self.perf_seconds = perf_seconds
        #
        o = self.output_directory
        self._times = os.path.join(o, '_times.out')
        self._performance = os.path.join(o, '_performance.out')
        if std:
            self._stdout = os.path.join(o, '_stdout.out')
            self._stderr = os.path.join(o, '_stderr.out')
        else:
            self._stdout = None
            self._stderr = None

    def _run_command(self, cmd):
        def f():
            if self._stdout:
                subprocess.call(cmd.split(),
                                stdout=open(self._stdout, 'w'),
                                stderr=open(self._stderr, 'w'))
            else:
                subprocess.call(cmd.split())
        return f

    def _pid_cmd(self, cmd):
        main_c = os.path.basename(cmd.split()[0])
        if len(main_c) > 10:
            main_c = '"' + main_c[:10] + '*"'
        return ['pidstat', str(self.perf_seconds),
                '-rud', '-h',
                '-C', main_c,
                '-T', 'CHILD']

    def run(self):
        if self.time_it:
            print('INFO: Writing start time!')
            with open(self._times, 'w') as f:
                f.write("started: {}\n".format(
                    datetime.datetime.now().isoformat()))

        first_cmd = True
        for cmd in self.commands:
            if self.performance:
                print('INFO: Starting pidstat!')
                _p_pidstat = subprocess.Popen(
                    self._pid_cmd(cmd),
                    stdout=open(self._performance, 'w' if first_cmd else 'a'))
                print('INFO: pidstat started!', _p_pidstat.pid)

            first_cmd = False

            print('INFO: Starting command!')
            self._p_run = multiprocessing.Process(target=self._run_command(cmd))
            self._p_run.start()
            print('INFO: Command started!', self._p_run.pid)

            self._p_run.join()
            print('INFO: Command Finished!')

            if self.performance:
                _p_pidstat.terminate()
                print('INFO: pidstat terminated!')

        if self.time_it:
            print('INFO: Writing end time!')
            with open(self._times, 'a') as f:
                f.write("ended: {}\n".format(
                    datetime.datetime.now().isoformat()))


if __name__ == '__main__':
    import sys
    import yaml
    with open(sys.argv[1], "r") as f:
        data = yaml.load(f, yaml.CLoader)
    RunWithPerformance(**data).run()
