import os
import sys
import tempfile
import appdirs

from comic_dl.utils.helpers import get_chrome_driver


__dbName__ = 'comic.db'
platform = sys.platform


BASE_PATH = os.path.dirname(os.path.dirname(__file__))


ASSETS_PATH = appdirs.user_data_dir(appname='comic-dl')
if not os.path.exists(ASSETS_PATH):
    os.makedirs(ASSETS_PATH)


TEMP_PATH = os.path.join(tempfile.gettempdir(), 'comictemp')
if os.path.exists(TEMP_PATH):
    for f in os.listdir(TEMP_PATH):
        os.remove(os.path.join(TEMP_PATH, f))


if platform in ['linux', 'linux2', 'darwin']:
    ARCHIVE_PATH = os.path.join(os.getenv('HOME'), 'Downloads')
elif platform == 'win32':
    ARCHIVE_PATH = os.path.join(os.getenv('USERPROFILE'), 'Downloads')

ARCHIVE_PATH = os.path.join(ARCHIVE_PATH, 'ComicDL')


if sys.platform == 'win32':
    CHROMEDRIVER = os.path.abspath(
        os.path.join(ASSETS_PATH, 'chromedriver.exe')
    )
else:
    CHROMEDRIVER = os.path.abspath(
        os.path.join(ASSETS_PATH, 'chromedriver')
    )


if not os.path.exists(CHROMEDRIVER):
    prompt = input('Chromedriver is required for this'
                   ' application, download? (y/N): ')
    if prompt.lower() == 'y':
        get_chrome_driver(platform=platform)
    else:
        sys.exit()
