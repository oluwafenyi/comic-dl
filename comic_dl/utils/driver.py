from urllib.parse import urlencode

import selenium
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from comic_dl.core.config import CHROMEDRIVER
from comic_dl.utils.exceptions import NetworkError


class Driver(selenium.webdriver.Chrome):
    def __init__(self, **kwargs):
        prefs = {"profile.managed_default_content_settings.images": 2}
        options = Options()
        options.add_experimental_option('prefs', prefs)
        options.add_argument("--headless")
        options.add_argument("--window-size=1920x1080")
        super().__init__(
            options=options, executable_path=CHROMEDRIVER, **kwargs
        )
        print('Gathering results...\n')

    def _find_with_wait(self, ec, by, value):
        try:
            return WebDriverWait(self, 10).until(
                ec((by, value))
            )
        except TimeoutException:
            raise NetworkError

    def get(self, url='https://readcomiconline.to/Search/Comic', params={}):
        query_str = urlencode(params)
        super().get('{}?{}'.format(url, query_str))

    def find_element_by_css_selector(self, css_selector):
        return self._find_with_wait(
            EC.presence_of_element_located, By.CSS_SELECTOR, css_selector
        )

    def find_elements_by_css_selector(self, css_selector):
        return self._find_with_wait(
            EC.presence_of_all_elements_located, By.CSS_SELECTOR, css_selector
        )
