# -*- coding: utf-8 -*-
"""Python 3.6.0
Chemistry Calculator - GUI (2017)
Graphical user interface of ChemCalc
Author: Jingjie YANG (j.yang19 at ejm.org)"""

import sys
import sympy
from PyQt5 import QtGui, QtCore, QtWidgets
from CHEMaths import process_formula, smart_calculate, get_ratio, process_and_balance_equation, Alkane


class GUI(QtWidgets.QWidget):
    def __init__(self):
        """Create an user interface"""
        super().__init__()
        self.status_labels = []
        self.input_buttons = []
        self.input = QtWidgets.QLineEdit()
        self.confirm_input_button = QtWidgets.QPushButton("Enter")
        self.confirm_input_button.clicked.connect(self.confirm_input)
        self.initUI()

    def initUI(self):
        """Initiate user interface"""
        # set title and icon
        self.setWindowTitle("CHEMaths")
        self.resize(800, 512)

        # centering application
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # create widgets
        status_labels_text = [
            ("+", "Information on Molecule"),
            ("->", "Balance Equation"),
            ("g", "Determine Empirical Formula"),
            ("CH", "Alkane")
        ]
        input_buttons_text = [
            '->', '^', '_', '(', ')', ':', ';'
        ]

        # font and tooltip
        QtWidgets.QToolTip.setFont(QtGui.QFont('Serif', 10))

        # grid widgets
        grid = QtWidgets.QGridLayout()

        # add widgets to grid
        grid.addWidget(self.input, 0, 0, 1, 7)
        grid.addWidget(self.confirm_input_button, 0, 7)
        for column_number, input_button_text in enumerate(input_buttons_text):
            input_button = QtWidgets.QPushButton(input_button_text)
            input_button.setStyleSheet("""
                            background-color: LightGrey;
                        """)
            grid.addWidget(input_button, 1, column_number)
            self.input_buttons.append(input_button)
        for row_number, status_label_text in enumerate(status_labels_text):
            status_label = QtWidgets.QLabel(status_label_text[0])
            status_label.setToolTip(status_label_text[1])
            status_label.setStyleSheet("""
                                        background-color: #B43;
                                        color: #ffffff;
                                        padding: 5;
                                        font-family: serif;
                                    """)
            status_label.setWordWrap(True)
            status_label.resize(10, 30)
            status_label.setAlignment(QtCore.Qt.AlignCenter)
            grid.addWidget(status_label, row_number + 2, 0)
            self.status_labels.append(status_label)
        self.status_labels[0].setStyleSheet("""
                                            background-color: #00b540; 
                                            color: #ffffff; 
                                            font-family: serif
                                        """)
        self.setLayout(grid)
        self.show()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Return:
            self.confirm_input()
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()

    def confirm_input(self):
        print(self.input.text())
        self.input.clear()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app_gui = GUI()
    app.setWindowIcon(QtGui.QIcon('icon.png'))
    sys.exit(app.exec_())
