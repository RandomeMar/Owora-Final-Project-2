from PyQt6.QtWidgets import *
from gui import *
from random import *
import csv


class Logic(QMainWindow, Ui_MainWindow):
    """
    Method to set up window, 2d-lists, variables, and button functionality
    :return: None
    """

    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)

        self.rows: int = 1
        self.cols: int = 1
        self.bombs: int = 1
        self.flags: int = 1
        self.board: list = [[]]
        self.board_nums: list = []
        self.board_flags: list = []
        self.set_button(0, 0)

        self.generate_board()
        self.button_gen.clicked.connect(lambda: self.generate_board())
        self.flag_icon: QtGui.QIcon = QtGui.QIcon('Flag.png')

    def set_button(self, row: int, col: int) -> None:
        """
        Method for creating a push button in a specific row and column in the grid layout
        :param row: row that the button will be created in
        :param col: column that the button will be created in
        :return: None
        """
        self.button: QtWidgets.QPushButton = QtWidgets.QPushButton(parent=self.frame_game)
        self.button.setMaximumSize(QtCore.QSize(40, 40))
        self.button.setMinimumSize(QtCore.QSize(40, 40))
        self.button.setObjectName(f"button{row}_{col}")
        self.button.setIconSize(QtCore.QSize(30, 30))
        self.gridLayout.addWidget(self.button, row, col)
        self.board[row].append(self.button)
        self.button.clicked.connect(lambda: self.button_pressed(self.board[row][col]))

    def button_pressed(self, space: QtWidgets.QPushButton) -> None:
        """
        Method for deciding which method to call when a space is clicked on the board
        :param space: space on the board being manipulated
        :return: None
        """
        if self.radio_flag.isChecked():
            self.flag(space)
        elif self.radio_click.isChecked():
            self.sweep(space)

    def sweep(self, space: QtWidgets.QPushButton) -> None:
        """
        Method for when a space is clicked
        :param space: space on the board being manipulated
        :return: None
        """

        row, col = self.get_button_position(space)
        row: int
        col: int

        if self.board_flags[row][col] == 'F':
            return

        if self.board_nums[row][col] == 'x':
            self.lose()
        else:
            self.flood_fill(row, col)
            self.check_win()

    def get_button_position(self, button: QtWidgets.QPushButton) -> tuple[int, int]:
        """
        Method for returning the row and column of a button on the grid layout
        :param button: Button whose coordinates will be gathered
        :return: a tuple containing the row and column values
        """
        pos: list = self.gridLayout.getItemPosition(self.gridLayout.indexOf(button))
        return pos[0], pos[1]

    def flag(self, space: QtWidgets.QPushButton) -> None:
        """
        Method for when a space is flagged
        :param space: space on the board being manipulated
        :return: None
        """
        row, col = self.get_button_position(space)
        row: int
        col: int
        if self.board_flags[row][col] == '' and self.flags > 0:
            space.setIcon(self.flag_icon)
            self.board_flags[row][col] = 'F'
            self.flags -= 1
        elif self.board_flags[row][col] == 'F':
            space.setIcon(QtGui.QIcon())
            self.board_flags[row][col] = ''
            self.flags += 1
        self.lcd_flag.setProperty("intValue", self.flags)

    def generate_board(self) -> None:
        """
        Method for generating the game board and deleting an old game board
        :return: None
        """
        try:
            temp_r: int = int(self.input_row.text())
            temp_c: int = int(self.input_col.text())
            temp_b: int = int(self.input_bomb.text())
            if temp_r < 1 or temp_c < 1 or temp_b < 1 or temp_b > temp_r * temp_c:
                raise TypeError

            for row in range(self.rows):

                for col in range(self.cols):
                    self.board[row][col].setParent(None)
            self.board.clear()
            self.board_nums.clear()
            self.board_flags.clear()

            self.rows = temp_r
            self.cols = temp_c
            self.bombs = temp_b
            self.flags = temp_b

            for row in range(self.rows):
                self.board.append([])
                self.board_nums.append([])
                self.board_flags.append([])

                for col in range(self.cols):
                    self.set_button(row, col)
                    self.board_nums[row].append(0)
                    self.board_flags[row].append('')

            for i in range(self.bombs):
                rand_row = randint(0, self.rows - 1)
                rand_col = randint(0, self.cols - 1)
                while self.board_nums[rand_row][rand_col] == 'x':
                    rand_row = randint(0, self.rows - 1)
                    rand_col = randint(0, self.cols - 1)

                self.board_nums[rand_row][rand_col] = 'x'

            self.lcd_flag.setProperty("intValue", self.flags)
            self.label_face.setPixmap(QtGui.QPixmap("Slightly Smiling Face Emoji.png"))
            self.label_main.setText("Input rows, columns, and bombs to generate a new game")
            self.generate_nums()

        except ValueError:
            self.label_main.setText('Please input only integers')

        except TypeError:
            self.label_main.setText('Make sure all values are positive and that there are more spaces than bombs')

    def generate_nums(self) -> None:
        """
        Method for assigning number of bombs nearby for all spaces on the board
        :return: None
        """
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board_nums[row][col] != 'x':
                    num_bombs: int = self.count_neighboring_bombs(row, col)
                    self.board_nums[row][col] = num_bombs

    def count_neighboring_bombs(self, row, col) -> int:
        """
        Method for evaluating how many bombs are nearby
        :param row: row of space being evaluated
        :param col: column of space being evaluated
        :return: int measuring amount of bombs nearby
        """
        bomb_count: int = 0

        for i in range(-1, 2):
            for j in range(-1, 2):
                new_row, new_col = row + i, col + j
                if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                    if self.board_nums[new_row][new_col] == 'x':
                        bomb_count += 1

        return bomb_count

    def flood_fill(self, row, col) -> None:
        """
        Recursive method for filling in spaces with bomb count of zero
        :param row: row of central space for floodfill
        :param col: column of central space for floodfill
        :return: None
        """
        try:
            if row < 0 or col < 0:
                raise IndexError
            if not self.board[row][col].isEnabled():
                return
            if self.board_flags[row][col] == 'F':
                return
            num: int = self.board_nums[row][col]
            self.board[row][col].setEnabled(False)
            if num > 0:
                self.board[row][col].setText(str(num))
                return
            elif num == 0:
                self.flood_fill(row + 1, col - 1)
                self.flood_fill(row + 1, col)
                self.flood_fill(row + 1, col + 1)
                self.flood_fill(row, col - 1)
                self.flood_fill(row, col + 1)
                self.flood_fill(row - 1, col - 1)
                self.flood_fill(row - 1, col)
                self.flood_fill(row - 1, col + 1)
        except IndexError:
            return

    def check_win(self) -> None:
        """
        Method for checking if the player has won
        :return: None
        """
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board_nums[row][col] == 'x':
                    continue
                if self.board[row][col].isEnabled():
                    return
        for row in self.board:
            for button in row:
                button.setEnabled(False)
                button.setText('')
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board_nums[row][col] == 'x':
                    self.board[row][col].setIcon(QtGui.QIcon('Slightly Smiling Face Emoji.png'))
        self.label_main.setText("You win! Press generate to play again")
        with open("win_record.csv", 'a', newline='') as file:
            csv_w: csv.writer = csv.writer(file)
            csv_w.writerow([f'{self.rows}x{self.cols}', self.bombs, "Win"])

    def lose(self) -> None:
        """
        Method for displaying the loss state of the game
        :return: None
        """
        for row in self.board:
            for button in row:
                button.setEnabled(False)
                button.setText('')
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board_nums[row][col] == 'x':
                    self.board[row][col].setIcon(QtGui.QIcon('Dizzy Face Emoji.png'))
        self.label_face.setPixmap(QtGui.QPixmap("Dizzy Face Emoji.png"))
        self.label_main.setText("You lose! Press generate to play again")
        with open("win_record.csv", 'a', newline='') as file:
            csv_w: csv.writer = csv.writer(file)
            csv_w.writerow([f'{self.rows}x{self.cols}', self.bombs, "Loss"])
