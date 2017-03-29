# -*- coding: utf-8 -*-
"""Python 3.6.0
Chemistry Calculator - GUI (2017)
Graphical user interface of CHEMaths
Author: Jingjie YANG (j.yang19 at ejm.org)"""

# TODO implement MathInput
# TODO add shortcuts
# TODO add collapse widgets

import sys
import os
from PyQt5 import QtGui, QtCore, QtWidgets, QtWebEngineWidgets


class ChemKeyboard(QtWebEngineWidgets.QWebEngineView):
    def __init__(self):
        super().__init__()

        self.load(QtCore.QUrl("file:///Users/yangjingjie/PycharmProjects/CHEMaths/src/ChemInput.html"))


class GUI(QtWidgets.QWidget):
    def __init__(self):
        """Create an user interface"""
        super().__init__()
        self.status_labels = []
        self.input_buttons = []
        self.input_equation = ChemKeyboard()

        self.init_ui()

    def init_ui(self):
        """Initiate user interface"""
        # set title and icon
        self.setWindowTitle("CHEMaths")
        self.resize(800, 512)

        # centering application
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # font and tooltip
        QtWidgets.QToolTip.setFont(QtGui.QFont('Serif', 10))

        # grid widgets
        grid = QtWidgets.QGridLayout()

        # create widgets
        status_labels_text = [
            ("+", "Information on Molecule"),
            ("->", "Balance Equation"),
            ("g", "Determine Empirical Formula"),
            ("CH", "Alkane")
        ]
        input_buttons_text = [
            '->', '^', '_', '(', ')', '+', ':', ';'
        ]

        # add widgets to grid
        grid.addWidget(self.input_equation, 0, 0, 1, 8)
        self.input_equation.setMaximumSize(2500, 100)
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
            status_label.setWordWrap(True)
            status_label.resize(10, 30)
            status_label.setAlignment(QtCore.Qt.AlignCenter)
            grid.addWidget(status_label, row_number + 2, 0)
            self.status_labels.append(status_label)

        # connect buttons to functions

        self.update()
        self.setLayout(grid)
        self.show()

    def update_mode(self, mode):
        for index, status_label in enumerate(self.status_labels):
            if index == mode:
                style_sheet = """
                    background-color: #B43;
                    color: #ffffff;
                    padding: 5;
                    font-family: serif;
                    """
            else:
                style_sheet = """
                    background-color: #00b540; 
                    color: #ffffff; 
                    font-family: serif
                    """
            status_label.setStyleSheet(style_sheet)

    def update(self):
        # TODO: get text from input
        text = ''
        # Detect mode
        if "->" in text:
            mode = 1
        elif "alkane" in text.lower():
            mode = 3
        elif ":" in text:
            mode = 2
        else:
            mode = 0

        self.update_mode(mode)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app_gui = GUI()
    app.setWindowIcon(QtGui.QIcon('src/icon.png'))
    sys.exit(app.exec_())
