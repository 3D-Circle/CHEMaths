# -*- coding: utf-8 -*-
"""Python 3.6.0
Chemistry Calculator - GUI (2017)
Graphical user interface of ChemCalc
Author: Jingjie YANG (j.yang19 at ejm.org)"""

import sys
import matplotlib as mpl
from matplotlib.backends.backend_agg import FigureCanvasAgg
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget, QLineEdit, QPushButton, QGridLayout, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from ChemCalc import process_formula, smart_calculate, get_ratio, process_and_balance_equation, Alkane


class GUI(QWidget):
    def __init__(self):
        """Create an user interface"""
        super().__init__()
        self.initUI()
        self.status_labels = []
        self.input_buttons = []

    def initUI(self):
        """Initiate user interface"""
        # set title and icon
        self.setWindowTitle("ChemCalc")
        self.resize(800, 512)

        # centering application
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # create widgets
        equation_input = QLineEdit()
        confirm_input = QPushButton("Enter")
        status_molecule_information = QLabel("Information on Molecule")
        status_balance_equation = QLabel("Balance Equation")
        status_empirical_formula = QLabel("Determine Empirical Formula")
        status_alkane = QLabel("Alkane")
        input_caret = QPushButton("^")
        input_underscore = QPushButton("_")
        input_left_parenthesis = QPushButton("(")
        input_right_parenthesis = QPushButton(")")
        input_colon = QPushButton(":")
        input_semicolon = QPushButton(";")
        input_right_arrow = QPushButton("->")  # \rightarrow

        self.status_labels = [
            status_molecule_information,
            status_balance_equation,
            status_empirical_formula,
            status_alkane
        ]
        self.input_buttons = [
            input_right_arrow,
            input_caret,
            input_underscore,
            input_left_parenthesis,
            input_right_parenthesis,
            input_colon,
            input_semicolon
        ]

        # grid widgets
        grid = QGridLayout()

        # add widgets to grid
        grid.addWidget(equation_input, 0, 0, 1, 7)
        grid.addWidget(confirm_input, 0, 7)
        for column_number, input_button in enumerate(self.input_buttons):
            input_button.setStyleSheet("""
                            background-color: LightGrey;
                        """)
            grid.addWidget(input_button, 1, column_number)
        for row_number, status_label in enumerate(self.status_labels):
            status_label.setStyleSheet("""
                                        background-color: #B43;
                                        color: #ffffff;
                                        padding: 5;
                                        font-family: serif;
                                    """)
            status_label.setWordWrap(True)
            status_label.resize(10, 30)
            status_label.setAlignment(Qt.AlignCenter)
            grid.addWidget(status_label, row_number + 2, 0)
        self.status_labels[0].setStyleSheet("""
                                            background-color: #00b540; 
                                            color: #ffffff; 
                                            font-family: serif
                                        """)
        self.setLayout(grid)

        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app_gui = GUI()
    app.setWindowIcon(QIcon('icon.png'))
    sys.exit(app.exec_())
