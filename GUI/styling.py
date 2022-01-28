import sys
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget

"""
Interesting: Qtconcurrent::run()

https://doc.qt.io/qtforpython/tutorials/basictutorial/widgetstyling.html
"""

style = '\\\\work\\tech\\Henry\\Programs\\Python\\bgt-automate\\create_product\\GUI\\style.qss'
class Widget(QWidget):
  def __init__(self, parent=None) -> None:
    super(Widget, self).__init__(parent)

    menu_widget = QListWidget()
    for i in range(10):
      item = QListWidgetItem(f'Item {i}')
      item.setTextAlignment(Qt.AlignCenter)
      menu_widget.addItem(item) # add item to the list

    text_widget = QLabel('AMERICAN COLOR IMAGING')
    button = QPushButton('Something')

    content_layout = QVBoxLayout()
    content_layout.addWidget(text_widget)
    content_layout.addWidget(button)
    main_widget = QWidget()
    main_widget.setLayout(content_layout)

    layout = QHBoxLayout()
    layout.addWidget(menu_widget, 1)
    layout.addWidget(main_widget, 4)
    self.setLayout(layout)



if __name__ == '__main__':


  app = QApplication() # initialize
  widget = Widget()
  widget.show()
  widget.resize(800, 600)
  with open(style, 'r') as f:
    _style = f.read()
    app.setStyleSheet(_style)
  # w.show()
  sys.exit(app.exec())
