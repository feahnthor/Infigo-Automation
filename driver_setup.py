from selenium.webdriver import FirefoxOptions
from selenium import webdriver
from helium import * # Helium is a higher level webdriver that still allows for use of selenium webdriver
import logging

from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)

class DriverSetup:
  """
  Helium: https://selenium-python-helium.readthedocs.io/en/latest/api.html
  """
  def __init__(self, url, headless=False) -> WebDriver:
    super().__init__()
    self.url = url
    self.headless = headless
    # self.options = FirefoxOptions()
    # self.options.add_argument('--width=1920')
    # self.options.add_argument('--height=1020')
    # self.driver = start_firefox(self.url, options=self.options)

    # start_firefox() accpets a url and launches a instance of a firefox browser, *method from Helium*
    
    logger.info('Starting Firefox driver')
    try:
      start_firefox(self.url, headless=self.headless).maximize_window()
      self.driver = get_driver()
    except Exception as e:
      logger.critical('Firefox driver Failed to start')
      DriverSetup.done(self)
  def _get_driver(self): # get_driver is already a helium function
    """
    This method is specifically used for Multithreading as it returns an instance of a browser. Just calling saving
    `driver` as a variable instead of using `self.driver` will have a return of None
    """
    return self.driver
  def done(self) -> None:
    if self.driver != None:
      kill_browser()