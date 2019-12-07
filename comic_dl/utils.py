import os
import re
import zipfile

import requests

from config import TEMP_PATH, ARCHIVE_PATH


def download_page(entry):
    page_number, uri = entry
    res = requests.get(uri)
    cd = res.headers.get('content-disposition')
    extension = re.search(r'filename="(.*)"', cd).group(1).split('.')[-1]
    filename = 'page_{}.{}'.format(page_number + 1, extension)
    path = os.path.join(TEMP_PATH, filename)
    with open(path, 'wb') as img:
        for block in res.iter_content(1024):
            img.write(block)
    return path


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
