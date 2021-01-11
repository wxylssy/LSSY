#! /usr/bin/python3
import subprocess

def o(cmd):
    print(subprocess.check_output(cmd, shell=True).decode())

if __name__ == "__main__":
    o('sudo pip3 install redis')
    o('sudo pip3 install baostock')
    o('sudo pip3 install pytdx')
    o('sudo pip3 install akshare')
    o('sudo pip3 install pycryptodome')
    o('sudo pip3 install plotly')

