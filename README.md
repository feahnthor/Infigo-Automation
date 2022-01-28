# ReadMe
## Setup
1. Innstall required modules in `requirements.txt` by being in the base directory of this program in a terminal and typing `pip install -r requirements.txt`
   1. Note: Selenium version must remain below `4.0` as of 1/15/2022 as `Helium 3.0.8` a Selenium wrapper does not currently support `version 4.0` or above of `Selenium`
2. Run `test.py` to get the coordinates for the `open` button for the `Windows Explorer` window that pops up when uploading an image from https:backgroundtown.com
   1. Use these values to make the appropriate changes to, it would be better to add this to the config `.toml` file or create and `.ini` file
    ```python
        if self.hostname.lower() == 'aci421': # this computer has the File Explorer window show up at a different location
          pyautogui.moveTo(794, 504)
        elif self.hostname.lower() == 'aci426': # Tad's computer
          pyautogui.moveTo(794, 564)
        else:
          pyautogui.moveTo(495, 480)
    ```
3. Create a `credentials.py` file with the class
   ```python
    class Credentials:
        email = 'email@email.com'
        password = 'password'
   ```
4. To make changes to the default template products and update locators edit `locators.py`, also look at `\config\.toml` to add or remove designer codes
   1. Note: Consolidating these files into one config type would be great, I originally made `locators.py` first and found out about `.toml` files along the way
5. INSTALL FIREFOX or make the appropriate changes to the code to accept other browsers in `driver_setup.py`