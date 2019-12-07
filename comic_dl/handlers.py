
from comic import Comic
from exceptions import InvalidRangeException


class HandlerMixin:
    def display_watched(self):
        print('|{:20}      {:<20}|'.format('Comic', 'Alias'))
        for comic in Comic.list_watched():
            print('|{:20}      {:<20}|'.format(comic[0], comic[2]))

    def add_comic_to_watched(self):
        self.driver.get(params={'keyword': self.args.add})
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
            print('Pick comic to add or enter q at any time to exit: \n\n')
            for idx, result in results.items():
                print('{}. {}'.format(idx + 1, result[0]))
            n = int(input('\n>>> ')) - 1

            if n == 'q':
                break

            choice = results.get(n, None)
            if choice:
                alias = ''
                while not alias:
                    alias = input('Set an alias for "{}"\n>>> '
                                  .format(choice[0]))
                    if alias.isnumeric() or alias.isspace() or ' ' in alias:
                        print('not a valid alias, alphanumeric, no spaces')
                        alias = ''
                    if not Comic.is_alias_unique(alias):
                        print('alias already used')
                        alias = ''

                comic = Comic(*choice, alias=alias)
                comic.save()
                print('Added "{}" to list of watched comics...'
                      .format(choice[0]))
            else:
                print('That is not a valid option. Try again.')

    def download(self):
        alias = self.args.alias

        if not alias:
            raise ValueError

        comic = Comic.get_by_alias(alias)

        if self.args.issue:
            path = comic.download_issue(self.args.issue, self.driver)
            print('Comic downloaded to {}'.format(path))

        elif self.args.range:
            try:
                start, end = map(
                    lambda arg: int(arg), self.args.range.split('-')
                )
            except ValueError:
                raise InvalidRangeException(
                    'Range should be of form: "a-b", where a and b are '
                    'integers'
                )
            start, end = sorted([start, end])
            paths = comic.download_issues(start, end, self.driver)
            print('Comics downloaded to: ')
            for path in paths:
                print(path)

    def get_updates(self):
        for comic in Comic.list_watched():
            unread = comic.get_updates(self.driver)
            if not unread:
                continue
            print('Unread Comics for {} -- alias: "{}"'
                  .format(comic.title, comic.alias))
            for issue in unread:
                print('  {} - #{}'.format(comic.title, issue))

    def list_available(self):
        comic = Comic.get_by_alias(self.args.alias)
        available = comic.list_available(self.driver)
        print('Available comics for {}:'.format(comic.title))
        for issue in available:
            print(issue)
