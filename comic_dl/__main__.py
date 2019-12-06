import sys

from commands import CommandUtility


argv = sys.argv
with CommandUtility(argv) as c:
    c.execute()
