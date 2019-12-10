import re
from multiprocessing.pool import ThreadPool

from tqdm import tqdm

from common.db import ComicDB
from common.driver import Driver
from common.exceptions import ComicDoesNotExist, NetworkError
from common.utils import download_page, zip_comic, get_size, download_prompt


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

    def get_image_links(self, driver: Driver, issue):
        driver.get('{}/Issue-{}/'.format(self.link, issue),
                   params={'quality': 'hq'})
        driver.find_element_by_css_selector('script:nth-child(5)')
        matches = re.findall(r'lstImages.push\("(.*)"\)', driver.page_source)
        if matches:
            for match in matches:
                yield match
        else:
            raise NetworkError

    def download_issue(self, driver: Driver, issue, many=False) -> str:
        links = [link for link in self.get_image_links(driver, issue)]

        if not many:
            size = sum(size for size in
                       ThreadPool(8).imap_unordered(get_size, links))
            prompt = download_prompt(size)
            if prompt.lower() != 'y':
                return

        entries = list(enumerate(links))
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

    def download_issues(self, driver: Driver, start=1, end='last') -> list:
        if end == 'last':
            end = self.latest_issue

        prompt = input('Can\'t precalculate the size of your download, '
                       'are you sure you want to do this? [y/N]: ')
        if prompt.lower() != 'y':
            return

        paths = []
        for issue in range(start, end + 1):
            path = self.download_issue(driver, issue, many=True)
            paths.append(path)
        return paths

    def get_updates(self, driver: Driver) -> list:
        available = self.list_available(driver)

        def issue_num(title):
            match = re.search(r'#(\d+)', title)
            if match:
                return int(match.group(1))
            return False

        last_read = list(filter(
            lambda i: issue_num(i[0]) == self.last_downloaded,
            available
        ))[0]

        idx = available.index(last_read)
        updates = available[:idx]

        latest_issue = issue_num(available[0][0])
        self.latest_issue = latest_issue
        self.save()

        return updates

    def list_available(self, driver: Driver) -> list:
        driver.get(self.link)
        available_issues = driver\
            .find_elements_by_css_selector('table.listing td a')
        available =\
            [issue.get_attribute('textContent').strip()
                for issue in available_issues]
        dates = driver.\
            find_elements_by_css_selector('table.listing tr td:nth-child(2)')
        dates = [date.get_attribute('textContent').strip() for date in dates]

        available = list(zip(available, dates))
        return available
