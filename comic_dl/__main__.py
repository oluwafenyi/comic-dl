#!/usr/bin/env python3
import sys

from commands import CommandUtility


def main():
    with CommandUtility(sys.argv) as c:
        c.execute()


if __name__ == '__main__':
    main()
