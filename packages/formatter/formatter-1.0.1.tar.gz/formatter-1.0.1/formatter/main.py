import sys
import argparse
from .formatter import Formatter


def main(*argv):
    parser = argparse.ArgumentParser('Format Python files')
    parser.add_argument('files', nargs='+')
    parser.add_argument('-r', '--recursive', action='store_true',
                        help='Process directories recursively')

    argv = argv or sys.argv
    args = parser.parse_args(argv[1:])
    formatter = Formatter()
    for file_ in args.files:
        formatter.format_path(file_, args.recursive)
