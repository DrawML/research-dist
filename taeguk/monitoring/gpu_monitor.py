#!/usr/bin/python3
import subprocess
import os
import sys
import xml.etree.ElementTree as ET

# its win32, maybe there is win64 too?
is_windows = sys.platform.startswith('win')

if is_windows:
    PYTHON2 = 'C:/Python27/python.exe'
else:
    PYTHON2 = 'python2'


class NvidiaGpuInformation(object):

    AVAILABLE_KEYS = (
        ''
    )

    def __init__(self):
        self._info = {}

    def __getitem__(self, key):
        return self._info[key]

    def __setitem__(self, key, value):
        self._info[key] = value

    def __delitem__(self, key):
        del self._info[key]


class NvidiaDeviceInformation(object):

    AVAILABLE_KEYS = (
        'gpu_count', 'gpus'
    )

    def __init__(self):
        self._info = {}
        self._gpus = []
        self._info['gpus'] = self._gpus

    def __getitem__(self, key):
        return self._info[key]

    def __setitem__(self, key, value):
        self._info[key] = value

    def __delitem__(self, key):
        del self._info[key]




def run_smi():
    SRC_DIR = os.path.dirname(os.sys.modules[__name__].__file__)
    proc = subprocess.Popen([PYTHON2, SRC_DIR + '/nvidia_smi.py'],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    return out.decode(), err.decode()


def monitor():
    pass


if __name__ == '__main__':
    out, err = run_smi()

    print('stdout : "' + out + '"')
    print('stderr : "' + err + '"')
