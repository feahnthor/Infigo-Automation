"""
Author: Henry F.
Description: Contains functions that should only be called while on a base product url such as https://backgroundtown.com/Admin/Product/Edit/{id} 
    Things to note: \
      1. Only one function `upload_img()` is called here and also variants.py, as the upload of an image is exactly the same, only change what is appended to the image name
      2. If any changes has been made to the baseproduct make sure to call save_and_edit(). *add_tags()* does not save unless `save_and_edit()` is called
      3. Function `go_to_variants()` should be the last to be called as it switches to the variants page and should start using variants.py functions
      4. IMPORTANT: 
"""


from selenium.webdriver.support import wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select  # good for options
from selenium.common.exceptions import *

from locators import Locators
from dir_location import DirLocation
from dir_location import Variables
from dir_location import SubFolder
from Pages.login import Login 
from helium import * # to see available methods hit F12 while using VS Code or Visual Studio
import collections
import re
import os
import logging
import sys
import pyautogui
import time

logger = logging.getLogger(__name__)

class BaseProduct:
  def __init__(self, key=None, value=None, **kwargs) -> None:
    """
    Key: string containing key which is a product name
    value: nested dictionary
    :param **kwargs accepts unpacked dictionary argument
    Example calling from main.py: BaseProduct(**dict_object)

    *** For methods that only modifies an existing product I will add these values ****
    """
    try:
      self.name = kwargs['name'].title()
      self.designer = kwargs['designer']
      # self.code = DESIGNER_CODE[self.designer.lower()]
      self.sizes = kwargs['sizes']
      self.colors = kwargs['colors']
      self.tags = kwargs['tags']
      if 'themes' in kwargs:
        self.themes = kwargs['themes']
        self.prod_name = self.name # only ever need this once
      elif 'floor_themes' in kwargs:
        self.themes = kwargs['floor_themes']
        self.prod_name = f'{self.name} Floor' # only need this once
      else:
        logger.warn(f'No Theme provided! {self.name}')
    except Exception as e:
      logger.critical(f'Unable to initialize file, required parameters may be missing \nError Message: {e}')
    self.driver = get_driver()

    self.add = Locators.add_picture
    self.edit = Locators.edit
    self.popup_esc = Locators.popup_esc_tab
    self.update = Locators.update
    self.copy = Locators.copy_prod_btn
    self.edit = Locators.edit
    self.popup_esc = Locators.popup_esc_tab
    self.update = Locators.update
    self.copy = Locators.copy_prod_btn
    self.terminal_recursion = 0


  def copy_product(self):
    """
    Creates a copy of current product, best to create a template product to copy from
    to avoid corrupting the originals
    """
    self.name_field = Locators.new_prod_name
    copy_img = Locators.copy_images_checkbox
    self.check = Locators.copy_extended_checkbox # should only be used for non basic products such as Dynamic ones

    
    wait_until(Text(self.copy).exists)
    # self.driver.find_element_by_id('side-bar__burger').click() # closes sidebar
    try:
      click(self.copy)
    except Exception as e:
      logger.critical(self.name, sys.stderr, f'Could not find Copy Product Button\nProduct: {self.driver.current_url} \nException: {e}' )
      if self.driver != None:
        kill_browser()
      sys.exit(1)
    
    write(self.prod_name, into=self.name_field)
    click(CheckBox(copy_img)) # deselects the copy image option that is default
    click(self.copy)
    # Ensures that the copy product window no longer exist before trying to find anything else
    #https://stackoverflow.com/questions/24928582/expectedcondition-invisibility-of-element-located-takes-more-time-selenium-web
    WebDriverWait(self.driver, 30).until(EC.invisibility_of_element_located((By.ID, Locators.copy_window)))
    self.current_url = self.driver.current_url
    logger.info(f'Product copied successfully.\nCurrent url: {self.current_url}')
    # click(Locators.published) # Sets product to be visible to customers
    wait_until(Text(Locators.show_in_search).exists)
    if not CheckBox(Locators.show_in_search).is_checked():
      click(CheckBox(Locators.show_in_search)) # Sets products to be visible in search results


  def save_and_edit(self):
    '''
    ***Must be called second to last as go_to_variants() will be called next***
    '''
    self.save = Locators.save_and_continue
    logger.info('Saving and Continuing Edit...')
    WebDriverWait(self.driver, 30).until(EC.invisibility_of_element_located((By.CLASS_NAME, Locators.tag_window)))
    self.copy_prod_btn_id.location_once_scrolled_into_view
    click(self.save)
    WebDriverWait(self.driver, 30).until(EC.staleness_of(self.copy_prod_btn_id))

  def upload_img(self, web=SubFolder.web, pop_up_window=False, img_name_variant=None, img_type='.jpg', second_driver=False):
    """
    Primarily made to  upload web icon image products,
    [x] ***will need to update handling random files - COMPLETED***
    :param web: The (string) of a subfolder i.e. \\web\\
    :param pop_up_window: Should only be True if this ```upload file``` appears within a \
    popup window as there are more steps needed to close it to return to main window
    :param img_name_variant: The (string) of a text to append to file name.
      Ex: Forest Loner.jpg vs Forest Loner_8x10.jpg
    :param img_typ: The (string) of the file extention, default is .jpg
    ***Will need to update parameters to either be variables in __init__ or remain here***
    ***Need to create check for image already existing***
    """
    # WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, Locators.product_edit_tabs)))
    # wait_until(Text('Pictures').exists)
    self.web = web
    self.upload = Locators.upload # Expected value to be "Upload a file". Open locators.py and search for "upload" to make edits
    self.pop_up = pop_up_window
    self.img_name_variant = img_name_variant
    self.img = DirLocation.production + self.designer + self.web + self.name
    designer_folder = DirLocation.production + self.designer + self.web
    self.img_type = img_type

    if self.img_name_variant != None:
      self.img = self.img_name_variant._str
    else: # should be the main image that shows on the baseproduct page
      if os.path.isfile(f'{self.img}{self.img_type}'): # In case there is an image without an extension, that should be the default
        self.img = f'{self.img}{self.img_type}'
      elif os.path.isfile(f'{self.img}_8x10{self.img_type}'): # sets default image
        self.img = f'{self.img}_8x10{self.img_type}'
      elif os.path.isfile(f'{self.img}_10x8{self.img_type}'):
        self.img = f'{self.img}_10x8{self.img_type}'
      else: # if these sizes do not exist, find a product with it
        base_size = re.search("(\d{1,}'(\d)?x\d{1,}('\d)?)", self.sizes[0]).group(1) # Uses the first size as the default,
            # find match of digit, single quote(') optional digit for cases like 5'x6 that has the digit after the x
        base_size = re.sub("'", '', base_size) # get rid of single quotess
        if os.path.isfile(f'{self.img}_{base_size}{img_type}'):
          self.img = f'{self.img}_{base_size}{img_type}'
          logger.warning(f'The default variant sizes 8x10 and 8x10 did not exist for the base product. Setting {self.img} as default. \nLocation: {self.driver.current_url}')

    logger.info(f'Image to upload in upload_img() {self.img}')
    if os.path.isfile(self.img):
      
      try:
        wait_until(Text(self.upload).exists)

        click(self.upload)
      except (LookupError, Exception) as e: # when adding images in variants, image tab was not clicked
        logger.warning(f'Variants image could not find upload button. {e} \n{self.driver.current_url}\nReloading to try again')
        refresh()
        wait_until(Text('Images').exists)
        click('Images')
        click(self.upload)
      if not second_driver:
        logger.info(f'Available windows: {self.driver.window_handles}')
        write(self.img)
        press(ENTER+ENTER)
        wait_until(Text(self.add).exists)
      elif second_driver: # tries to close the explorer window 
        # img_upload = self.driver.find_element_by_css_selector('.uploaded-image img')
        time.sleep(1)
        pyautogui.write(self.img)
        time.sleep(1)
        # onscreen = pyautogui.onScreen(794, 504)
        pyautogui.moveTo(794, 504)
        # pyautogui.moveTo(495, 480)
        # pyautogui.moveTo(495, 450)
        # file_upload_btn_location = pyautogui.locateOnScreen('\\\\work\\tech\\henry\\programs\\python\\bgt-automate\\file_okay_btn.png')
        # pyautogui.moveTo(1060, 800)
        # btn_point = pyautogui.center(file_upload_btn_location)
        # btn_x, btn_y = btn_point
        pyautogui.click()
        # pyautogui.click(btn_x, btn_y)
        # pyautogui.press('enter')
        img_upload = self.driver.find_element_by_css_selector('.uploaded-image img')
        foo = img_upload.get_attribute('src')
        try:
          WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'qq-upload-success'))) # only appears after image has been uploaded
        except TimeoutException as e:
          self.terminal_recursion += 1
          logger.error(f'pyautogui was not able to write the image in calling prod_img() again\nRecursion Count: {self.terminal_recursion}\nUrl: {self.current_url}')
          # pyautogui.getActiveWindow()
          # foo = pyautogui.getAllTitles()
          # pyautogui.getWindowsWithTitle('File Upload')
          # pyautogui.press('esc')
          if self.terminal_recursion < 5:

            self.prod_img()
          else:
            pass
        # https://stackoverflow.com/questions/70048615/how-to-wait-for-img-src-attribute-to-change-using-selenium-and-javascript
      WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'qq-upload-success'))) # only appears after image has been uploaded
      try:
        click(self.add)
        # WebDriverWait(self.driver, 30).until(EC.presence_of_all_elements_located((By.CLASS_NAME, '#entitiypictures-grid td')[2]))
        # uploaded_image_element = self.driver.find_elements_by_css_selector('#entitiypictures-grid td')
        # print(len(uploaded_image_element))
        # if second_driver:
        #   get_driver().close() # close the second driver
      except Exception as e:
        click(self.add)
        logger.critical(f'THIS IS AN ERROR THAT NEEDS TO BE RESOLVED, POSSIBLY NO IMAGE UPLOADED {e}')
        if Alert().exists():
          Alert().accept()

      ###### BUG FIX ######

        logger.info('Attribute combination page upload image pop closed successfully')
    else:
      logger.warning(f'{self.img} did not exist {self.driver.current_url}')
      # if second_driver:
      #     get_driver().close() # close the second driver
      pass
  def prod_img(self):
    """
    Clicks image tab then calls upload image
    To stop the automatic wait for the second browswer window to close, comment out the Login(), second_driver(), then change BaseProduct.upload_img(..., second_driver=False) 
    """
    self.pic_tab = Locators.picture_tab
    self.url = self.driver.current_url

    # Login(self.url, headless=False)
    # second_driver = get_driver()


    wait_until(Text(self.pic_tab).exists, timeout_secs=10)
    click(self.pic_tab)
    BaseProduct.upload_img(self, second_driver=True)

  def add_tags(self):
    """

    ***Does not yet handle new tags - `Complete`***
    For scrollable UI elements that do not create their own window handles such as list using methods\
      scroll_down(), press(```Keys for scrolling```) only affects the main window \
        driver().location_once_scrolled_into_view allows for scrolling into view
          https://stackoverflow.com/questions/41744368/scrolling-to-element-using-webdriver
    """
    tags = self.tags + [self.designer] + self.colors # designer is a string, has to be made into a array for concatenation
    logger.info(f'These are the tags we are going to add {tags}')
    # Resolves Karas issue of not having to type the tags into the intranet form. desinger, colors, and themes will be added to the tags
    self.tag_loc = Locators.tag_class
    wait_until(Text(self.copy).exists)
    self.copy_prod_btn_id = self.driver.find_element_by_id('copyproduct')

    press(END)

    click(TextField(to_right_of=Locators.tag_field))
    try:
      wait_until(Text(Locators.first_tag).exists) # wait for first element in tags to be visible
    except Exception as e:
      logger.critical(self.name, sys.stderr, f'Could not find Copy Product Button\nProduct: {self.driver.current_url} \nException: {e}' )

    # All elements available in the tag window. Not a string but an object that references the exact element on page
    self.tag_elements = self.driver.find_elements_by_class_name(self.tag_loc)
    converted_tag_dict = {}
    new_tags = ''
    for element_ref in self.tag_elements:
      # update dict with name as key and value as the reference to the element
      converted_tag_dict[element_ref.get_attribute('textContent').lower()] = element_ref

    for tag_to_add in tags:
      if tag_to_add.lower() not in converted_tag_dict: # no condition to handle numbers
        logger.warning(f'{tag_to_add.title()} tag does not exist. {self.name} \n{self.driver.current_url}')
        # Adds tags to tags to write
        new_tags += tag_to_add.title() + ', ' # Add tag if it doesn't exist
      else:
        try:
          logger.info(f'Adding {tag_to_add.title()}')
          # Brings tag into view using element reference provided by 'find_elements_by_class_name()
          converted_tag_dict[tag_to_add.lower()].location_once_scrolled_into_view
          click(tag_to_add)
        except Exception as e:
          # Not sure when this exception will trigger yet. Hopefully never
          logger.error(f'Exception occurred when trying to select tag: {tag_to_add.title()}\n Product: {self.driver.current_url} \n{sys.stderr}')
    # Write (str) of new tags into empty field. Must save the page to keep changes using Baseproduct.save_and_edit()
    write(new_tags, into=S('.'+Locators.tag_add_text)) # comma seperated
    click('ok')
    WebDriverWait(self.driver, 30).until(EC.invisibility_of_element_located((By.CLASS_NAME, Locators.tag_window)))
    self.copy_prod_btn_id.location_once_scrolled_into_view

  def add_category(self):
    """
    Assumes product is new and has no prior categories
    Assumes there is always no more than 1 designer or theme
    Assumes color is an object within json
    ***Need to check if categories have already been added to avoid repeats***
    """
    category = Locators.category
    add = Locators.add_record
    first = Locators.first
    set_driver(self.driver)

    if 'Backdrops' in self.themes[0]:
      product_type = Locators.backdrop
      extra = ' Backdrops' # Categories on bgt should have 'Backdrops' at the end of `Color` and `Themes`
    else: # Assumes the only other option available is a floor which does not use 'Backdrops' keyword
      product_type = Locators.floor
      extra = ''

    color_categories_to_add_list = [product_type + Locators.color_category + color + extra for color in self.colors ]
    theme_categories_to_add_list = [product_type + Locators.theme_category + theme for theme in self.themes ]
    categories_to_add_list = color_categories_to_add_list + theme_categories_to_add_list + [product_type + Locators.designer_category + self.designer]
    if Alert().exists(): # In case the Add product picture is clicked before the upload is complete
      Alert().accept()
    wait_until(Text(category).exists)
    click(category)

    for category_to_add in categories_to_add_list:
      logger.info(f'Adding Category: {category_to_add}')
      try:
        click(add)
        click(first)
        wait_until(Text('ACI Hot Drops').exists)
      except Exception as e:
       logger.error(sys.stderr, f'Could not find ACI Hot Drops in Category dropdown, this is the first element to be searched for to add a category.\n Failed to add Category {category_to_add}\
       \nProduct: {self.driver.current_url} \nException: {e}' )

      WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 't-item')))
      category_element_list = self.driver.find_elements_by_class_name('t-item')
      category_list = [category for category in category_element_list if category.get_attribute('textContent').lower() == category_to_add.lower()]

      try:
        category_list[-1].location_once_scrolled_into_view
        click(category_list[-1].get_attribute('textContent'))
        click('insert')
      except IndexError as e:

        logger.critical(f'Index error when scrolling to category. The category may not exist \n{category_to_add}\n{self.name}. If the category was blank, then most likely the designer was not \
          added, or the strings do not match exactly. Inspect element and make sure there are no extra spaces or let. {self.designer} \n{self.driver.current_url}')
        pass
      # click(category_list[-1].get_attribute('textContent'))
      # click('insert')

  def go_to_variants(self):
    """
    Assumes page url contains Admin/Product/Edit/ in order to switch variants tab
    """
    self.variants = Locators.variants
    self.unnamed = Locators.unnamed
    self.attr = Locators.attribute

    self.current_url = self.driver.current_url
    var_url = re.sub('/Product/', '/ProductVariant/', self.current_url)

    try:
      go_to(var_url)
      wait_until(Text(self.attr).exists)
      click(self.attr)
    except StaleElementReferenceException:
      logger.warning(f'Unable to go to product variants page. Trying again... {self.name} \n{self.driver.current_url}')
      go_to(var_url)
      wait_until(Text(self.attr).exists)
      click(self.attr)