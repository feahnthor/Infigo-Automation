# Import other python files from folders in this directory to use
from selenium.common.exceptions import TimeoutException
from Pages.login import Login # In the ./pages/ folder use login.py and use Login() class. Only used to start the program
from Pages.variants import Variants # function that will be used on the Variants page; such as editing sizes
from Pages.baseproduct import BaseProduct # functions that will be used on the product home page that contains Categories
from locators import Locators # In this current directory use locators.py and use Locators class. Only has variables no functions
from dir_location import DirLocation
from file_handler import FileHandler
from driver_setup import DriverSetup

from helium import *
import logging
import logging.config
from pythonjsonlogger import jsonlogger #https://github.com/madzak/python-json-logger
## loggin with python https://blog.guilatrova.dev/how-to-log-in-python-like-a-pro/
import os
import shutil
import PySimpleGUI as sgs
from pathlib import Path
import time
import watchdog
from glob import glob
import multiprocessing as mp
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
"""
https://stackoverflow.com/questions/35950740/virtualenv-is-not-recognized-as-an-internal-or-external-command-operable-prog
To Do for attribute sort: 
1. Fix program to accep\\work\production\backgroundtown images\Serendipity\web\Springfield_8x10.jpgt url or product to edit without a json
2. Allow user to enter sizes to be added

https://selenium-python.readthedocs.io/api.html
"""

logging.config.dictConfig(FileHandler('\\\\work\\tech\\Henry\\Programs\\Python\\bgt-automate\\create_product\\loggin_config.json').open_json())
# Create logger
logger = logging.getLogger(__name__)

def main():
  begin_time = time.perf_counter()
  os.chdir(DirLocation.add_to_bgtown)
  try:
    first_json_object = FileHandler(os.listdir()[0]).open_json()
  except IndexError as e:
    logger.info(f'No files found yet, waiting again')
    exit()
  url, is_floor = get_base_url(first_json_object) #determines which template url to use
  finished_url_array = []

  ############ Start Web Driver then loging ###########
  Login(url, headless=True) # param: headless=False is false be default, change it to run in headless mode
  

  logger.info(f'Retrieving json from {DirLocation.add_to_bgtown}')
  count = 0
  try:
    wait_until(Text(Locators.save_and_continue).exists, timeout_secs=20) # If login time takes longer than normal, update this timeout accordingly
  except TimeoutException as e:
    logger.info(f'Timeout error on first load of the page. Reloading...\nIf this fails again, consider checking if there is congestion in our network before sending an email to Infigo\n')
    refresh()
    wait_until(Text(Locators.save_and_continue).exists, timeout_secs=30) # If the load time to login 
    
  driver = get_driver()
  WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, 'side-bar__burger')))
  driver.find_element_by_id('side-bar__burger').click() # closes sidebar
  
  
  files = os.listdir()
  for file in files:
    # file = os.listdir
    # time.sleep(3)
    try:
      if not Path(f'{DirLocation.bgt_processing}\\{file}').exists():
        processing_file = shutil.move(file, DirLocation.bgt_processing)
      else:
          continue # this file is already being used, go to the next
    except Exception as e:
      logger.info(f'File not found to move it\nFile: {file}')
      continue # go to next iteration, assumption is it has been picked up by another instance
    try:
      json_object = FileHandler(processing_file).open_json()
      logger.info(f'Retrieved data from {json_object}.\n {count}/{len(os.listdir())}')
      count+=1
      url, is_floor = get_base_url(json_object)

      wait_until(Text(Locators.save_and_continue).exists) # important to avoid reloading the page
      go_to(url)
      
      prod_home = BaseProduct(**json_object)
      variants_page = Variants(**json_object)
      logger.info(f'Available sizes {len(json_object["sizes"])}: {json_object["sizes"]}')
      prod_home.copy_product()
      prod_home.add_tags()
      prod_home.prod_img()
      prod_home.add_category()
      finished_url_array.append(get_driver().current_url)
      prod_home.save_and_edit()
      
      wait_until(Text(Locators.published).exists)
      prod_home.go_to_variants()
      # if is_floor != True: # floors do not have attribute logic to delete\\
        # variants_page.delete_logic()  # delete_logic may be deprecated as delete_size() does the same
      start_time = time.perf_counter()
      variants_page.update_codes()
      variants_page.delete_size_new() # delete_logic() is deprecated and has been replaced with delete_size() look at delete_size() comments for more info
      elapsed_time = time.perf_counter() - start_time
      print(f"delete_size() Elapsed time: {elapsed_time:0.4f} seconds")

      variants_page.sort_sizes()
      # start_time = time.perf_counter()
      variants_page.delete_combination()
      # elapsed_time = time.perf_counter() - start_time
      print('finished with delete_sizes()')
      variants_page.add_variant_image()

      print(f"delete_combination() Elapsed time: {elapsed_time:0.4f} seconds")
      logger.info(f'Done with {file}. \n Moving to {DirLocation.bgt_done}')
      shutil.move(processing_file, DirLocation.bgt_done) # Move to done folder
    except Exception as e:
      logger.critical(f'Error happend while trying to process the file moving back to {DirLocation.bgt_processing}')
      driver.close()
      driver.quit()

      #**** Move to Error folder *##
      shutil.move(processing_file, DirLocation.bgt_error)
  # logger.complete(f'PROGRAM COMPLETED SUCCESSFULLY. Completed {count} Products.\n{finished_url_array}') # Made changes to the loggin init
  logger.critical(f'PROGRAM COMPLETED SUCCESSFULLY. Completed {count} Products.\n{finished_url_array}\nTime: {time.perf_counter() - begin_time:0.4f} seconds') # Made changes to the loggin init
  # need to get an email

