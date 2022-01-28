import PySide6
import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui


# starting virtual environment python -m venv env

class MyWidget(QtWidgets.QWidget):
  def __init__(self):
    super().__init__()

    self.hello = ["Hallo Welt", "Hei maailma", "Hola Mundo", "Привет мир", "안녕하세요 세계", "你好，世界"]

    self.button = QtWidgets.QPushButton("Click me!")
    self.text = QtWidgets.QLabel("Hello World", alignment=QtCore.Qt.AlignCenter)

    self.layout = QtWidgets.QVBoxLayout(self)
    self.layout.addWidget(self.text)
    self.layout.addWidget(self.button)

    self.button.clicked.connect(self.magic)

  @QtCore.Slot() # https://stackoverflow.com/questions/6392739/what-does-the-at-symbol-do-in-python
  def magic(self):
    self.text.setText(random.choice(self.hello))

if __name__ == '__main__':
  app = QtWidgets.QApplication([])

  widget = MyWidget()
  widget.resize(200,200)
  widget.show()

  with open('\\\\work\\tech\\Henry\\Programs\\Python\\bgt-automate\\create_product\\GUI\style.qss', 'r') as f:
    _style = f.read()
    app.setStyleSheet(_style)

  sys.exit(app.exec())