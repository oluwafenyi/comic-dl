import os
import sys

from common.utils import get_chrome_driver


__version__ = '0.0.1'

BASE_PATH = os.path.dirname(os.path.dirname(__file__))

ASSETS_PATH = os.path.join(BASE_PATH, 'assets')

TEMP_PATH = os.path.join(BASE_PATH, 'temp')
if os.path.exists(TEMP_PATH):
    for f in os.listdir(TEMP_PATH):
        os.remove(os.path.join(TEMP_PATH, f))

ARCHIVE_PATH = os.path.join(BASE_PATH, 'archives')

if sys.platform == 'win32':
    CHROMEDRIVER = os.path.abspath(
        os.path.join(ASSETS_PATH, 'chromedriver.exe')
    )
else:
    CHROMEDRIVER = os.path.abspath(
        os.path.join(ASSETS_PATH, 'chromedriver')
    )

if not os.path.exists(CHROMEDRIVER):
    platform = sys.platform

    prompt = input('Chromedriver is required for this'
                   ' application, download? (y/N): ')
    if prompt.lower() == 'y':
        get_chrome_driver(platform=platform)
    else:
        sys.exit()
