#!/usr/bin/env python3
import sys

from commands import CommandUtility


def main():
    with CommandUtility(sys.argv) as c:
        c.execute()

# todo: comment code


if __name__ == '__main__':
    main()
