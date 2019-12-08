import argparse

from common.driver import Driver
from common.exceptions import AliasNotSpecified
from handlers import HandlerMixin


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

        parser.add_argument(
            '--alias',
            '-a',
            type=str,
            help='Unique identifier for comics',
        )

        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--add',
            '-q',
            action='store',
            type=str,
            help='Finds comics based on query and adds your choice to database'
                 ' identified by specified alias',
        )
        group.add_argument(
            '--watched',
            '-w',
            action='store_true',
            help='Lists all comics in database along with alias',
        )
        group.add_argument(
            '--download',
            '-d',
            action='store_true',
            help='Downloads comic issues for comic specified by alias(-a flag)'
                 ' one of -i, -r, --all flags should be specified',
        )
        group.add_argument(
            '--issues',
            '-s',
            action='store_true',
            help='Lists available issues for comic specified by alias(-a flag)'
        )
        group.add_argument(
            '--updates',
            '-u',
            action='store_true',
            help='Lists issues for watched comics that haven\'t been'
                 ' downloaded',
        )

        download_options = parser.add_mutually_exclusive_group()
        download_options.add_argument(
            '--issue',
            '-i',
            type=int,
            help='Used with the download flag to specify issue to be '
                 'downloaded',
        )
        download_options.add_argument(
            '--range',
            '-r',
            type=str,
            help='Used to specify an inclusive range of issues to be '
                 'downloaded. ex: -r=3-21'
        )
        download_options.add_argument(
            '--all',
            action='store_true',
            help='Used to specify that all available issues for a comic should'
                 'be downloaded '
        )

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
                self.download_issues(
                    alias,
                    self.args.range,
                    all_=self.args.all
                )

        elif self.args.updates:
            self.get_updates()

        elif self.args.issues:
            alias = self.args.alias
            self.list_available(alias)
