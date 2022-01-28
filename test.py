"""
Description: Script to return out the current coordinate of the mouse pointer, this used to find the Windows Explorer `open` and `cancel` buttons in order for 
            pyautogui to actaully close the window by clicking. The location changes based on the computer, so go to a product on backgrountown and try to click
            upload and see where the window appears. Try this on the `product variation -> attribute combination` page as well 
"""

import pyautogui, sys
print('Press Ctrl-C to quit.')
try:
    while True:
        x, y = pyautogui.position()
        positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
        # positionStr = f'X: {x} Y: {y}'
        print(positionStr, end='')
        print('\b' * len(positionStr), end='', flush=True)
except KeyboardInterrupt:
    print('\n')
    