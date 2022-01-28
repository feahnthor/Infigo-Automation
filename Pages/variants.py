"""
Author: Henry F.
Description: Contains functions that should only be called while on a variant product url such as https://backgroundtown.com/Admin/ProductVariant/Edit/{id} 

"""


import logging
from helium import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC, wait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from Pages.baseproduct import BaseProduct
from locators import Locators
from dir_location import DirLocation
from dir_location import Variables
from dir_location import SubFolder
from file_handler import FileHandler
import os
import re
import sys
import numpy as np
import pathlib
from dotmap import DotMap
from natsort import natsorted
import time

"""
Stale element reference 
https://stackoverflow.com/questions/16166261/selenium-webdriver-how-to-resolve-stale-element-reference-exception
"""
logger = logging.getLogger(__name__)

NEW_SIZES = {

}

class Variants(BaseProduct): # Implements BaseProduct

  def __init__(self, **kwargs) -> None:
    # invoke BaseProduct.__init__
    super().__init__(**kwargs) # Allows for this method to call methods variables as though in the baseproduct.py file
    print(self.name) # test to make sure that BaseProduct has been implemented correctly, as self.name is the first thing declared in the __init__()
    # `self` is an object that now contains all functions and variables stored to in in baseproduct.py
    self.url = self.driver.current_url
    self.conf = FileHandler('\\\\work\\tech\\Henry\\Programs\\Python\\bgt-automate\\Update_product\\Config\\.toml').open_toml()
    self.m_design_conf = DotMap(self.conf).designer_code # now able to use dot notation for object/dict : means mapped designer config
    self.var_conf = DotMap(self.conf).var # Variables to use for elements

  def get_combination_elements(self):
    """
    Function to get the buttons that will be clicked, sizes, and columns for each of the 
    attribute combination elements.
    Assumes there is at least 1 element present
    Returns list containing list
    https://stackoverflow.com/questions/28022764/python-and-how-to-get-text-from-selenium-element-webelement-object
    
    If there happens to be a deleted name still remaining. Make sure that things are spelled correctly and the correct case.
      Ex: 8'x10' UltraCloth !=  8'x10' Ultracloth     ---there is a lower case 'c'----
    """
    self.base_image_loc = DirLocation.production + self.designer + SubFolder.web + self.name
    
    elements_list = []
    elements_dict = {}
    # Stores elements for each rows
    row_elements = np.array(self.driver.find_elements_by_css_selector(Locators.attribute_combinations))
    # Store columns from row_elements such as SKU, Attributes
    # row_column_elements = row_elements.find_element_by_css_selector('td')
    for row_element in row_elements:
      try:
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td')))
      except Exception as e:
        logger.warning('unexpected error ',e)
        refresh()
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'td')))
      column_elements = row_element.find_elements_by_css_selector('td')
      attribute = column_elements[0].text # use getText() to keep <br> from ignoring \n
      sku = column_elements[3].get_attribute('textContent')
      edit_btn = row_element.find_element_by_css_selector('td input')
      delete_btn = column_elements[-1]
      attribute = re.sub('\\n.*', '', attribute) #get newline character and everything after in regex
      combination_size = re.sub('^.*: ', '', attribute) # can be found in regex notes
      combination_size = re.sub('"', '', combination_size) # string
      size = re.sub(' .*', '', combination_size)
      size = re.sub("'", '', size) # size should now be something like 8x8
      elements_list.append([combination_size, size,  attribute, sku, edit_btn, delete_btn])
      elements_dict[combination_size] = delete_btn
    return elements_list, elements_dict

  def add_variant_image(self):
    """
    ***Page does not need to reload to add an image, so only calling get_combination_elements() once is enough***
    Helium does not seem to be able to recognize when selenium switches to a new window. No idea why it doesn't work in this function
    but is able to work perfectly fine and make helium calls in the BaseProduct.upload_img() method
    so its best to use selenium methods to find elements, then use helium for clicks using the selenium web-element
    """
    click('Attribute Combination')
    combination_elements_list, foo = self.get_combination_elements() # index 0 is the string of the size

    for row_elements in combination_elements_list:
      print(row_elements[0], row_elements[1])
      comb_size, size, attr, sku, edit_btn, del_btn = row_elements
      logger.info(f'adding image {self.base_image_loc}_{row_elements[1]}')
      file = pathlib.Path(f'{self.base_image_loc}_{row_elements[1]}.jpg') # now a file object
      if file.exists():
        logger.info(f'Found image variant {file}')
        edit_btn.location_once_scrolled_into_view
        click(edit_btn)
        browser_windows = self.driver.window_handles
        self.driver.switch_to.window(browser_windows[-1]) # switch to newest browser
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, Locators.image_tab)))
        img_tab = self.driver.find_elements_by_css_selector(Locators.image_tab)
        click(img_tab[1])
        BaseProduct.upload_img(self, pop_up_window=True, img_name_variant=file)
        self.close_window() # closes window without saving to prevent staleelement exception
      elif not file.exists():
        logger.warning(f'Could not find variant image file {file}\n{self.name} {self.driver.current_url}')
    variant_top = self.driver.find_element_by_id(Locators.top_of_variant_page)
    variant_top.location_once_scrolled_into_view

    self.terminal_recursion = 0 # reset recursion after product is done

  def delete_combination_new(self):
    """
    NOT DONE YET
    If all combinations sizes are deleted, it might be a backdrop with a Floor_themes instead of a backdrop themes
    """
    m = self.var_conf
    url = self.driver.current_url
    wait_until(Text(Locators.attribute).exists)
    click(Locators.attribute)
    click('Attribute combinations')

    try:
      try:
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.combination.size_name))) # find each name in the second column
        WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, m.combination.delete_btn))) # finds each delete button, at index 11
        
        attribute_list = np.array(self.driver.find_elements_by_css_selector(m.combination.size_name))
        delete_btn_list = np.array(self.driver.find_elements_by_css_selector(m.combination.delete_btn))
      except Exception as e:
        logger.warning(f'Unable to find size elements in order to sort them. Refreshing then trying again {e}')
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.combination.size_name)))
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.combination.delete_btn)))
        attribute_list = np.array(self.driver.find_elements_by_css_selector(m.combination.size_name))
        delete_btn_list = np.array(self.driver.find_elements_by_css_selector(m.combination.delete_btn))

      all_attributes = [size.get_attribute('textContent') for size in attribute_list] # get string of sizes
      for size_attribute in all_attributes:
        try:
          size = re.search('CanvasSize: (.*)Mentor',size_attribute).group(1)
        except AttributeError as e:
          logger.error(f'Attribute size did not match the Regular Expression.\nOriginal: {size_attribute}\n{e}') 
          size = re.search(':CanvasSize:\s\d{3,}',size_attribute).group(1)
        if size not in self.sizes and 'NewFab' not in size: # NewFab contains double quotes in size name 3'9"x5' NewFab
          # size_compare = re.sub('"', '', size_list[count].get_attribute('textContent')).lower() # get rid of double quotes Ex: 3'9"x5' NewFab => 3'9x5
          size_column_element = self.driver.find_element_by_xpath(f'''//*[text() = "{size}"]''') # FIND ELEMENT BASE, tHANKS TO THE
          parent_element = size_column_element.find_element_by_xpath('./..') # Get parent element in order to use it to find the edit button for this sizes row
          size_element_from_parent = parent_element.find_element_by_css_selector('td:nth-of-type(2)').get_attribute('textContent')
          delete_btn_element_from_parent = parent_element.find_element_by_css_selector(m.size.delete_btn_from_parent)
          logger.info(f'Size {size} not part of the sizes to add {self.sizes}')
          delete_btn_element_from_parent.location_once_scrolled_into_view
          delete_btn_element_from_parent.click()
          try:
            wait_until(Alert().exists)
          except Exception as e:
            logger.warning(f'Expected error {e}\n{self.driver.current_url}')
            logger.info(f'Alert did not come up after trying to delete {size}')
            delete_btn_element_from_parent.location_once_scrolled_into_view # count - 1 to use the same value as size_compare
            delete_btn_element_from_parent.click()
            wait_until(Alert().exists)
          Alert().accept() # page will be refreshed after and elements will become stale
          try:
            WebDriverWait(self.driver, 5).until(EC.staleness_of(delete_btn_element_from_parent)) # waits for button to actually be off the DOM
          except IndexError as e:
            logger.warning(f'delete button element reference for {size} removed before the WebDriverWait could find it. \n\
            Size should be deleted so not much of a problem. This `warning` can probably be made `info`\n{self.driver.current_url}\n{e}')
      
      
    except Exception as e:
      logger.error(f'Unexpected error when in the delete_size function at {self.driver.current_url}, will try to reload then call the function again')
      # refresh()
      go_to(url)
      self.delete_size_new()
      wait_until(Text(Locators.attribute).exists)
      click(Locators.attribute)

    go_to(url) # Should be done, going back to Variants page so the next function can go
    wait_until(Text(Locators.attribute).exists)
    click(Locators.attribute)

    pass
  
  def delete_combination(self):
    """
    ***Deleting an element will reload the page, will need to call get_combination_element in a loop to
    avoid Stale Element Exceptions***
    ***An alert pops up after hitting delete with options 'Ok' and 'Cancel'***
    # Need to increase speed of these loops, much slower than `delete_sizes()`
    """

    click('Attribute Combination')
    try:
      row_elements = np.array(self.driver.find_elements_by_css_selector(Locators.attribute_combinations))
      total_combinations = len(row_elements)

      ####### INFINITE LOOP ########
      #1. Possible infinite Loop the value for `size` and `self.sizes` are not exact `8x10 Ultracloth` vs `8x10 UltraCloth`
      #2. There is an
      while total_combinations != len(self.sizes): # becomes an infinite loop if extra sizes were deleted manually in delete_sizes as each attribute will no longer match when on this page
        foo, combination_elements_dict = self.get_combination_elements()
        for size, del_btn in combination_elements_dict.items():
          foo, combination_elements_dict = self.get_combination_elements()
          total_combinations = len(foo) # PREVENTS INFINITE LOOP: before 
          if size not in self.sizes:
            logger.info(f'{size} not in sizes to add {self.sizes}')
            # total_combinations = len(foo)
            combination_elements_dict[size].location_once_scrolled_into_view
            click(combination_elements_dict[size])
            Alert().accept() #page will be refreshed after and elements will become stale
            WebDriverWait(self.driver, 10).until(EC.staleness_of(combination_elements_dict[size]))
    
            WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, Locators.attribute_combinations)))
    except Exception as e:
      logger.error(f'{self.name}\n{self.driver.current_url}\n', sys.stderr, f'Something went wrong in Variants.delete_combinations()\nProduct: {self.driver.current_url} \nException: {e}' )
      pass
    variant_top = self.driver.find_element_by_id(Locators.top_of_variant_page)
    variant_top.location_once_scrolled_into_view 
    logger.info(f'Attribute Combinations deleted')

  def split_list(self, list, amount=2, filler=None):
    """ 
    ***Currently not in use by this program, but is still a useful function***
    Splits an array/list into equal smaller lists. Default amount is set to 2
    ***Should be made into a help function in another class***
    taken from https://appdividend.com/2021/06/15/how-to-split-list-in-python/
    :param list: The (list) that needs to be separated 
    :param amount: (int) value to separate each list/array into, defaults to 2 
    :param filter: Can be any type, will fill any remaining indexes of the list/array, default none
      Ex: [[1,2,5,20], [21, 28, None, None, None]] 
    """
    completed_chunks = []
    for i in range(0, len(list), amount):
      try:
        chunk = list[i: amount+i]
        completed_chunks.append(chunk) # add the list containing chunks to the whole 
      except Exception as e:
        logger.critical(f'{self.name}' f'{sys.stderr}\nSpliting failed, please ensure that a list was sent through and the amount was a positive integer\
          {e}')
      if len(chunk) < amount:
        # chunk.append([filler for y in range(amount - len(chunk))]) # add filler content to chunk
        np.append(chunk, [filler for y in range(amount - len(chunk))])
    return completed_chunks
  # New Page Attributes
  def edit_combinations(self):
    """
    Assumes attribute combinations are already present,
    Assumes SKUs are present as well
    Must have sizes be visible before scrolling on the current window or get a LookupError
    Should only call upload method if there exist a variant size of the image
    Do not need to upload the normal version of the image here as that has been done in the baseProduct() class
    """
    self.images = Locators.images
    self.web = SubFolder.web
    self.foo = DirLocation.production + self.designer + self.web + self.name
    self.img_type = '.jpg'
    click('Attribute combinations')
    scroll_down(num_pixels=380)
    for v in self.sizes:
      "v is the (string) of the size in this case ex. 8x20 Background"
      a = re.sub(' RubberMat', '', v)
      a = re.sub(' UltraCloth', '', a)
      a = re.sub(' NewFab', '', a)
      
      variant_size = f'_' + re.sub("'", "", a)
      
      variant_size2 = f' ' + re.sub("'", "", a)
      self.variant_image = self.foo + variant_size + self.img_type
      self.variant_image2 = self.foo + variant_size2 + self.img_type
      print(f'trying {self.variant_image}\n')
      if os.path.isfile(self.variant_image) or os.path.isfile(self.variant_image2):
        
        print(self.variant_image, 'EXIST')
        while True:
          try:
            print(v)
            #value for pixels gotten from $("#attributecombinations-grid").offset().top + window.screenY;
            wait_until(Button(self.edit).exists)

            scroll_down(num_pixels=20)
            print('buttttosdfhdsdf',Button(self.edit, to_right_of=Text(v)))
            
            click(Button(self.edit, to_right_of=Text(v)))
            wait_until(Text(self.images).exists)
            click(self.images)
            BaseProduct.upload_img(self, pop_up_window=True, img_name_variant=self.variant_image)
            break
          except Exception as e:
            print('Caught ', e, 'at size', v)
            self.close_window(self)
            
      else:
        print(self.variant_image,  'DOES NOT EXIST')
        
        pass
    # go_to(Locators.base_prod_url)       

  def close_window(self):
    """
    this function may no longer be needed as selenium has the expected conditions of 
    `new_window_is_opened(current_handles)` and `number_of_windows_to_be(num_windows)`
    https://www.selenium.dev/selenium/docs/api/py/webdriver_support/selenium.webdriver.support.expected_conditions.html#module-selenium.webdriver.support.expected_conditions
    """
    # windows = self.driver.window_handles
    try:
      WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(2))
      windows = self.driver.window_handles
      if len(windows) > 1:
        self.driver.switch_to.window(windows[-1])
        logger.info(f'attempting to close the new window')
        self.driver.close()
        WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(1))
    finally:
      logger.info('Switching back to main window')
      WebDriverWait(self.driver, 10).until(EC.number_of_windows_to_be(1))
      self.driver.switch_to.window(windows[0])
    
    # if len(windows) > 1:
    #   try:
    #     print(f'Attempting to close second window')
    #     self.driver.close()
    #     if (self.driver.window_handles) > 1:
    #       logger.warning(f'The ammount of windows opened after trying to close the other is greater than 1 {self.driver.window_handles}')
    #       self.driver.
    #   self.driver.switch_to.window(windows[0])
    # else:
    #   self.driver.switch_to.window(windows[0])

  def delete_logic(self):
    """
    ------Deprecated: delete sizes does this as a side effect--------
    ***Major issue that keeps presenting a stale element exception after successfully deleting
    a item, trying to call logic_elements[i] fails --COMPLETED used expected condition .stalenessof
    https://stackoverflow.com/questions/60535663/how-to-scroll-a-web-page-down-until-specific-button-to-click
    Used ids in id_list as references to find elements using ids since they do not change on reload thanks to Jarred,
    ***Searching by id attribute to find the id must be done with find_element_by_id()***
    """
    try:
      logic_elements = self.driver.find_elements_by_css_selector(Locators.attribute_logic_list_id)
      id_list = [element.get_attribute('id') for element in logic_elements]

      for id in id_list:
        wait_until(Text('Show').exists)
        total_elements = self.driver.find_elements_by_css_selector(Locators.attribute_logic_list_id)
        current_element = self.driver.find_element_by_id(f'{id}')
        size = current_element.find_elements_by_css_selector('span')[3].get_attribute('textContent')
        delete_btn = current_element.find_element_by_css_selector(f'a')
        size = re.sub('"', '', size)
        if size not in self.sizes:
          delete_btn.location_once_scrolled_into_view
          delete_btn.click()
          WebDriverWait(self.driver, 10).until(EC.staleness_of(delete_btn))
          WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, Locators.attribute_logic_list_id)))
        if len(total_elements) == len(self.sizes): #should be done.
          break
    except Exception as e:
      logger.critical(f'{self.name}', sys.stderr, f'Could not find Logic delete button\nProduct: {self.driver.current_url} \nException: {e}' )
      pass
    variant_top = self.driver.find_element_by_id(Locators.top_of_variant_page)
    variant_top.location_once_scrolled_into_view  

  def update_codes(self):
    """
    Need to update to take in a unknown amount of attributes
    ***issue where exception pops up on attributes page  ***
    """

    designer = re.sub('\s', '_', self.designer.lower()) # will provide the string used to access the config and get the right product code
    if designer not in self.m_design_conf:
      logger.critical(f'Designer {designer} is present in the config file as a designer \\..\\Config\\.toml \n{self.driver.current_url}')
      pass
    nf_code = self.m_design_conf[designer]['new_fab']
    reg_code = self.m_design_conf[designer]['regular']
    handles = self.driver.window_handles
    cur_url = self.driver.current_url


    try: 
      wait_until(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_2).exists) # to the right of "Mentor"
      click(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_2))
      wait_until(Text(self.edit).exists)
      ############## Add Regular Code ###############
      # WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR))) # wait for new window to open
      click(Text(self.edit, to_right_of='40')) # Regular designs have a price of $40
      WebDriverWait(self.driver, 5).until(EC.number_of_windows_to_be(2)) # wait for new window to open
      self.driver.switch_to.window(self.driver.window_handles[-1])
      wait_until(Text(Locators.code_name).exists)
      write(reg_code, into=TextField(to_right_of=Locators.code_name))
      write(reg_code, into=TextField(to_right_of=Locators.code_f_name))
      click('Save')
      self.driver.switch_to_window(handles[0])

      ############# Add NewFab code ################
      if Text('12.5').exists():
        try:
          click(Text(self.edit, to_right_of='12.5'))
        except StaleElementReferenceException as e:
          logger.warning(f'StaleElementReference when trying to change product codes, \nProduct: {self.name}\nLoaction: {self.driver.current_url}\nMessage: {e}\Resolution: Attempting to reload..')
          refresh()
          wait_until(Text(self.edit).exists)
          click(Text(self.edit, to_right_of='12.5'))

        WebDriverWait(self.driver, 5).until(EC.number_of_windows_to_be(2))
        wait_until(Text(Locators.code_name).exists)
        write(nf_code, into=TextField(to_right_of=Locators.code_name))
        write(nf_code, into=TextField(to_right_of=Locators.code_f_name))
        click('Save')
        self.driver.switch_to_window(handles[0])
    except Exception as e:
      logger.warning(f'Unhandled exception  when trying to Update Codes for designer in config {designer} {self.name} \n{self.driver.current_url}\n{e}')
    finally:
      #### Go back to variants ####
      self.driver.switch_to_window(handles[0])
      go_to(cur_url)
      wait_until(Text(Locators.attribute).exists)
      click(Locators.attribute)

  def update_price_aci(self, *args):
    """
    ***DEPRECATED**
    """
    handles = self.driver.window_handles

    wait_until(Text('Tier prices').exists)
    click(Locators.attribute)
    print(f'UPDATING Prices! Prices AVAILABLE')
    wait_until(Text(Locators.attribute_edit).exists)
    # total = re.findall('[0-9]',Text(Locators.attribute_edit).value)[0]
    
    click(Locators.attribute_edit)

    # wait_until(Button('Edit').exists)
    
    print('bttuon sdfsdfd')                                                                            
    # foo = re.sub('[0-9]+', Text(Locators.attribute_edit).value)[0]
    
    # print('Total', foo)
    # click(Text(Locators.attribute_edit))
    # wait_until(Text(self.edit).exists)
    wait_until(Button('Edit').exists)
    edit_btns = find_all(Button('Edit'))
    # print(edit_btns,)
    print('Total sizes available', len(edit_btns))
    for i in range(len(edit_btns)):
      print('before while true')
      while True:
        print('before try')
        try:
          print('before conditions', print(edit_btns[i]))
          wait_until(Text('Edit').exists)
          print('found button')
          # click(edit_btns[i])
          click('edit')
          print('after click')
          wait_until(Text(Locators.price).exists)
          price = int(TextField(to_right_of=Locators.price).value)
          print('PRICE:', price)
          if price == 72:
            write('84.50', into=TextField(to_right_of=Locators.price))
            click('Save')
            self.driver.switch_to_window(handles[0])
          elif price == 110:
            write('122.50', into=TextField(to_right_of=Locators.price))
            click('Save')
            self.driver.switch_to_window(handles[0])
          else:
            new_price = price + 40
            write(new_price, into=TextField(to_right_of=Locators.price))
            click('Save')
            self.driver.switch_to_window(handles[0])
          break
        except Exception as e:
          print('Caught ', e, 'update price aci')
          break
          # BaseProduct.close_window(self)
    pass
  
  def go_back_to_variant(self):
    # self explanatory
    go_to(self.url)

  def delete_size_new(self):
    """
    Thanks to the XPATH I can just use a for loop to look for sizes to delete only based off the size name. This way ignores the old method that used a while loop, that method
      was longer and relied on counting how many products are there.
    """
    m = self.var_conf
    url = self.driver.current_url

    try:
      wait_until(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1).exists)
      click(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1))
    except StaleElementReferenceException as e:
      logger.warning(f'Stale Element exception  when trying to find {Locators.attribute_label_1} in delete_size {self.name} \n{self.driver.current_url}')
      refresh() # after refresh need to get back to Attributes tab
      click(Locators.attribute)
      wait_until(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1).exists)
      click(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1))

    try:
      try:
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.size.size_name))) # find each name in the second column
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.size.delete_btn))) # finds each delete button, at index 11
        
        size_list = np.array(self.driver.find_elements_by_css_selector(m.size.size_name))
        delete_btn_list = np.array(self.driver.find_elements_by_css_selector(m.size.delete_btn))
      except Exception as e:
        logger.critical(f'Unable to find size elements in order to sort them. Refreshing then trying again {e}')
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.size.size_name)))
        WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.size.delete_btn)))
        size_list = np.array(self.driver.find_elements_by_css_selector(m.size.size_name))
        delete_btn_list = np.array(self.driver.find_elements_by_css_selector(m.size.delete_btn))

      all_sizes = [size.get_attribute('textContent') for size in size_list] # get string of sizes
      for size in all_sizes:
        if size not in self.sizes and 'NewFab' not in size: # NewFab contains double quotes in size name 3'9"x5' NewFab
          # size_compare = re.sub('"', '', size_list[count].get_attribute('textContent')).lower() # get rid of double quotes Ex: 3'9"x5' NewFab => 3'9x5
          size_column_element = self.driver.find_element_by_xpath(f'''//*[text() = "{size}"]''') # FIND ELEMENT BASE, tHANKS TO THE
          parent_element = size_column_element.find_element_by_xpath('./..') # Get parent element in order to use it to find the edit button for this sizes row
          size_element_from_parent = parent_element.find_element_by_css_selector('td:nth-of-type(2)').get_attribute('textContent')
          delete_btn_element_from_parent = parent_element.find_element_by_css_selector(m.size.delete_btn_from_parent)
          logger.info(f'Size {size} not part of the sizes to add {self.sizes}')
          delete_btn_element_from_parent.location_once_scrolled_into_view
          delete_btn_element_from_parent.click()
          try:
            wait_until(Alert().exists)
          except Exception as e:
            logger.warning(f'Expected error {e}\n{self.driver.current_url}')
            logger.info(f'Alert did not come up after trying to delete {size}')
            delete_btn_element_from_parent.location_once_scrolled_into_view # count - 1 to use the same value as size_compare
            delete_btn_element_from_parent.click()
            wait_until(Alert().exists)
          Alert().accept() # page will be refreshed after and elements will become stale
          try:
            WebDriverWait(self.driver, 5).until(EC.staleness_of(delete_btn_element_from_parent)) # waits for button to actually be off the DOM
          except IndexError as e:
            logger.warning(f'delete button element reference for {size} removed before the WebDriverWait could find it. \n\
            Size should be deleted so not much of a problem. This `warning` can probably be made `info`\n{self.driver.current_url}\n{e}')
      
      
    except Exception as e:
      logger.warn(f'Unexpected error when in the delete_size function at {self.driver.current_url}, will try to reload then call the function again')
      # refresh()
      go_to(url)
      self.delete_size_new()
      wait_until(Text(Locators.attribute).exists)
      click(Locators.attribute)

    go_to(url) # Should be done, going back to Variants page so the next function can go
    wait_until(Text(Locators.attribute).exists)
    click(Locators.attribute)



  def delete_size(self):
    """
    1. Takes in no arguments, uses similar method to delete fields as `Varants.delete_combination()`
    Notes:
      1. Any New size added after that contains a special character besides " can be handled in `size_compare` variable, its best to create a `sanitize_string()` function
      2. `nth-of-type` can be found in mozilla docs is Extremely useful as before i had to create my own functions to separate the array/list of table elements. see `get_combination_elements()` if it hasn't been
      deleted
    2. This MUST run after delete_logic as Infigo will not allow a size to be deleted if the logic still exists.
      *** ABOVE IS NO LONGER TRUE as of 10/13/21. Infigo seems to have updated so if a size is deleted here, it also deletes the logic***
    3. `count` needS to be set back to 0 once a size has been deleted so it starts
    4. The sizes in the dict self.sizes, must have their keys changed to lowercase to account for a lowercase value from the site.
            This will help prevent a value such as 8'x16' Ultracloth from being deleted, and keeping a size that was not wanted thanks to
            the while loop exit condition of `sizes to add from dict` being equal to the `s
    """
    # To change these values go to Locators file
    url = self.driver.current_url
    size_dict_with_lowered_keys = [size.lower() for size in self.sizes]
    try:
      wait_until(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1).exists)
      click(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1))
    except StaleElementReferenceException as e:
      logger.warning(f'Stale Element exception  when trying to find {Locators.attribute_label_1} in delete_size {self.name} \n{self.driver.current_url}')
      refresh() # after refresh need to get back to Attributes tab
      click(Locators.attribute)
      wait_until(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1).exists)
      click(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1))

    name_selector = Locators.variant_name
    del_btn_selector = Locators.var_delete_btn
    row_selector = Locators.var_row_selector

    # nth-of-type(11) ensures delete field is present on the dom too
    WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, row_selector)))
    WebDriverWait(self.driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, del_btn_selector)))

    try:
      size_list = np.array(self.driver.find_elements_by_css_selector(name_selector))
      all_sizes = [size.get_attribute('textContent') for size in size_list]
      logger.info(f'HERE ARE ALL THE SIZES {all_sizes}')
      delete_btn_list = np.array(self.driver.find_elements_by_css_selector(del_btn_selector))
      sizes_left = []
      while len(delete_btn_list) != len(size_dict_with_lowered_keys):
        sizes_left = []
        size_list = np.array(self.driver.find_elements_by_css_selector(name_selector))
        delete_btn_list = np.array(self.driver.find_elements_by_css_selector(del_btn_selector))
        count = 0

        for i in range(len(delete_btn_list)): # assumption is that both size and delete_btn are sorted by their order
          size_list = np.array(self.driver.find_elements_by_css_selector(name_selector))
          delete_btn_list = np.array(self.driver.find_elements_by_css_selector(del_btn_selector))
          # so the goal is to use the index to remove the corresponding size

          size_compare = re.sub('"', '', size_list[count].get_attribute('textContent')).lower() # get rid of double quotes Ex: 3'9"x5' NewFab => 3'9x5
          sizes_left.append(size_compare)
          # size_compare = re.sub(' floor', '', size_compare) # remove floor from string Ex: 4'x5' rubbermat floor => 4'x5' rubbermat
          count += 1 # want count to keep increasing if value is an accepted size
          if '20' in size_compare:
            logger.info(f'FOUND A SIZE WITH 20 {size_compare}')
          if size_compare in size_dict_with_lowered_keys:
            logger.info(f'Size {size_compare} is in {size_dict_with_lowered_keys} not deleting Attribute. Please Check')

          elif size_compare not in size_dict_with_lowered_keys:
            logger.info(f'Size {size_compare} not in {size_dict_with_lowered_keys} deleting Attribute')
            delete_btn_list[count - 1].location_once_scrolled_into_view # count - 1 to use the same value as size_compare
            click(delete_btn_list[count - 1])

            try:
              wait_until(Alert().exists)
            except Exception as e:
              logger.warning(f'Expected error {e}\n{self.driver.current_url}')
              logger.info(f'Size {size_compare} not in {size_dict_with_lowered_keys} deleting Attribute')
              delete_btn_list[count - 1].location_once_scrolled_into_view # count - 1 to use the same value as size_compare
              click(delete_btn_list[count - 1])
              wait_until(Alert().exists)
            Alert().accept() # page will be refreshed after and elements will become stale

            ##################### FIX THIS LATER INDEX ISSUES #############
            try:
              WebDriverWait(self.driver, 5).until(EC.staleness_of(delete_btn_list[i])) # waits for button to actually be off the DOM 
            except IndexError as e:
              logger.warning(f'Index error while trying to delete sizes, delete button element reference for {size_compare} removed before the WebDriverWait could find it. \n\
              Size should be deleted so not much of a problem. This `warning` can probably be made `info`\n{self.driver.current_url}\n{e}')
              pass
            count = 0 # reset count back to 0 once size has been deleted. *IMPORTANT*
      if len(delete_btn_list) == len(size_dict_with_lowered_keys): # NEED TO CHECK IF SOMETHING WAS DELETED THAT WASN'T SUPPOSED TO
        logger.info(sizes_left)
        for size in sizes_left:
          if size not in size_dict_with_lowered_keys:
            logger.critical(f'A size that was not supposed to be deleted was deleted. {size} is not part of {size_dict_with_lowered_keys}.\n\n{self.url}')
        
    except Exception as e:
      logger.critical(f'{self.name} \n{self.driver.current_url}\n'  f'Unhandled exception Trying again {e}')
      go_to(url)
      wait_until(Text(Locators.attribute).exists)
      click(Locators.attribute)
      self.delete_size()
      pass
    finally: # will always be executed, not matter if there is an error
      go_to(url)
      wait_until(Text(Locators.attribute).exists)
      click(Locators.attribute)

  def sort_sizes(self, order_difference=5) -> None:
    """
    :param driver: (Webdriver Object) takes an instance of the webdriver object. If there is an attribute error check driver_setup.py 
        to make sure the driver was setup correctly. Drivers should have access to a simple method like `driver.current_url`
    :param order_difference: (int) of what each size will be sorted by. i.e. sort by 5 =>  0, 5, 10, 15
    """
    start_time = time.perf_counter()
    driver = get_driver()
    m = self.var_conf
    url = driver.current_url
    # title = self.click_attribute_tab(driver)
    # need to be in sizes to edit size

    ##################### Go to Sizes #####################
    try:
      WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, m.attr_tab)))
      title_str = driver.find_element_by_class_name('title').get_attribute('textContent')
      title = re.search(': (\w+(\s\w+)?(\s\w+)?)', title_str).group(1) # Same as using $1 in regex
      wait_until(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1).exists)
      click(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1))
    except StaleElementReferenceException as e:
      logger.warning(f'Stale Element exception  when trying to find {Locators.attribute_label_1} in sort_sizes {self.name} \n{self.driver.current_url}')
      refresh() # after refresh need to get back to Attributes tab
      click(Locators.attribute)
      wait_until(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1).exists)
      click(Text(Locators.attribute_edit, to_right_of=Locators.attribute_label_1))

    original_window = driver.current_window_handle

    try:
      try:
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.size.size_name)))
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.size.edit_btn)))
        
        size_list = np.array(driver.find_elements_by_css_selector(m.size.size_name))
        edit_btn_list = np.array(driver.find_elements_by_css_selector(m.size.edit_btn))
      except Exception as e:
        logger.warning(f'Unable to find size elements in order to sort them. Refreshing then trying again {e}')
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.size.size_name)))
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.size.edit_btn)))
        size_list = np.array(driver.find_elements_by_css_selector(m.size.size_name))
        edit_btn_list = np.array(driver.find_elements_by_css_selector(m.size.edit_btn))
      
      
      readable_size_list = [size.get_attribute('textContent') for size in size_list] # get values from position 2 onwards

      ########### TEST PARENT #############
      parent_list = []
      sorted_size_list = natsorted(readable_size_list) # use the index * 5 to set display order
      _sorted = False

      ####### Check to make sure things are sorted before looping ######s
      if sorted_size_list == readable_size_list and "4'x5' UltraCloth" not in sorted_size_list and "5'x4' UltraCloth" not in sorted_size_list and len(sorted_size_list) > 0: # Skip product if already sorted
        _sorted = True
        logger.warning(f'This product {title} is already sorted \n{sorted_size_list}')

      elif len(sorted_size_list) < 1:
        logger.critical(f'empty list for {title} when trying to find size, retrying function sort_sizes()')
        go_to(url)
        wait_until(Text(Locators.attribute).exists)
        click(Locators.attribute)
        self.sort_sizes()

      # while _sorted != True:
      while not _sorted:
        # Check to make sure that current sort is the same as sorted_size
        count = 0
        for i in range(len(edit_btn_list)): # This is only too loop through the total number of sizes
          """
          Does not do its own sort, merely uses the natsorted() result as a reference to what each Display order item should
            be. If there
          1. We find elements again inside the for loop to prevent a StaleElementError on the second and subsequent loops
          """
          WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, m.size.edit_btn)))
          WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, m.size.edit_btn)))
          size_list = np.array(driver.find_elements_by_css_selector(m.size.size_name))
          edit_btn_list = np.array(driver.find_elements_by_css_selector(m.size.edit_btn))
      
          # attr_dict = dict(zip(readable_size_list, edit_btn_list)) # Stores size as key and Edit button as value
          sorted_size_key = sorted_size_list[i]

          # parents_row_using_sizesdfinv = driver.find_element_by_xpath(f'''//*[text() = "8'x10' UltraCloth"]''') # find element using the text visible  https://riptutorial.com/xpath/example/6209/find-all-elements-with-certain-text
          if 'NewFab'  not in sorted_size_key: # With NewFab have double quotes, i was not able to find a way that worked using xpath.
            count += 1 # Assumption is the the sort of NewFabs should already be 0
            size_column_element = driver.find_element_by_xpath(f'''//*[text() = "{sorted_size_key}"]''')
            parent_element = size_column_element.find_element_by_xpath('./..') # Get parent element in order to use it to find the edit button for this sizes row
            size_element_from_parent = parent_element.find_element_by_css_selector('td:nth-of-type(2)').get_attribute('textContent')
            edit_btn_element_from_parent = parent_element.find_element_by_css_selector(m.size.edit_btn_from_parent)

            if sorted_size_key != size_element_from_parent: # Test to make sure the correct Edit button in relation to size is clicked
              print('damn')

            try:
              edit_btn_element_from_parent.location_once_scrolled_into_view
              edit_btn_element_from_parent.click()
            except StaleElementReferenceException as e:
              logger.warning(f'Stale element exception while sorting sizes for  {self.name} at {driver.current_url}\n{e}\nRunning sort_sizes() again')
              self.sort_sizes()

            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
            driver.switch_to.window(driver.window_handles[-1]) # switch to newest windows to edit size
            new_order = str(count*order_difference)
            print(f'Size: {sorted_size_key}: {count} * {order_difference} = {count*order_difference}: passed {new_order} \t\t{driver.current_url}')

            try:
              WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, m.size.window.order)))
              order_field = driver.find_element_by_id(m.size.window.order)
            except NoSuchElementException as e:
              logger.warning(f'Could not find element to change Display order when sorting sizes. \Location: {self.driver.current_url}\Resolution: Trying to refresh the page\nError Message: {e}')
              refresh()
              WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, m.size.window.order)))
              order_field = driver.find_element_by_id(m.size.window.order)

            order_field.clear()
            order_field.send_keys(new_order)
          
            order_field = driver.find_element_by_id(m.size.window.order) # Check if value actually added          

            ##### Close Window #######
            save_btn = driver.find_element_by_css_selector(m.size.window.save_btn)
            save_btn.click()
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(1))
            driver.switch_to.window(original_window)

        _sorted = True # Exit Loop

      elapsed_time = time.perf_counter() - start_time
      logger.info(f"Elapsed time for Variants sort sizes: {elapsed_time:0.4f} Seconds")
    except Exception as e:
      logger.warning(f'Product {title}\nUnhandled exception in \\Update_product\\Pages\\variants.py while trying to sort_sizes() \n{driver.current_url}\n{e}')
    finally: # will always be executed, not matter if there is an error
      go_to(url)
      wait_until(Text(Locators.attribute).exists)
      click(Locators.attribute)