global browser

def main_():
  """
  1. Assumption is that for main to be called there must be at least one json present in the add folder, and that a browser has 
  already been created

  """

  try:
    # file = glob('*.json')[0]
    os.chdir(DirLocation.add_to_bgtown)
    try:
      file = glob('*.json')[0]
      if not Path(f'{DirLocation.bgt_processing}\\{file}').exists(): # check to make sure file isn't already processing
        logger.info(f'File found, moving it to processing.\nFile: {file}')
        processing_file = shutil.move(file, DirLocation.bgt_processing)
    except Exception as e:
      logger.info(f'File not found when trying to move it.\nFile: {file}')
      exit()
    
    json_object = FileHandler(processing_file).open_json()
    url, is_floor = get_base_url(json_object)

    driver = set_driver(browser) # using a global variable sucks
    wait_until(Text(Locators.save_and_continue).exists) # important to avoid reloading the page
    go_to(url)

    prod_home = BaseProduct(**json_object)
    variants_page = Variants(**json_object)
    logger.info(f'Available sizes {len(json_object["sizes"])}: {json_object["sizes"]}')
    prod_home.copy_product()
    prod_home.add_tags()
    prod_home.prod_img()
    prod_home.add_category()
    # finished_url_array.append(get_driver().current_url)
    prod_home.save_and_edit()

    wait_until(Text(Locators.published).exists)
    prod_home.go_to_variants()
    # if is_floor != True: # floors do not have attribute logic to delete\\
      # variants_page.delete_logic()  # delete_logic may be deprecated as delete_size() does the same
    start_time = time.perf_counter()
    variants_page.update_codes()
    variants_page.delete_size_new() # delete_logic() is deprecated and has been replaced with delete_size() look at delete_size() comments for more info
    elapsed_time = time.perf_counter() - start_time
    print(f"delete_size() Elapsed time: {elapsed_time:0.4f} seconds")

    variants_page.sort_sizes()
    # start_time = time.perf_counter()
    variants_page.delete_combination()
    # elapsed_time = time.perf_counter() - start_time
    print('finished with delete_sizes()')
    variants_page.add_variant_image()

    print(f"delete_combination() Elapsed time: {elapsed_time:0.4f} seconds")
    logger.info(f'Done with {file}. \n Moving to {DirLocation.bgt_done}')
    shutil.move(processing_file, DirLocation.bgt_done) # Move to done folder
  except (Exception, KeyboardInterrupt) as e:
    logger.critical(f'Error happend while trying to process the file moving back to {DirLocation.bgt_error}')
    # shutil.move(processing_file, DirLocation.bgt_error) # Move to error folder
    driver = get_driver()
    driver.close()
    driver.quit()

    #**** Move to Error folder *##
    shutil.move(processing_file, DirLocation.bgt_error)
  # logger.complete(f'PROGRAM COMPLETED SUCCESSFULLY. Completed {count} Products.\n{finished_url_array}') # Made changes to the loggin init
  # logger.critical(f'PROGRAM COMPLETED SUCCESSFULLY. Completed {count} Products.\n{finished_url_array}\nTime: {time.perf_counter() - begin_time:0.4f} seconds') # Made changes to the loggin init
  # need to get an email

def start_up():
  ############ Start Web Driver then loging ###########
  url = Locators.base_prod_url
  try: # Try to see if driver is already running, if it is then we have already logged in previously
    global browser
    browser = DriverSetup(url, headless=False)
    Login()
  except Exception as e:
    logger.error('Driver not running yet, attempting to open one then log in')
    # Login(url, headless=False) # param: headless=False is false be default, change it to run in headless mode
  
  try: # Wait for button on Admin page
    wait_until(Text(Locators.save_and_continue).exists)
  except TimeoutException as e:
    logger.info(f'Timeout error on first load of the page. Reloading...\n')
    refresh()
    wait_until(Text(Locators.save_and_continue).exists)
  

def get_base_url(json_object):
  # Determine product type \\work\production\backgroundtown images\Serendipity\web\Maya_8x10.jpge based on json key
  is_floor = False
  if 'floor_themes' in json_object:
    is_floor = True
    logger.info('Floor found! Using floor layout')
    url = Locators.base_floor_prod_url
    return url, is_floor
  else:
    logger.info('No floor found! Using backdrop layout')
    url = Locators.base_prod_url
    return url, is_floor


if __name__ == '__main__':
  os.chdir(DirLocation.add_to_bgtown) # Change directory to folder to look in before the loop
  # start_up()
  while True:
    if not glob(f'{DirLocation.add_to_bgtown}*.json'): # folder is empty or no json files, wait x amount of seconds
      time.sleep(300)
    else:
      p = mp.Process(target=main)
      p.start()
      p.join()
      time.sleep(1)
  # all memory used by the subprocess will be freed to the OS\\work\production\backgroundtown images\Serendipity\web\Electric_8x10.jpg\