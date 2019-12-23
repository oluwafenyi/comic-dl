
from comic_dl.utils.db import ComicDB
from comic_dl.utils.driver import Driver
from comic_dl.utils.exceptions import ComicDoesNotExist, IssueNotAvailable
from comic_dl.utils.helpers import get_issue_num, get_annual_num


class Comic:
    def __init__(self, title: str, link: str, alias: str,
                 latest_issue: int = 0,
                 last_downloaded: int = 0):
        self.title = title
        self.alias = alias
        self.latest_issue = latest_issue
        self.last_downloaded = last_downloaded
        self.link = link

    def __str__(self):
        return self.title

    def save(self):
        with ComicDB() as db:
            db.save(**vars(self))

    def delete(self):
        with ComicDB() as db:
            db.delete(self.alias)

    @classmethod
    def list_watched(cls) -> list:
        """
        Comic Class Method
        -----------------------------------------------------------------------
        :returns: list of watched Comic objects
        """
        with ComicDB() as db:
            watched = db.get_all()
        return list(map(lambda comic: Comic(*comic[1:]), watched))

    @classmethod
    def is_alias_unique(cls, alias) -> bool:
        try:
            cls.get_by_alias(alias)
        except ComicDoesNotExist:
            return True
        return False

    @classmethod
    def get_by_alias(cls, alias):
        with ComicDB() as db:
            comic = db.get(alias)
        if not comic:
            raise ComicDoesNotExist()
        return Comic(*comic[1:])

    def get_listing(self, driver: Driver):
        driver.get(self.link)
        return driver.find_elements_by_css_selector('table.listing td a')

    def get_issues(self, driver: Driver):
        listing = self.get_listing(driver)
        issues = list(filter(
            lambda e:
                get_issue_num(e.get_attribute('textContent')) is not None,
            listing
        ))
        return issues

    def get_issue_link(self, driver: Driver, issue):
        issues = self.get_issues(driver)
        try:
            return list(filter(
                lambda e:
                    get_issue_num(e.get_attribute('textContent')) == issue,
                issues
            ))[0].get_attribute('href')
        except IndexError:
            raise IssueNotAvailable

    def get_annuals(self, driver: Driver):
        listing = self.get_listing(driver)
        annuals = list(filter(
            lambda e: get_annual_num(e.get_attribute('textContent')),
            listing
        ))
        return annuals

    def get_annual_link(self, driver: Driver, annual):
        issues = self.get_annuals(driver)
        try:
            return list(filter(
                lambda e:
                    get_annual_num(e.get_attribute('textContent')) == annual,
                issues
            ))[0].get_attribute('href')
        except IndexError:
            raise IssueNotAvailable

    def get_updates(self, driver: Driver) -> list:
        available = self.list_available(driver)

        try:
            last_read = list(filter(
                lambda i: get_issue_num(i[0]) == self.last_downloaded,
                available
            ))[0]
        except IndexError:
            idx = None
        else:
            idx = available.index(last_read)

        updates = available[:idx]
        return updates

    def list_available(self, driver: Driver) -> list:
        available_issues = self.get_listing(driver)
        available =\
            [issue.get_attribute('textContent').strip()
                for issue in available_issues]

        latest_issue = get_issue_num(available[0])
        self.latest_issue = latest_issue or 0
        self.save()

        dates = driver.\
            find_elements_by_css_selector('table.listing tr td:nth-child(2)')
        dates = [date.get_attribute('textContent').strip() for date in dates]

        available = list(zip(available, dates))
        return available
