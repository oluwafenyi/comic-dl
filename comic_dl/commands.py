import argparse

from common.driver import Driver
from common.exceptions import ArgumentNotSpecified, AliasNotSpecified
from handlers import HandlerMixin


class CommandUtility(HandlerMixin):
    def __init__(self, argv, args=None):
        self.argv = argv
        self.args = args

    def __enter__(self):
        return self

    def __exit__(self, ext_type, exc_value, traceback):
        try:
            self.driver.quit()
        except AttributeError:
            pass

    def execute(self):
        parser = argparse.ArgumentParser()

        parser.add_argument(
            'command',
            type=str,
            help="""
            Command Options:
                * add: Finds comics based on query and adds your choice to the
                      database under specified alias.

                * watched: Lists all comics in database along with aliases.

                * download: Downloads comic issues for comic specified by alias
                      one of -i, -r or --all flags should be specified.

                * issues: Lists available issues for comic specified by alias.

                * updates: lists issues for watched comics that have not been
                      downloaded.
                 """,
        )

        parser.add_argument(
            'alias',
            type=str,
            help='-Unique identifier for comics',
            nargs='?'
        )

        parser.add_argument(
            '--query',
            '-q',
            action='store',
            type=str,
            help='-Finds comics based on query and adds your choice to'
                 ' database identified by specified alias',
        )

        download_options = parser.add_mutually_exclusive_group()
        download_options.add_argument(
            '--issue',
            '-i',
            type=int,
            help='-Used with the download flag to specify issue to be '
                 'downloaded',
        )
        download_options.add_argument(
            '--range',
            '-r',
            type=str,
            help='-Used to specify an inclusive range of issues to be '
                 'downloaded. ex: -r=3-21'
        )
        download_options.add_argument(
            '--all',
            action='store_true',
            help='-Used to specify that all available issues for a comic '
                 'should be downloaded '
        )

        self.args = parser.parse_args(self.argv[1:]) \
            if not self.args else self.args

        if self.args.command == 'watched':
            self.display_watched()

        elif self.args.command == 'add':
            query = self.args.query
            if not query:
                raise ArgumentNotSpecified('-q="<query>" flag is compulsory'
                                           ' for this command')
            self.driver = Driver()
            self.add_comic_to_watched(query)

        elif self.args.command == 'download':
            alias = self.args.alias
            if not alias:
                raise AliasNotSpecified
            self.driver = Driver()

            if self.args.issue:
                self.download(alias, self.args.issue)

            elif self.args.range or self.args.all:
                self.download_issues(
                    alias,
                    self.args.range,
                    all_=self.args.all
                )

        elif self.args.command == 'updates':
            self.driver = Driver()
            self.get_updates()

        elif self.args.command == 'issues':
            alias = self.args.alias
            if not alias:
                raise AliasNotSpecified
            self.driver = Driver()
            self.list_available(alias)
