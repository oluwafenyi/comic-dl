import os
import re
import stat
import zipfile

import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from comic_dl.core import config
from comic_dl.utils.exceptions import PlatformNotSupported


def normalize(text):
    return re.sub(r'\s+', ' ', text).replace(':', ' -')


def get_issue_num(text):
    match = re.search(r'#(\d+)', text)
    if match:
        return int(match.group(1))
    return None


def get_annual_num(text):
    match = re.search(r'Annual (\d+)', text)
    if match:
        return int(match.group(1))
    return None


def format_size(size):
    power = 2**10
    n = 0
    power_labels = {0: '', 1: 'k', 2: 'm', 3: 'g', 4: 't'}
    while size > power:
        size /= power
        n += 1
    return ''.join([str(round(size, 2)), power_labels[n] + 'b'])


def get_size(url):
    size = requests.head(url).headers['Content-Length']
    return int(size)


def download_prompt(size):
    prompt = input('Total size is {}, Download? [y/N]: '
                   .format(format_size(size)))
    return prompt


def download_page(entry):
    page_number, uri = entry

    res = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504],
    )
    res.mount('https://', HTTPAdapter(max_retries=retries))

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
    res.close()
    return path


def zip_comic(comic_title, archive_name, images):
    print('Zipping comic...')
    path = os.path.join(config.ARCHIVE_PATH, comic_title)
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, '{}.cbz'.format(archive_name))
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as zf:
        for img in images:
            zf.write(img, compress_type=zipfile.ZIP_STORED)
            os.remove(img)
    print('Done')
    return path


def get_chrome_driver(platform):
    print('Downloading chromedriver, please wait...')
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

    try:
        with open(path, 'wb') as f:
            for block in res.iter_content(1024):
                f.write(block)

        with zipfile.ZipFile(path, 'r') as zf:
            zf.extractall(config.ASSETS_PATH)

        os.remove(path)

        if platform in ['linux', 'linux2', 'darwin']:
            st = os.stat(config.CHROMEDRIVER)
            os.chmod(config.CHROMEDRIVER, st.st_mode | stat.S_IEXEC)
    except:
        if os.path.exists(path):
            os.remove(path)
