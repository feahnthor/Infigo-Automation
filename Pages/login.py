from helium import *
#import toml   look up toml for more human readable configs
from credentials import Credentials
from locators import Locators
from driver_setup import DriverSetup
import logging

logger = logging.getLogger(__name__)

class Login(DriverSetup):
  def __init__(self, url, headless=False) -> None:
    super().__init__(url=url, headless=headless)
    """
    This class is resusable as it only accepts an url to login and send it to DriverSetup class. Should only really
      be called once, as once logged in sessions can continue without the prompt during redirects
    """
    # set variables for input into login page
    self.url = url
    self.email = Credentials.email
    self.password = Credentials.password
    self.email_loc = Locators.email 
    self.password_loc = Locators.password
    self.login = Locators.login_button
    

    # Both write() and click() functions are from Helium, which sends data to the browser, in this case the login info then clicks the login button
    # Great demonstration of this can be found on the github page under their README.md https://github.com/mherrmann/selenium-python-helium
    write(self.email, into=self.email_loc)
    write(self.password, into=self.password_loc)
    click(self.login)
    logger.info('Logging in')