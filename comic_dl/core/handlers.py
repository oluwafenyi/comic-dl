
from core.comic import Comic
from core.downloader import ComicDownloader
from utils.exceptions import InvalidRangeException
from utils.helpers import get_issue_num


def set_alias(title):
    alias = input('Set an alias for "{}"\n>>> '.format(title))
    if alias.isnumeric() or alias.isspace() or ' ' in alias:
        print('not a valid alias, alias should be alphanumeric, no spaces')
        alias = ''
    if not Comic.is_alias_unique(alias):
        print('alias already used')
    return alias


def get_choice(options):
    print('Pick comic to add or enter q at any time to exit: \n\n')
    for idx, option in options.items():
        print('{}. {}'.format(idx + 1, option[0]))

    n = input('\n>>> ')
    if n == 'q':
        return 'q'
    try:
        return options.get(int(n) - 1, None)
    except ValueError:
        return None


class HandlerMixin:
    def display_watched(self):
        watched = Comic.list_watched()
        print('|{:20}      {:<20}      {:<20}|'
              .format('Comic', 'Alias', 'Last Downloaded'))
        for comic in watched:
            print('|{:20}      {:<20}      {:<20}|'
                  .format(comic.title, comic.alias, comic.last_downloaded))

    def add_comic_to_watched(self, query):
        self.driver.get(params={'keyword': query})
        table = self.driver.find_element_by_css_selector('table.listing')
        rows = table.find_elements_by_css_selector('tr > td:nth-child(1) > a')
        rows = list(map(
            lambda row: (
                row.get_attribute('textContent').strip(),
                row.get_attribute('href'),
            ),
            rows
        ))
        results = dict(enumerate(rows))

        choice = None
        while choice is None:
            choice = get_choice(results)

            if choice == 'q':
                break

            if choice:
                alias = ''
                while not alias:
                    alias = set_alias(choice[0])

                comic = Comic(*choice, alias=alias)
                comic.save()
                print('Added "{}" to list of watched comics...'
                      .format(choice[0]))
            else:
                print('That is not a valid option. Try again.')

    def watch_link(self, link):
        self.driver.get(link)
        title = self.driver.find_element_by_css_selector('.bigChar')\
            .get_attribute('textContent').strip()
        latest_issue = self.driver.find_element_by_css_selector('tr > td > a')\
            .get_attribute('textContent').strip()
        latest_issue = get_issue_num(latest_issue)
        alias = ''
        while not alias:
            alias = set_alias(title)
        comic = Comic(title, link, alias, latest_issue=latest_issue)
        comic.save()
        print('Added "{}" to list of watched comics under...'.format(title))

    def download_issue(self, alias, issue):
        comic = Comic.get_by_alias(alias)
        cd = ComicDownloader(comic)
        path = cd.download_issue(self.driver, issue=issue)
        if path:
            print('Comic downloaded to {}'.format(path))

    def download_annual(self, alias, annual):
        comic = Comic.get_by_alias(alias)
        cd = ComicDownloader(comic)
        path = cd.download_issue(self.driver, annual=annual)
        if path:
            print('Comic downloaded to {}'.format(path))

    def download_issues(self, alias, range_, all_):
        comic = Comic.get_by_alias(alias)
        cd = ComicDownloader(comic)
        if not all_:

            try:
                start, end = map(lambda arg: int(arg), range_.split('-'))
            except ValueError:
                raise InvalidRangeException(
                    'Range should be of form: "a-b", where a and b are '
                    'integers'
                )

            start, end = sorted([start, end])
            paths = cd.download_issues(self.driver, start, end)
        else:
            comic.get_updates(self.driver)
            paths = cd.download_issues(self.driver)

        if paths:
            print('Comics downloaded to: ')
            for path in paths:
                print(path)

    def get_updates(self):
        updates = {}
        for comic in Comic.list_watched():
            unread = comic.get_updates(self.driver)
            if not unread:
                continue
            title = 'Unread Comics for {} -- alias: "{}"'\
                .format(comic.title, comic.alias)
            updates[title] = unread

        for title, issues in updates.items():
            if not issues:
                continue
            print('{:20}      {:<20}'
                  .format(title, 'Date Uploaded'))
            for issue in issues:
                print('{:20}      {:<20}'.format(issue[0], issue[1]))

    def list_available(self, alias):
        comic = Comic.get_by_alias(alias)
        available = comic.list_available(self.driver)
        print('Available comics for {}:'.format(comic.title))
        for issue, date in available:
            print('{:20}      {:<20}'.format(issue, date))
