#!/usr/bin/python3

# Executing several relevant commands for any not existing command.

from __future__ import print_function
import os

print("-------- linux info 1 --------")
os.system("grep . /etc/*-release")
print("------------------------------\n")

print("-------- linux info 2 --------")
os.system("grep . /etc/issue*")
print("------------------------------\n")

print("-------- kernel info --------")
os.system("cat /proc/version")
print("------------------------------\n")

print("-------- cpu info --------")
os.system("cat /proc/cpuinfo")
print("------------------------------\n")

print("-------- mem info --------")
os.system("cat /proc/meminfo")
print("------------------------------\n")

print("-------- gpu info 1 --------")
os.system("lshw -C video")
print("------------------------------\n")

print("-------- gpu info 2 --------")
os.system("lspci -nn | egrep 'VGA|Display'")
print("------------------------------\n")

print("-------- gpu info 3 --------")
os.system("nvidia-smi")
print("------------------------------\n")

print("-------- proccess info --------")
os.system("top -n 1 -b")
print("------------------------------\n")
