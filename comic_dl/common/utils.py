import os
import re
import stat
import zipfile

import requests

import config
from common.exceptions import PlatformNotSupported


def download_page(entry):
    page_number, uri = entry
    res = requests.get(uri)
    cd = res.headers.get('content-disposition')
    extension = re.search(r'filename="(.*)"', cd).group(1).split('.')[-1]
    filename = 'page_{}.{}'.format(page_number + 1, extension)
    if not os.path.exists(config.TEMP_PATH):
        os.makedirs(config.TEMP_PATH)
    path = os.path.join(config.TEMP_PATH, filename)
    with open(path, 'wb') as img:
        for block in res.iter_content(1024):
            img.write(block)
    return path


def zip_comic(comic_title, archive_name, images):
    print('Zipping comic...')
    path = os.path.join(config.ARCHIVE_PATH, comic_title)
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, archive_name)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as zf:
        for img in images:
            zf.write(img, compress_type=zipfile.ZIP_STORED)
            os.remove(img)
    return path


def get_chrome_driver(platform):
    latest_version = requests\
        .get('https://chromedriver.storage.googleapis.com/LATEST_RELEASE').text

    chromedriver = 'chromedriver'
    if platform == 'linux' or platform == 'linux2':
        chromedriver += '_linux64.zip'

    elif platform == 'darwin':
        chromedriver += '_mac64.zip'

    elif platform == 'win32':
        chromedriver += '_win32.zip'

    else:
        raise PlatformNotSupported('{platform} is currently not supported'
                                   ' for chromedriver')

    url = 'https://chromedriver.storage.googleapis.com/{}/{}'\
        .format(latest_version, chromedriver)

    res = requests.get(url)
    path = os.path.join(config.ASSETS_PATH, chromedriver)

    with open(path, 'wb') as f:
        for block in res.iter_content(1024):
            f.write(block)

    with zipfile.ZipFile(path, 'r') as zf:
        zf.extractall(config.ASSETS_PATH)

    os.remove(path)

    if platform in ['linux', 'linux2', 'darwin']:
        st = os.stat(config.CHROMEDRIVER)
        os.chmod(config.CHROMEDRIVER, st.st_mode | stat.S_IEXEC)
