import argparse
import logging
import sys

from selenium.webdriver.remote.remote_connection import LOGGER

from . import __version__
from comic_dl.core.handlers import HandlerMixin
from comic_dl.utils.driver import Driver
from comic_dl.utils.exceptions import ArgumentNotSpecified, AliasNotSpecified


LOGGER.setLevel(logging.WARNING)


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
            '-v',
            '--version',
            action='version',
            version='comicdl - {version}'.format(version=__version__)
        )

        parser.add_argument(
            'command',
            type=str,
            help="""
            Command Options:
            * watch: Finds comics based on query and adds your choice to the
                     database under specified alias.

            * stopwatch: Deletes aliased comic from watchlist.

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

        add_options = parser.add_mutually_exclusive_group()

        add_options.add_argument(
            '--query',
            '-q',
            action='store',
            type=str,
            help='-Finds comics based on query and adds your choice to'
                 ' database identified by specified alias',
        )

        add_options.add_argument(
            '--link',
            '-l',
            action='store',
            type=str,
            help='-Adds valid links for comic series from readcomiconline.to '
                 'to watch list'
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
            '--annual',
            '-a',
            type=int,
            help='Used with the download flag to specify annual to be '
                 'downloaded'
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

        elif self.args.command == 'watch':
            query = self.args.query
            link = self.args.link
            self.driver = Driver()
            if query:
                self.add_comic_to_watched(query)

            elif link:
                self.watch_link(link)

            else:
                raise ArgumentNotSpecified('-q or -l argument expected')

        elif self.args.command == 'download':

            if self.args.link:
                self.driver = Driver()
                self.download_series(self.args.link)
                return

            alias = self.args.alias
            if not alias:
                raise AliasNotSpecified

            self.driver = Driver()

            if self.args.issue:
                self.download_issue(alias, self.args.issue)

            elif self.args.annual:
                self.download_annual(alias, self.args.annual)

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

        elif self.args.command == 'stopwatch':
            alias = self.args.alias
            if not alias:
                raise AliasNotSpecified
            self.stop_watching(alias)

        else:
            parser.print_help()


def execute_from_command_line():
    with CommandUtility(sys.argv) as c:
        c.execute()
