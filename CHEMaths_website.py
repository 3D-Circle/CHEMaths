# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from CHEMaths import smart_calculate, process_and_balance_equation, get_ratio, Alkane
app = Flask(__name__)


def latex2chem(latex):
    """parses latex input for future uses"""
    return latex


@app.route("/")
def home():
    """renders home page of CHEMaths"""
    return render_template('index.html', name="homepage")


@app.route("/", methods=['POST'])
def process():
    """processes input from home page"""
    chem_input = request.form['input']
    # processed_input = latex2chem(chem_input)
    print(chem_input)
    return render_template('index.html', name="result")  # TODO: render new result

if __name__ == "__main__":
    app.run()
