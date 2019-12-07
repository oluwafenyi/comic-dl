import argparse

from driver import Driver
from handlers import HandlerMixin

from exceptions import AliasNotSpecified


class CommandUtility(HandlerMixin):
    def __init__(self, argv, args=None):
        self.argv = argv
        self.args = args
        self.driver = Driver()

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        self.driver.quit()

    def execute(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('--alias', '-l', type=str)

        group = parser.add_mutually_exclusive_group()
        group.add_argument('--add', '-a', action='store', type=str)
        group.add_argument('--watched', '-w', action='store_true')
        group.add_argument('--download', '-d', action='store_true')
        group.add_argument('--issues', '-s', action='store_true')
        group.add_argument('--updates', '-u', action='store_true')
        group.add_argument('--available', '-e', action='store_true')

        download_options = parser.add_mutually_exclusive_group()
        download_options.add_argument('--issue', '-i', type=int)
        download_options.add_argument('--range', '-r', type=str)
        download_options.add_argument('--all', action='store_true')

        self.args = parser.parse_args(self.argv[1:]) \
            if not self.args else self.args

        if self.args.watched:
            self.display_watched()

        elif self.args.add:
            query = self.args.add
            self.add_comic_to_watched(query)

        elif self.args.download:
            alias = self.args.alias
            if not alias:
                raise AliasNotSpecified()

            if self.args.issue:
                self.download(alias, self.args.issue)

            elif self.args.range or self.args.all:
                self.download_issues(alias, self.args.range, all=self.args.all)

        elif self.args.updates:
            self.get_updates()

        elif self.args.available:
            alias = self.args.alias
            self.list_available(alias)
