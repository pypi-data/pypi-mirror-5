#!/usr/bin/env python3

import sys

from pyloadutils.pyload import PyloadConnection

def main():
    con = PyloadConnection()
    con.restartFailed()

if __name__ == '__main__':
    sys.exit(main())
