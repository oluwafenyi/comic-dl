import os
import re
import zipfile
from multiprocessing.pool import ThreadPool
from typing import Union

import requests
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm

from db import ComicDB
from driver import Driver
from exceptions import AliasDoesNotExist


BASE_PATH = os.path.dirname(os.path.dirname(__file__))
TEMP_PATH = os.path.join(BASE_PATH, 'temp')
ARCHIVE_PATH = os.path.join(BASE_PATH, 'archives')


def download_pages(entry):
    page_number, uri = entry
    res = requests.get(uri)
    cd = res.headers.get('content-disposition')
    extension = extension_from_cd(cd)
    filename = 'page_{}.{}'.format(page_number + 1, extension)
    path = os.path.join(TEMP_PATH, filename)
    with open(path, 'wb') as img:
        for block in res.iter_content(1024):
            img.write(block)
    return path


def extension_from_cd(cd):
    result = re.search(r'filename="(.*)"', cd)
    return result.group(1).split('.')[-1]


def zip_comic(comic_title, archive_name, images):
    print('Zipping comic...')
    path = os.path.join(ARCHIVE_PATH, comic_title)
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, archive_name)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as zf:
        for img in images:
            zf.write(img, compress_type=zipfile.ZIP_STORED)
            os.remove(img)
    return path


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
    def list_watched(cls):
        with ComicDB() as db:
            watched = db.get_all()
        return list(map(lambda comic: comic[1:], watched))

    @classmethod
    def is_alias_unique(cls, alias):
        try:
            cls.get_by_alias(alias)
        except AliasDoesNotExist():
            return True
        return False

    @classmethod
    def get_by_alias(cls, alias):
        with ComicDB() as db:
            comic = db.get(alias)
        if not comic:
            raise AliasDoesNotExist()
        return Comic(*comic[1:])

    def download_issue(self, issue, driver: Driver) -> Union[str, None]:
        try:
            img_404 = driver.find_element_by_css_selector(
                '#divMsg > div:nth-child(2) > img'
            )
            if 'error' in img_404.get_attribute('src'):
                return None
        except NoSuchElementException:
            ...

        driver.get('{}/Issue-{}/'.format(self.link, issue),
                   params={'quality': 'hq'})
        driver.find_element_by_css_selector('script:nth-child(5)')
        matches = re.findall(r'lstImages.push\("(.*)"\)', driver.page_source)
        entries = list(enumerate(matches))
        img_paths = [path for path in tqdm(
            ThreadPool(8).imap_unordered(download_pages, entries),
            desc='{} - #{}'.format(self.title, issue),
            total=len(entries),
        )]
        archive_name = '{} - #{}.cbz'.format(self.title, issue)
        path = zip_comic(self.title, archive_name, img_paths)
        self.last_downloaded = issue if issue > self.last_downloaded\
            else self.last_downloaded
        self.save()
        return path

    def download_issues(self, start, end, driver: Driver):
        paths = []
        for issue in range(start, end + 1):
            path = self.download_issue(issue, driver)
            paths.append(path)
        return paths
