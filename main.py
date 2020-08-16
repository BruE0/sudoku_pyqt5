
#!/usr/bin/env python3

"""
    main.py
    2020
"""

import sys
import time
import json
import random

from pathlib import Path
from functools import partial

from PyQt5.QtCore import Qt, QTimer
from PyQt5 import QtGui, QtWidgets
from PyQt5 import uic

from sudoku_board import Board


CHARACTERS = "·123456789"

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("mainwindow.ui", self)

        self.solveButton.clicked.connect(self.solve_sudoku)
        self.clearButton.clicked.connect(partial(self.clear_all, include_static=False))
        self.clearAllButton.clicked.connect(partial(self.clear_all, include_static=True))
        self.checkButton.clicked.connect(self.check_board)
        self.startButton.clicked.connect(self.initialize_board_from_labels)

        self.actionSolve.triggered.connect(self.solve_sudoku)
        self.actionExit.triggered.connect(self.close)
        self.actionEasy.triggered.connect(partial(self.load_data, "easy"))
        self.actionMedium.triggered.connect(partial(self.load_data, "medium"))
        self.actionHard.triggered.connect(partial(self.load_data, "hard"))
        self.actionCSV.triggered.connect(partial(self.load_data, "csv"))
        self.actionHelpControls.triggered.connect(help_controls)
        self.actionAbout.triggered.connect(about)

        self.lcdtimer = QTimer(self)
        self.stop_lcd_timer(reset=True)

        self.button_cells = [[None]*9 for _ in range(9)]
        for btn in self.buttonGroup.buttons():
            index = int(btn.objectName()[10:])
            i, j = divmod(index, 9)
            btn.mousePressEvent = partial(self.slot_click, i, j, btn)
            btn.setText(CHARACTERS[0])
            self.button_cells[i][j] = btn

        self.board = Board([[None]*9 for _ in range(9)])

    def initialize_board_from_labels(self):
        data = [
            [int(btn.text()) if btn.text() in "123456789" else None for btn in row]
            for row in self.button_cells
        ]
        self.board = Board(data)
        self.set_labels_from_board()
        if not self.board.is_solvable():
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("The initial digits in the grid make the sudoku unsolvable!")
            msg.exec_()
        self.start_lcd_timer()

    def check_board(self):
        self.set_labels_from_board(color_wrong=True)
        if self.board.is_solved():
            self.stop_lcd_timer(reset=False)
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Sudoku Check")
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("It is solved!")
            msg.exec_()

    def set_labels_from_board(self, color_wrong = False):
        static_digits = self.board.static_digits_index
        for i, row in enumerate(self.button_cells):
            for j, cell in enumerate(row):
                board_element = self.board[i, j]
                if (i, j) in static_digits:
                    cell.setStyleSheet("color: blue")
                    cell.setText(str(board_element))
                elif (color_wrong and board_element is not None and
                    self.board[i,j] not in self.board.get_digits_available((i, j))):
                    cell.setStyleSheet("color: red")
                else:
                    cell.setStyleSheet("color: none")
                    cell.setText(
                        CHARACTERS[0] if board_element is None else str(board_element)
                    )

    def start_lcd_timer(self):
        start_time = time.time()
        self.lcdtimer.timeout.connect(partial(self.update_lcd_display, start_time))
        self.lcdtimer.start(500)

    def stop_lcd_timer(self, reset=True):
        self.lcdtimer.stop()
        if reset:
            self.lcdNumber.display("88:88:88")

    def update_lcd_display(self, start_time):
        diff = int(time.time() - start_time)
        hh = diff // 3600
        mm, ss = (diff%3600) // 60, diff % 60
        self.lcdNumber.display(f"{hh:02d}:{mm:02d}:{ss:02d}")

    def clear_all(self, include_static = False):
        if not include_static:
            self.board.clear()
        else:
            self.board = Board([[None]*9 for _ in range(9)])
            self.stop_lcd_timer(reset=True)
        self.set_labels_from_board()

    def slot_click(self, i, j, button, mouse_event):
        if self.board.is_available((i,j)):
            mouse_button = mouse_event.button()
            if mouse_button in (Qt.MiddleButton, Qt.LeftButton, Qt.RightButton):
                button.setStyleSheet("color: none")
                char = button.text()
                index = CHARACTERS.find(char)
                if mouse_button == Qt.LeftButton:
                    new_char = CHARACTERS[(index + 1 ) % 10]
                elif mouse_button == Qt.RightButton:
                    new_char = CHARACTERS[(index - 1 ) % 10]
                else:
                    new_char = CHARACTERS[0]

                button.setText(new_char)
                self.board[i, j] = int(new_char) if new_char != CHARACTERS[0] else None

    def solve_sudoku(self):
        board = self.board.is_solvable()
        if board:
            self.board = board
            self.set_labels_from_board()
        else:
            msg = QtWidgets.QMessageBox()
            msg.setWindowTitle("Solve")
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Cannot solve.")
            msg.exec_()

    def load_data(self, type_="csv"):
        if type_ == "csv":
            data = load_csv()
        elif type_ in ("easy", "medium", "hard"):
            data = load_json(difficulty=type_)

        if data:
            self.board = Board(data)
            self.set_labels_from_board()
            self.start_lcd_timer()



def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


def help_controls():
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle("Controls")
    msg.setIcon(QtWidgets.QMessageBox.Information)
    msg.setText("Mouse")
    msg.setInformativeText(("Left click: increase number.\n"
                            "Right click: decrease number.\n"
                            "Middle click: erase number.\n\nThat's it."))
    msg.exec_()


def load_csv():
    options = QtWidgets.QFileDialog.Options()
    options |= QtWidgets.QFileDialog.DontUseNativeDialog
    file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
        None,
        "Load CSV",
        "",
        "CSV files (*.csv);;Text files (*.txt);;All files (*.*)",
        options=options,
    )
    if file_name:
        for delimiter in (",", " ", ";", "|"):
            data = []
            try:
                with open(file_name) as f:
                    for line in f:
                        data.append(
                            [int(d) if d in "123456789" else None 
                            for d in line.split(delimiter)[:9]]
                        )
                if len(data) != 9 or any(len(data[i]) != 9 for i in range(9)):
                    raise ValueError
            except (ValueError, OSError):
                pass
            else:
                return data
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("File Error")
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setText("Could not load file.")
        msg.setInformativeText("File did not have proper format.")
        msg.exec_()


def load_json(difficulty="easy"):
    file = Path() / "grids" / f"{difficulty}.json"
    try:
        with open(file) as f:
            return random.choice(json.load(f))
    except OSError:
        return


def about():
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle("About")
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Sudoku.")
        msg.setInformativeText("python 3.8\nPyQt5 5.15.0")
        msg.exec_()


if __name__ == "__main__":
    main()
