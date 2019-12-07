import re
from multiprocessing.pool import ThreadPool
from typing import Union

from tqdm import tqdm

from db import ComicDB
from driver import Driver
from exceptions import ComicDoesNotExist
from utils import download_page, zip_comic


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
        except ComicDoesNotExist():
            return True
        return False

    @classmethod
    def get_by_alias(cls, alias):
        with ComicDB() as db:
            comic = db.get(alias)
        if not comic:
            raise ComicDoesNotExist()
        return Comic(*comic[1:])

    def download_issue(self, issue, driver: Driver) -> Union[str, None]:
        driver.get('{}/Issue-{}/'.format(self.link, issue),
                   params={'quality': 'hq'})
        driver.find_element_by_css_selector('script:nth-child(5)')
        matches = re.findall(r'lstImages.push\("(.*)"\)', driver.page_source)
        if matches is None:
            return None
        entries = list(enumerate(matches))
        img_paths = [path for path in tqdm(
            ThreadPool(8).imap_unordered(download_page, entries),
            desc='{} - #{}'.format(self.title, issue),
            total=len(entries),
        )]
        archive_name = '{} - #{}.cbz'.format(self.title, issue)
        path = zip_comic(self.title, archive_name, img_paths)
        self.last_downloaded = issue if issue > self.last_downloaded\
            else self.last_downloaded
        self.save()
        return path

    def download_issues(self, start, end, driver: Driver) -> list:
        paths = []
        for issue in range(start, end + 1):
            path = self.download_issue(issue, driver)
            paths.append(path)
        return paths

    def download_all_issues(self, driver: Driver) -> list:
        paths = []
        self.get_updates()
        for issue in range(1, self.latest_issue + 1):
            path = self.download_issue(issue, driver)
            paths.append(path)
        return paths

    def get_updates(self, driver: Driver) -> list:
        driver.get(self.link)
        latest_issue = self.driver\
            .find_element_by_css_selector('tr > td > a')\
            .get_attribute('textContent').strip()
        search_obj = re.search(r'#(\d+)', latest_issue)
        latest_issue = int(search_obj.group(1))
        self.latest_issue = latest_issue
        self.save()
        return list(range(self.last_dowloaded + 1, self.latest_issue + 1))

    def list_available(self, driver: Driver) -> list:
        driver.get(self.link)
        available_issues = self.driver\
            .find_elements_by_css_selector('table > tr:nth-child(n+3) > a')
        available = list(map(
            lambda issue: issue.get_attribute('textContent').strip()
        ), available_issues)
        return available
