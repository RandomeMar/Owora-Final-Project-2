from PyQt6.QtWidgets import *
from gui import *


class Logic(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.rows = 10
        self.cols = 10
        self.board = []

        for row in range(self.rows):
            self.board.append([])

            for col in range(self.cols):
                self.set_button(row, col)




    def set_button(self, row, col):
        self.button = QtWidgets.QPushButton(parent=self.frame_game)
        self.button.setMaximumSize(QtCore.QSize(40, 40))
        self.button.setMinimumSize(QtCore.QSize(40, 40))
        self.button.setObjectName(f"button{row}_{col}")
        self.gridLayout.addWidget(self.button, row, col)
        self.board[row].append(self.button)
        self.button.clicked.connect(lambda: self.button_pressed(self.board[row][col]))




    def button_pressed(self, space):
        if self.radio_flag.isChecked():
            self.flag(space)
        elif self.radio_click.isChecked():
            self.sweep(space)

    def sweep(self, space):
        pass

    def flag(self, space):
        space.setText('F')



