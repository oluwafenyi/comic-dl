from multiprocessing.pool import ThreadPool
import re
import time

from tqdm import tqdm

from comic_dl.core.comic import Comic
from comic_dl.utils.driver import Driver
from comic_dl.utils.exceptions import NetworkError
from comic_dl.utils.helpers import (
    download_page,
    zip_comic,
    get_size,
    download_prompt,
    get_issue_num,
    get_annual_num
)


class ComicDownloader:
    def __init__(self, comic: Comic):
        self.comic = comic

    def get_image_links(self, driver: Driver, issue=None, annual=None):
        if issue is not None:
            link = '{}/Issue-{}/'.format(self.comic.link, issue)
        elif annual is not None:
            link = '{}/Annual-{}/'.format(self.comic.link, annual)
        driver.get(link, params={'quality': 'hq'})
        matches = self._image_links(driver)
        if matches:
            for match in matches:
                yield match
        else:
            # Failsafe in case the issue path is not the expected path
            # Came across an issue with path /Issue-32-2/ instead of /Issue-32/
            if issue is not None:
                issues = self.comic.get_issues(driver)
                titles =\
                    [get_issue_num(issue.get_attribute('textContent'))
                        for issue in issues]
                try:
                    index = titles.index(int(issue))
                except ValueError:
                    raise NetworkError
                link = issues[index].get_attribute('href')
            elif annual is not None:
                annuals = self.comic.get_annuals(driver)
                titles =\
                    [get_annual_num(annual.get_attribute('textContent'))
                        for annual in annuals]
                try:
                    index = titles.index(int(annual))
                except ValueError:
                    raise NetworkError
                link = annuals[index].get_attribute('href')

            driver.get(link, params={'quality': 'hq'})
            matches = self._image_links(driver)
            for match in matches:
                yield match

    def _image_links(self, driver: Driver):
        driver.find_element_by_css_selector('script:nth-child(5)')
        matches = re.findall(r'lstImages.push\("(.*)"\)', driver.page_source)
        return matches

    def download_issue(self, driver: Driver, issue=None, annual=None,
                       many=False) -> str:
        links = [link for link in
                 self.get_image_links(driver, issue=issue, annual=annual)]

        if not many:
            size = sum(size for size in
                       ThreadPool(8).imap_unordered(get_size, links))
            prompt = download_prompt(size)
            if prompt.lower() != 'y':
                return

        desc = '{} - #{}'.format(self.comic.title, issue) if issue is not None\
            else '{} - Annual {}'.format(self.comic.title, annual)

        entries = list(enumerate(links))
        img_paths = [path for path in tqdm(
            ThreadPool(8).imap_unordered(download_page, entries),
            desc=desc,
            total=len(entries),
        )]
        archive_name = '{}.cbz'.format(desc)
        path = zip_comic(self.comic.title, archive_name, img_paths)
        if issue is not None:
            self.comic.last_downloaded = issue if issue >\
                self.comic.last_downloaded else self.comic.last_downloaded
        self.comic.save()
        return path

    def download_issues(self, driver: Driver, start=1, end='last') -> list:
        annuals = False
        if end == 'last':
            end = self.comic.latest_issue
            annuals = True

        prompt = input('Can\'t precalculate the size of your download, '
                       'are you sure you want to do this? [y/N]: ')
        if prompt.lower() != 'y':
            return

        paths = []
        for i, issue in enumerate(range(start, end + 1)):
            if i % 30 == 0 and i != 0:
                print('Pausing for a bit to bypass rate limiting.')
                time.sleep(20)
                print('Resumed')
            path = self.download_issue(driver, issue, many=True)
            paths.append(path)

        if annuals:
            annuals = self.comic.get_annuals(driver)
            annuals = [get_annual_num(i) for i in annuals]
            for annual in annuals:
                path = self.download_issue(driver, annual=annual)
                paths.append(path)
        return paths
