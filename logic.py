from PyQt6.QtWidgets import *
from gui import *
from random import *
import csv


class Logic(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # these are not the defaults. Defaults are 10, 10, and 13
        self.rows = 1
        self.cols = 1
        self.bombs = 1
        self.flags = 1
        self.board = [[]]
        self.board_nums = []
        self.board_flags = []
        self.set_button(0, 0)
        self.generate_board()
        self.button_gen.clicked.connect(lambda: self.generate_board())
        self.flag_icon = QtGui.QIcon('Flag.png')





    def set_button(self, row, col):
        # This shit creates a button widget at space (row, col) in the grid layout. Also saves button to .board 2d
        # list for future fuckery
        self.button = QtWidgets.QPushButton(parent=self.frame_game)
        self.button.setMaximumSize(QtCore.QSize(40, 40))
        self.button.setMinimumSize(QtCore.QSize(40, 40))
        self.button.setObjectName(f"button{row}_{col}")
        self.button.setIconSize(QtCore.QSize(30, 30))
        self.gridLayout.addWidget(self.button, row, col)
        self.board[row].append(self.button)
        self.button.clicked.connect(lambda: self.button_pressed(self.board[row][col]))


    def button_pressed(self, space):
        # This shit is retarded
        if self.radio_flag.isChecked():
            self.flag(space)
        elif self.radio_click.isChecked():
            self.sweep(space)


    def sweep(self, space):
        """
        Todo: If a space is clicked, and it's not a bomb, disable it with .setEnabled(False) and change its text to the number in board_nums.

        Todo: If it is a bomb, disable all spaces and change the bomb spaces text to an X. I'll find a bomb image later.

        Todo: If a space is flagged, do nothing
        """

        row, col = self.get_button_position(space)

        if self.board_flags[row][col] == 'F':
            return
        
        if self.board_nums[row][col] == 'x':
            self.lose()
        else:
            self.flood_fill(row, col)
            self.check_win()
    
    def get_button_position(self, button):
        pos = self.gridLayout.getItemPosition(self.gridLayout.indexOf(button))
        return pos[0], pos[1]



    def flag(self, space):
        """
        Todo: Make it so you can flag and un-flag a space. For now just change the space text to 'F'. I'll get a flag image later
        """
        row, col = self.get_button_position(space)
        if self.board_flags[row][col] == '' and self.flags > 0:
            space.setIcon(self.flag_icon)
            self.board_flags[row][col] = 'F'
            self.flags -= 1
        elif self.board_flags[row][col] == 'F':
            space.setIcon(QtGui.QIcon())
            self.board_flags[row][col] = ''
            self.flags += 1
        self.lcd_flag.setProperty("intValue", self.flags)



    def generate_board(self):
        # This shit uses temp vars to see if the inputs are ints that are > 1. If they are it clears the board list,
        # destroys all the button widgets in the frame_game frame, and creates a new board with .set_button()
        try:
            temp_r = int(self.input_row.text())
            temp_c = int(self.input_col.text())
            temp_b = int(self.input_bomb.text())
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

            # This shit is bomb creation
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


    def generate_nums(self):
        """
        Todo: This shit should generate the numbers. Make a double for loop to cycle through every space in board_nums.
        Should look like this:          x 0 x
                                        0 # 0 = 3
                                        x 0 0
        If the space in the middle is an x then just continue.
        """
        for row in range(self.rows):
            for col in range(self.cols):
                if self.board_nums[row][col] != 'x':
                    num_bombs = self.count_neighboring_bombs(row, col)
                    self.board_nums[row][col] = num_bombs



    def count_neighboring_bombs(self, row, col):
    #THis shit was toxic bitch
        bomb_count = 0

        for i in range(-1, 2):
            for j in range(-1, 2):
                new_row, new_col = row + i, col + j

                #Checks the neighboring space to see if it's within the board boundaries
                if 0 <= new_row < self.rows and 0 <= new_col < self.cols:
                    if self.board_nums[new_row][new_col] == 'x':
                        bomb_count += 1

        return bomb_count

    def flood_fill(self, row, col):
        try:
            if row < 0 or col < 0:
                raise IndexError
            if not self.board[row][col].isEnabled():
                return
            if self.board_flags[row][col] == 'F':
                return
            num = self.board_nums[row][col]
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

    def check_win(self):
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board_nums[row][col] == 'x':
                    continue
                if self.board[row][col].isEnabled():
                    return
        # Put win condition
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
            csv_r = csv.writer(file)
            csv_r.writerow([f'{self.rows}x{self.cols}', self.bombs, "Win"])


    def lose(self):
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
            csv_r = csv.writer(file)
            csv_r.writerow([f'{self.rows}x{self.cols}', self.bombs, "Loss"])

