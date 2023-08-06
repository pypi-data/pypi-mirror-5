#!python


import os
import sys
import time


def _idle():
    working = os.path.abspath(os.getcwd())
    sys.path.append(working)
    repetitions = 0
    state = 0
    while True:
        new_state = sum(_checksums(working))
        if state != new_state:
            repetitions += 1
            _display_repetitions_banner(repetitions)
            os.system('python -m pyspecs')
            state = new_state
        time.sleep(.75)


def _checksums(working):
    for root, dirs, files in os.walk(working):
        for f in files:
            if f.endswith('.py'):
                stats = os.stat(os.path.join(root, f))
                yield stats.st_mtime + stats.st_size


def _display_repetitions_banner(repetitions):
    number = ' {} '.format(repetitions)
    half_delimiter = (EVEN if not repetitions % 2 else ODD) * \
                     ((80 - len(number)) / 2)
    print '\n{0}{1}{0}\n'.format(half_delimiter, number)


EVEN = '='
ODD = '-'


if __name__ == '__main__':
    _idle()