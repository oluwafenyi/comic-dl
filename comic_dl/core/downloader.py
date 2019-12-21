from multiprocessing.pool import ThreadPool
import re
import time

from tqdm import tqdm

from comic_dl.core.comic import Comic
from comic_dl.utils.driver import Driver
from comic_dl.utils.exceptions import NetworkError, CAPTCHAError
from comic_dl.utils.helpers import (
    download_page,
    zip_comic,
    get_size,
    download_prompt,
    get_issue_num,
    normalize as _,
)


class ComicDownloader:
    def __init__(self, comic: Comic = None):
        self.comic = comic

    def _image_links(self, driver: Driver):
        driver.find_element_by_css_selector('script:nth-child(5)')
        matches = re.findall(r'lstImages.push\("(.*)"\)', driver.page_source)
        return matches

    def get_image_links(self, driver: Driver, comic_link=None):
        driver.get(comic_link, params={'quality': 'hq'})
        title = driver.find_element_by_css_selector('title')\
            .get_attribute('textContent').strip()
        title = _(title.split('-')[0].strip())

        try:
            comic_series = driver\
                .find_element_by_css_selector('div#navsubbar a')\
                .get_attribute('textContent').strip()
        except NetworkError:
            title = driver.find_element_by_css_selector('title')\
                .get_attribute('textContent').strip()
            if _(title).strip().lower() == 'are you human':
                raise CAPTCHAError
            raise

        comic_series = _(comic_series).replace('Comic', '')\
            .replace('information', '').strip()
        img_links = self._image_links(driver)
        if img_links:
            return {
                'series': comic_series,
                'title': title,
                'img_links': img_links
            }
        raise NetworkError

    def _download_pages(self, desc, links):
        img_paths = [path for path in tqdm(
            ThreadPool(8)
            .imap_unordered(download_page, list(enumerate(links))),
            desc=desc,
            total=len(links),
        )]
        return img_paths

    def download_issue(self, driver: Driver, link, many=False) -> str:
        dict_data = self.get_image_links(driver, comic_link=link)
        title = dict_data['title']
        links = dict_data['img_links']
        series = dict_data['series']

        if not many:
            size = sum(size for size in
                       ThreadPool(8).imap_unordered(get_size, links))
            prompt = download_prompt(size)
            if prompt.lower() != 'y':
                return

        img_paths = self._download_pages(title, links)

        if self.comic:
            series = _(self.comic.title)

        path = zip_comic(series, title, img_paths)
        issue = get_issue_num(title)

        if issue is not None and self.comic is not None:
            self.comic.last_downloaded = issue if issue >\
                self.comic.last_downloaded else self.comic.last_downloaded
            self.comic.save()
        return path

    def download_issues(self, driver: Driver, links) -> list:
        prompt = input('Can\'t precalculate the size of your download, '
                       'are you sure you want to do this? [y/N]: ')
        if prompt.lower() != 'y':
            return

        paths = []
        for i, link in enumerate(links):
            if i % 30 == 0 and i != 0:
                print('Taking a break to bypass rate limiting, will resume...')
                time.sleep(20)
                print('Resumed')
            path = self.download_issue(driver, link=link, many=True)
            paths.append(path)
        return paths
