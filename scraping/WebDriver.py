from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class WebDriverSingleton:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            options = Options()
            options.add_argument('--headless')
            cls._instance = webdriver.Chrome(options=options)

        return cls._instance

    def quit(self):
        if self._instance:
            self._instance.quit()
            self._instance = None
